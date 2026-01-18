from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import LoginLog


def get_client_ip(request):
    """Extract the client IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def parse_user_agent(user_agent_string):
    """
    Parse user agent string to extract OS, browser, and device information.
    Uses user_agents library if available, otherwise falls back to basic parsing.
    """
    try:
        from user_agents import parse
        user_agent = parse(user_agent_string)
        
        # Get OS information
        os_info = user_agent.os.family
        if user_agent.os.version_string:
            os_info = f"{os_info} {user_agent.os.version_string}"
        
        # Get browser information
        browser = user_agent.browser.family
        browser_version = user_agent.browser.version_string
        
        # Get device information
        if user_agent.is_mobile:
            device = f"Mobile - {user_agent.device.family}"
        elif user_agent.is_tablet:
            device = f"Tablet - {user_agent.device.family}"
        elif user_agent.is_pc:
            device = "Desktop/PC"
        else:
            device = user_agent.device.family or "Unknown"
        
        return {
            'operating_system': os_info,
            'browser': browser,
            'browser_version': browser_version,
            'device': device,
        }
    except ImportError:
        # Fallback: basic user agent parsing without the library
        return parse_user_agent_basic(user_agent_string)


def parse_user_agent_basic(user_agent_string):
    """Basic user agent parsing without external libraries."""
    ua = user_agent_string.lower()
    
    # Detect OS
    if 'windows nt 10' in ua:
        os_info = 'Windows 10/11'
    elif 'windows nt 6.3' in ua:
        os_info = 'Windows 8.1'
    elif 'windows nt 6.2' in ua:
        os_info = 'Windows 8'
    elif 'windows nt 6.1' in ua:
        os_info = 'Windows 7'
    elif 'windows' in ua:
        os_info = 'Windows'
    elif 'mac os x' in ua:
        os_info = 'macOS'
    elif 'android' in ua:
        os_info = 'Android'
    elif 'iphone' in ua or 'ipad' in ua:
        os_info = 'iOS'
    elif 'linux' in ua:
        os_info = 'Linux'
    else:
        os_info = 'Unknown OS'
    
    # Detect Browser
    if 'edg/' in ua:
        browser = 'Microsoft Edge'
    elif 'chrome/' in ua and 'safari/' in ua:
        browser = 'Chrome'
    elif 'firefox/' in ua:
        browser = 'Firefox'
    elif 'safari/' in ua and 'chrome/' not in ua:
        browser = 'Safari'
    elif 'opera' in ua or 'opr/' in ua:
        browser = 'Opera'
    else:
        browser = 'Unknown Browser'
    
    # Detect Device
    if 'mobile' in ua or 'android' in ua and 'mobile' in ua:
        device = 'Mobile'
    elif 'tablet' in ua or 'ipad' in ua:
        device = 'Tablet'
    else:
        device = 'Desktop/PC'
    
    return {
        'operating_system': os_info,
        'browser': browser,
        'browser_version': '',
        'device': device,
    }


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Signal handler to log user login information."""
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    ip_address = get_client_ip(request)
    
    # Parse user agent
    ua_info = parse_user_agent(user_agent_string)
    
    # Create login log entry
    LoginLog.objects.create(
        user=user,
        ip_address=ip_address,
        operating_system=ua_info['operating_system'],
        browser=ua_info['browser'],
        browser_version=ua_info['browser_version'],
        device=ua_info['device'],
        user_agent=user_agent_string,
    )
