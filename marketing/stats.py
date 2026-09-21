import hashlib

from django.core.cache import cache
from django.db.models import Count

from .models import PageView

CACHE_KEY = "marketing:site_stats"
CACHE_SECONDS = 60


def build_visitor_key(request):
    """Identificador estable y anonimo del visitante.

    Se prefiere la sesion. Si el navegador no acepta cookies se cae a un hash
    de IP + user agent, para no inflar el conteo de visitantes unicos.
    """
    session_key = getattr(request.session, "session_key", None)
    if session_key:
        raw = f"session:{session_key}"
    else:
        ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
        ip = ip or request.META.get("REMOTE_ADDR", "")
        raw = f"anon:{ip}:{request.META.get('HTTP_USER_AGENT', '')}"
    return hashlib.sha256(raw.encode("utf-8", "ignore")).hexdigest()


def get_site_stats():
    """Total de visitas y de visitantes unicos, cacheado 60 s.

    Sin cache esto seria un COUNT en cada request de cada pagina.
    """
    stats = cache.get(CACHE_KEY)
    if stats is None:
        aggregate = PageView.objects.aggregate(
            total=Count("id"), visitors=Count("visitor_key", distinct=True)
        )
        stats = {
            "total": aggregate["total"] or 0,
            "visitors": aggregate["visitors"] or 0,
        }
        cache.set(CACHE_KEY, stats, CACHE_SECONDS)
    return stats
