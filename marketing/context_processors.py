from django.conf import settings

from .models import whatsapp_url
from .stats import get_site_stats


def site(request):
    """Datos de marca, contacto y contador disponibles en todas las plantillas."""
    stats = get_site_stats()
    return {
        "site_brand": settings.SITE_BRAND,
        "site_tagline": settings.SITE_TAGLINE,
        "whatsapp_number_display": settings.WHATSAPP_NUMBER_DISPLAY,
        "whatsapp_general_url": whatsapp_url(settings.WHATSAPP_GENERAL_MESSAGE),
        "site_views_total": stats["total"],
        "site_visitors_total": stats["visitors"],
        "panel_image_url": f"{settings.MEDIA_URL}{settings.PANEL_IMAGE}",
    }
