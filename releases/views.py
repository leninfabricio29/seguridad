from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from .models import App

from django.views.generic import TemplateView
from django.http import HttpResponse
from django.utils import timezone

class DeleteAccountView(TemplateView):
    template_name = "releases/delete_account.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context

class PrivacyTermsView(TemplateView):
    template_name = "releases/privacy_terms.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context

class HomeView(TemplateView):
    template_name = "releases/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apps = App.objects.all()
        context["apps"] = apps
        if apps.count() == 1:
            app = apps.first()
            context["app"] = app
            # Lista de imágenes de referencia no vacías
            reference_images = []
            for img in [app.reference_image1, app.reference_image2, app.reference_image3]:
                if img:
                    reference_images.append(img)
            context["reference_images"] = reference_images
            # URL de descarga de la última versión disponible (cualquier plataforma)
            latest = app.latest_version()
            if latest:
                context["latest_download_url"] = latest.file.url if latest.file else latest.external_link
        return context

class AppDetailView(DetailView):
    model = App
    template_name = "releases/app_detail.html"
    context_object_name = "app"

def latest_version_api(request, slug, platform):
    app = get_object_or_404(App, slug=slug)
    include_pr = request.GET.get("include_prerelease") == "1"
    ver = app.latest_version(platform=platform, include_prerelease=include_pr)
    if not ver:
        raise Http404("No hay versión publicada")
    payload = {
        "app": app.slug,
        "platform": platform,
        "version": ver.version,
        "build_number": ver.build_number,
        "is_prerelease": ver.is_prerelease,
        "release_notes": ver.release_notes,
        "download_url": ver.file.url if ver.file else ver.external_link,
        "published_at": ver.created_at.isoformat(),
    }
    return JsonResponse(payload)
