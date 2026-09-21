from django.views.generic import TemplateView

from releases.models import App

from .models import Audience, Feature, FeatureAudience, Plan


class HomeView(TemplateView):
    """Landing comercial de Seguridad del Altiplano."""

    template_name = "marketing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        plans = Plan.objects.filter(is_active=True).prefetch_related("features")
        context["plans_personas"] = [p for p in plans if p.audience == Audience.PERSONAS]
        context["plans_empresas"] = [p for p in plans if p.audience == Audience.EMPRESAS]

        features = Feature.objects.filter(is_active=True)
        context["features_app"] = [f for f in features if f.audience == FeatureAudience.APP]
        context["features_panel"] = [f for f in features if f.audience == FeatureAudience.PANEL]

        context.update(self.get_app_context())
        return context

    def get_app_context(self):
        """Datos de la app publicada. Reutiliza releases.App sin modificarlo."""
        app = App.objects.first()
        if app is None:
            return {"app": None, "reference_images": [], "versions": []}

        data = {
            "app": app,
            "reference_images": [
                image
                for image in (app.reference_image1, app.reference_image2, app.reference_image3)
                if image
            ],
            # El Meta del modelo ya ordena por -created_at.
            "versions": list(app.versions.all()[:6]),
        }

        try:
            latest = app.latest_version()
        except Exception:
            # Una version con formato no semantico no debe tumbar la home.
            latest = app.versions.first()
        if latest:
            data["latest_download_url"] = (
                latest.file.url if latest.file else latest.external_link
            )
            data["latest_version"] = latest
        return data
