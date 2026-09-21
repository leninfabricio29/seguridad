from django.conf import settings

from .models import PageView
from .stats import build_visitor_key

IGNORED_PREFIXES = ("/admin/", "/static/", "/media/", "/api/", "/favicon")


class PageViewMiddleware:
    """Registra una visita por cada pagina publica servida.

    Solo cuenta GET que devuelven 200 y que piden HTML, para no registrar
    descargas del APK, imagenes ni llamadas de la app movil.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if self._should_track(request, response):
                self._track(request)
        except Exception:
            # El contador nunca debe tumbar una pagina.
            pass
        return response

    def _should_track(self, request, response):
        if not getattr(settings, "PAGEVIEW_TRACKING_ENABLED", True):
            return False
        if request.method != "GET" or response.status_code != 200:
            return False
        if request.path.startswith(IGNORED_PREFIXES):
            return False
        if "text/html" not in response.get("Content-Type", ""):
            return False
        return True

    def _track(self, request):
        # Forzar la sesion da un identificador estable entre paginas.
        if hasattr(request, "session") and not request.session.session_key:
            request.session.save()
        PageView.objects.create(
            path=request.path[:255],
            visitor_key=build_visitor_key(request),
            referer=request.META.get("HTTP_REFERER", "")[:500],
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        )
