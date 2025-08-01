
def get_device_name_from_request(request) -> str:
    ua = request.user_agent  # provided by django-user-agents middleware
    dtype = "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "Desktop" if ua.is_pc else "Unknown"
    os_part = f"{ua.os.family} {ua.os.version}".strip()
    br_part = f"{ua.browser.family} {ua.browser.version}".strip()
    dev_part = " ".join(p for p in [ua.device.brand, ua.device.model] if p).strip()
    parts = [p for p in [dev_part or None, os_part or None, br_part or None] if p]
    return " | ".join(parts) if parts else dtype
