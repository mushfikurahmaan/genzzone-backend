"""
Meta Conversions API service.
Sends server-side events to Facebook's Conversions API.
"""
import hashlib
import logging
import re
import time
from typing import Any, Optional

import requests
from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger(__name__)

# Bangladesh country code for phone normalization
BANGLADESH_COUNTRY_CODE = "880"


def _normalize_email(email: str) -> Optional[str]:
    """Trim and lowercase email. Returns None if empty."""
    if not email or not isinstance(email, str):
        return None
    normalized = email.strip().lower()
    return normalized if normalized else None


def _normalize_phone_bangladesh(phone: str) -> Optional[str]:
    """
    Normalize Bangladesh phone: strip non-digits, remove leading zero, add 880.
    Input e.g. 01XXXXXXXXX -> 8801XXXXXXXXX
    """
    if not phone or not isinstance(phone, str):
        return None
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None
    # Remove leading zero if 11 digits (Bangladesh local format)
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) != 10:
        return None
    return BANGLADESH_COUNTRY_CODE + digits


def _normalize_first_name(name: str) -> Optional[str]:
    """Lowercase, no punctuation. Uses first token as first name. Supports Unicode."""
    if not name or not isinstance(name, str):
        return None
    parts = name.strip().split()
    if not parts:
        return None
    # Keep word characters (letters, numbers) per Meta UTF-8 guidance
    first = re.sub(r"[^\w]", "", parts[0].lower(), flags=re.UNICODE)
    return first if first else None


def _sha256(value: str) -> str:
    """SHA-256 hash as hex string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _get_client_ip(request: HttpRequest) -> Optional[str]:
    """Get client IP from X-Forwarded-For or REMOTE_ADDR."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # First IP is the client when behind a proxy
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _get_client_user_agent(request: HttpRequest) -> Optional[str]:
    """Get User-Agent header."""
    return request.META.get("HTTP_USER_AGENT")


def _build_user_data(
    request: HttpRequest,
    *,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    first_name: Optional[str] = None,
) -> dict[str, Any]:
    """Build user_data for Conversions API. Hashes PII per Meta's spec."""
    user_data: dict[str, Any] = {}

    if email:
        norm = _normalize_email(email)
        if norm:
            user_data["em"] = [_sha256(norm)]

    if phone:
        norm = _normalize_phone_bangladesh(phone)
        if norm:
            user_data["ph"] = [_sha256(norm)]

    if first_name:
        norm = _normalize_first_name(first_name)
        if norm:
            user_data["fn"] = [_sha256(norm)]

    # Non-hashed params (do not hash per Meta docs)
    client_ip = _get_client_ip(request)
    if client_ip:
        user_data["client_ip_address"] = client_ip

    client_ua = _get_client_user_agent(request)
    if client_ua:
        user_data["client_user_agent"] = client_ua

    return user_data


def _is_configured() -> bool:
    """Check if Conversions API is configured."""
    token = getattr(settings, "META_CONVERSIONS_ACCESS_TOKEN", None)
    pixel_id = getattr(settings, "META_CONVERSIONS_PIXEL_ID", None)
    return bool(token and pixel_id)


def send_purchase_event(
    request: HttpRequest,
    *,
    order_id: int,
    value: float,
    currency: str,
    customer_name: str,
    customer_phone: str = "",
    customer_email: str = "",
    content_ids: Optional[list[str]] = None,
    num_items: Optional[int] = None,
    event_source_url: Optional[str] = None,
) -> bool:
    """
    Send Purchase event to Meta Conversions API.
    Returns True if sent successfully, False otherwise.
    Does not block or raise; logs errors.
    """
    if not _is_configured():
        logger.debug("Meta Conversions API not configured (missing token/pixel), skipping Purchase")
        return False

    event_time = int(time.time())
    user_data = _build_user_data(
        request,
        email=customer_email or None,
        phone=customer_phone or None,
        first_name=customer_name or None,
    )

    if not user_data:
        logger.warning("Meta Conversions: Purchase event has no user_data (IP/UA required)")
        # Still try to send with minimal data; Meta may reject
        user_data = {}
        client_ip = _get_client_ip(request)
        if client_ip:
            user_data["client_ip_address"] = client_ip
        client_ua = _get_client_user_agent(request)
        if client_ua:
            user_data["client_user_agent"] = client_ua

    custom_data: dict[str, Any] = {
        "currency": currency,
        "value": round(float(value), 2),
        "order_id": str(order_id),
    }
    if content_ids:
        custom_data["content_ids"] = [str(x) for x in content_ids]
    if num_items is not None:
        custom_data["num_items"] = num_items
    custom_data.setdefault("content_type", "product")

    event: dict[str, Any] = {
        "event_name": "Purchase",
        "event_time": event_time,
        "action_source": "website",
        "user_data": user_data,
        "custom_data": custom_data,
    }

    # Required for website events - uniquely identifies where purchase occurred
    url = event_source_url or request.META.get("HTTP_REFERER") or request.META.get("HTTP_ORIGIN")
    if url:
        event["event_source_url"] = url

    test_code = getattr(settings, "META_CONVERSIONS_TEST_EVENT_CODE", None)
    if test_code and str(test_code).strip():
        event["test_event_code"] = str(test_code).strip()

    return _send_events([event])


def send_add_to_cart_event(
    request: HttpRequest,
    *,
    product_id: int,
    event_source_url: Optional[str] = None,
) -> bool:
    """
    Send AddToCart event to Meta Conversions API.
    Returns True if sent successfully, False otherwise.
    """
    if not _is_configured():
        logger.debug("Meta Conversions API not configured, skipping AddToCart")
        return False

    event_time = int(time.time())
    user_data = _build_user_data(request)

    if not user_data:
        user_data = {}
        client_ip = _get_client_ip(request)
        if client_ip:
            user_data["client_ip_address"] = client_ip
        client_ua = _get_client_user_agent(request)
        if client_ua:
            user_data["client_user_agent"] = client_ua

    custom_data: dict[str, Any] = {
        "content_type": "product",
        "content_ids": [str(product_id)],
    }

    event: dict[str, Any] = {
        "event_name": "AddToCart",
        "event_time": event_time,
        "action_source": "website",
        "user_data": user_data,
        "custom_data": custom_data,
    }

    if event_source_url:
        event["event_source_url"] = event_source_url

    test_code = getattr(settings, "META_CONVERSIONS_TEST_EVENT_CODE", None)
    if test_code and str(test_code).strip():
        event["test_event_code"] = str(test_code).strip()

    return _send_events([event])


def _send_events(events: list[dict[str, Any]]) -> bool:
    """POST events to Meta Conversions API. Returns True on success."""
    token = settings.META_CONVERSIONS_ACCESS_TOKEN
    pixel_id = settings.META_CONVERSIONS_PIXEL_ID
    api_version = getattr(settings, "META_CONVERSIONS_API_VERSION", "v21.0")

    url = f"https://graph.facebook.com/{api_version}/{pixel_id}/events"
    params = {"access_token": token}
    payload = {"data": events}

    try:
        resp = requests.post(url, params=params, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("events_received"):
                logger.debug("Meta Conversions API: events received", extra={"events": len(events)})
                return True
            if "error" in data:
                logger.warning("Meta Conversions API error: %s", data["error"])
                return False
            return True
        logger.warning(
            "Meta Conversions API HTTP %s: %s",
            resp.status_code,
            resp.text[:500],
        )
        return False
    except requests.RequestException as e:
        logger.warning("Meta Conversions API request failed: %s", e)
        return False
