"""
Steadfast Courier API Integration Service
"""
import requests
from django.conf import settings
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to 11 digits format required by Steadfast.
    Handles formats like: +8801712345678, 8801712345678, 01712345678, etc.
    """
    if not phone:
        return phone
    
    # Remove all non-digit characters
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # Remove country code if present (880 is Bangladesh country code)
    if digits_only.startswith('880') and len(digits_only) == 13:
        digits_only = digits_only[3:]
    
    # Ensure it's 11 digits (should start with 0)
    if len(digits_only) == 10 and not digits_only.startswith('0'):
        digits_only = '0' + digits_only
    
    return digits_only


class SteadfastService:
    """Service class for interacting with Steadfast Courier API"""
    
    BASE_URL = "https://portal.packzy.com/api/v1"
    
    def __init__(self):
        self.api_key = getattr(settings, 'STEADFAST_API_KEY', None)
        self.secret_key = getattr(settings, 'STEADFAST_SECRET_KEY', None)
        
        if not self.api_key or not self.secret_key:
            logger.warning("Steadfast API keys not configured. Integration will be disabled.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Api-Key': self.api_key,
            'Secret-Key': self.secret_key,
            'Content-Type': 'application/json'
        }
    
    def _is_enabled(self) -> bool:
        """Check if Steadfast integration is enabled"""
        return bool(self.api_key and self.secret_key)
    
    def create_order(
        self,
        invoice: str,
        recipient_name: str,
        recipient_phone: str,
        recipient_address: str,
        cod_amount: float,
        alternative_phone: Optional[str] = None,
        recipient_email: Optional[str] = None,
        note: Optional[str] = None,
        item_description: Optional[str] = None,
        total_lot: Optional[int] = None,
        delivery_type: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a single order in Steadfast
        
        Args:
            invoice: Unique invoice ID (alphanumeric with hyphens/underscores)
            recipient_name: Recipient name (max 100 chars)
            recipient_phone: 11-digit phone number
            recipient_address: Full address (max 250 chars)
            cod_amount: Cash on delivery amount in BDT
            alternative_phone: Optional 11-digit alternative phone
            recipient_email: Optional email
            note: Optional delivery instructions
            item_description: Optional item description
            total_lot: Optional total lot count
            delivery_type: 0 for home delivery, 1 for Point Delivery/Hub Pick Up
        
        Returns:
            Dict containing response from Steadfast API
        """
        if not self._is_enabled():
            logger.warning("Steadfast integration disabled. Skipping order creation.")
            return {
                'status': 'disabled',
                'message': 'Steadfast integration is not configured'
            }
        
        # Normalize and validate phone number (must be 11 digits)
        recipient_phone = normalize_phone_number(recipient_phone.strip())
        if not recipient_phone or not recipient_phone.isdigit() or len(recipient_phone) != 11:
            logger.error(f"Invalid phone number format: {recipient_phone}")
            return {
                'status': 'error',
                'message': 'Phone number must be 11 digits'
            }
        
        # Prepare payload
        payload = {
            'invoice': invoice,
            'recipient_name': recipient_name[:100],  # Ensure max 100 chars
            'recipient_phone': recipient_phone,
            'recipient_address': recipient_address[:250],  # Ensure max 250 chars
            'cod_amount': float(cod_amount)
        }
        
        # Add optional fields
        if alternative_phone:
            alt_phone = normalize_phone_number(alternative_phone.strip())
            if alt_phone and alt_phone.isdigit() and len(alt_phone) == 11:
                payload['alternative_phone'] = alt_phone
        
        if recipient_email:
            payload['recipient_email'] = recipient_email
        
        if note:
            payload['note'] = note
        
        if item_description:
            payload['item_description'] = item_description
        
        if total_lot is not None:
            payload['total_lot'] = total_lot
        
        if delivery_type is not None:
            payload['delivery_type'] = delivery_type
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/create_order",
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Steadfast order created successfully. Invoice: {invoice}, Consignment ID: {result.get('consignment', {}).get('consignment_id')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Steadfast order: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to create order in Steadfast: {str(e)}'
            }
    
    def get_delivery_status_by_consignment_id(self, consignment_id: int) -> Dict[str, Any]:
        """Get delivery status by consignment ID"""
        if not self._is_enabled():
            return {'status': 'disabled', 'message': 'Steadfast integration is not configured'}
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/status_by_cid/{consignment_id}",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting delivery status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_delivery_status_by_invoice(self, invoice: str) -> Dict[str, Any]:
        """Get delivery status by invoice ID"""
        if not self._is_enabled():
            return {'status': 'disabled', 'message': 'Steadfast integration is not configured'}
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/status_by_invoice/{invoice}",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting delivery status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_delivery_status_by_tracking_code(self, tracking_code: str) -> Dict[str, Any]:
        """Get delivery status by tracking code"""
        if not self._is_enabled():
            return {'status': 'disabled', 'message': 'Steadfast integration is not configured'}
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/status_by_trackingcode/{tracking_code}",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting delivery status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_balance(self) -> Dict[str, Any]:
        """Get current balance from Steadfast"""
        if not self._is_enabled():
            return {'status': 'disabled', 'message': 'Steadfast integration is not configured'}
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/get_balance",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting balance: {str(e)}")
            return {'status': 'error', 'message': str(e)}

