"""
ฟังก์ชันช่วยสำหรับการจัดการข้อมูลผู้ใช้
User helper functions for better Thai name display and profile management
"""

def get_user_display_name(user):
    """
    Get user display name with better Thai name support
    
    Args:
        user: User object from database
    
    Returns:
        str: Display name for the user
    """
    if not user:
        return "ไม่ระบุชื่อ"
    
    # Priority: full name > first name > username > email prefix
    if user.first_name and user.last_name:
        # Full name available
        full_name = f"{user.first_name.strip()} {user.last_name.strip()}"
        return full_name.strip()
    elif user.first_name:
        # Only first name available
        return user.first_name.strip()
    elif user.username and user.username != user.email:
        # Use username if it's not same as email
        return user.username
    elif user.email:
        # Fallback to email prefix
        return user.email.split("@")[0]
    else:
        return "ไม่ระบุชื่อ"

def get_user_short_name(user):
    """
    Get user short name for compact display
    
    Args:
        user: User object from database
    
    Returns:
        str: Short display name
    """
    if not user:
        return "?"
    
    if user.first_name:
        return user.first_name.strip()
    elif user.username and user.username != user.email:
        return user.username
    elif user.email:
        return user.email.split("@")[0]
    else:
        return "?"

def get_user_initials(user):
    """
    Get user initials for avatar display
    
    Args:
        user: User object from database
    
    Returns:
        str: User initials (1-2 characters)
    """
    if not user:
        return "?"
    
    if user.first_name and user.last_name:
        # Get first character of each name
        first_char = user.first_name.strip()[0].upper() if user.first_name.strip() else ""
        last_char = user.last_name.strip()[0].upper() if user.last_name.strip() else ""
        return f"{first_char}{last_char}"
    elif user.first_name:
        # Get first 1-2 characters of first name
        name = user.first_name.strip()
        if len(name) >= 2:
            return name[:2].upper()
        else:
            return name[0].upper() if name else "?"
    elif user.username and user.username != user.email:
        # Get first 1-2 characters of username
        name = user.username.strip()
        if len(name) >= 2:
            return name[:2].upper()
        else:
            return name[0].upper() if name else "?"
    elif user.email:
        # Get first character of email
        return user.email[0].upper()
    else:
        return "?"

def is_thai_name(name):
    """
    Check if a name contains Thai characters
    
    Args:
        name: Name string to check
    
    Returns:
        bool: True if contains Thai characters
    """
    if not name:
        return False
    
    # Thai Unicode range: \u0E00-\u0E7F
    thai_pattern = r'[\u0E00-\u0E7F]'
    import re
    return bool(re.search(thai_pattern, name))

def format_user_profile_data(user):
    """
    Format user data for profile display
    
    Args:
        user: User object from database
    
    Returns:
        dict: Formatted user data
    """
    if not user:
        return {
            'id': None,
            'display_name': 'ไม่ระบุชื่อ',
            'short_name': '?',
            'initials': '?',
            'email': '',
            'username': '',
            'profile_image': None,
            'is_thai_name': False,
            'full_name': '',
            'auth_type': 'unknown'
        }
    
    display_name = get_user_display_name(user)
    short_name = get_user_short_name(user)
    initials = get_user_initials(user)
    
    # Check if it's Thai name
    is_thai = is_thai_name(user.first_name) or is_thai_name(user.last_name) or is_thai_name(user.username)
    
    # Full name
    full_name = ""
    if user.first_name and user.last_name:
        full_name = f"{user.first_name} {user.last_name}"
    elif user.first_name:
        full_name = user.first_name
    
    # Auth type
    auth_type = 'google' if user.password_hash == 'oauth_google' else 'regular'
    
    return {
        'id': user.id,
        'display_name': display_name,
        'short_name': short_name,
        'initials': initials,
        'email': user.email or '',
        'username': user.username or '',
        'profile_image': user.profile_image,
        'is_thai_name': is_thai,
        'full_name': full_name,
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'bio': user.bio or '',
        'auth_type': auth_type,
        'email_verified': user.email_verified if hasattr(user, 'email_verified') else False,
        'role': user.role if hasattr(user, 'role') else 'student',
        'created_at': user.created_at if hasattr(user, 'created_at') else None,
        'last_login': user.last_login if hasattr(user, 'last_login') else None
    }