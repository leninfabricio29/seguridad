from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from releases.models import App, AppVersion

from .models import Feature, PageView, Plan, PlanFeature


class PlanModelTests(TestCase):
    def setUp(self):
        Plan.objects.all().delete()

    def test_slug_se_genera_con_la_audiencia(self):
        plan = Plan.objects.create(name="Familiar", audience="personas")
        self.assertEqual(plan.slug, "personas-familiar")

    def test_precio_oculto_muestra_cotizar(self):
        plan = Plan.objects.create(name="Familiar", price=Decimal("19.90"))
        self.assertFalse(plan.show_price)
        self.assertEqual(plan.price_display, "Cotizar")

    def test_precio_visible_se_formatea(self):
        plan = Plan.objects.create(
            name="Familiar", price=Decimal("19.90"), show_price=True
        )
        self.assertEqual(plan.price_display, "USD 19.90")

    def test_whatsapp_url_lleva_el_nombre_del_plan(self):
        plan = Plan.objects.create(name="Entidad Profesional", audience="empresas")
        url = plan.whatsapp_url
        self.assertTrue(url.startswith("https://wa.me/593959681092?text="))
        self.assertIn("Entidad%20Profesional", url)
        self.assertIn("estoy%20interesado%20en", url)

    def test_whatsapp_url_respeta_mensaje_propio(self):
        plan = Plan.objects.create(name="Flota", whatsapp_message="Quiero el plan Flota")
        self.assertIn("Quiero%20el%20plan%20Flota", plan.whatsapp_url)


class FeatureModelTests(TestCase):
    def test_icono_devuelve_svg(self):
        feature = Feature.objects.create(title="Boton fisico", icon="radio")
        self.assertIn("<circle", feature.icon_svg)

    def test_icono_desconocido_cae_al_escudo(self):
        feature = Feature.objects.create(title="X", icon="no-existe")
        self.assertIn("<path", feature.icon_svg)


class HomeViewTests(TestCase):
    def setUp(self):
        cache.clear()
        Plan.objects.all().delete()
        Feature.objects.all().delete()
        self.app = App.objects.create(name="V-SOS", description="App de emergencias")
        AppVersion.objects.create(app=self.app, platform="android", version="1.2.0")

    def test_home_responde_ok_y_muestra_la_marca(self):
        response = self.client.get(reverse("marketing:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Seguridad del Altiplano")

    def test_home_lista_planes_separados_por_audiencia(self):
        personal = Plan.objects.create(name="Personal", audience="personas")
        entidad = Plan.objects.create(name="Entidad", audience="empresas")
        PlanFeature.objects.create(plan=personal, text="1 usuario")

        response = self.client.get(reverse("marketing:home"))
        self.assertEqual(
            [p.pk for p in response.context["plans_personas"]], [personal.pk]
        )
        self.assertEqual(
            [p.pk for p in response.context["plans_empresas"]], [entidad.pk]
        )
        self.assertContains(response, "1 usuario")

    def test_home_no_muestra_planes_inactivos(self):
        Plan.objects.create(name="Viejo", audience="personas", is_active=False)
        response = self.client.get(reverse("marketing:home"))
        self.assertEqual(response.context["plans_personas"], [])

    def test_home_separa_funcionalidades_por_seccion(self):
        Feature.objects.create(title="Boton de panico", audience="app")
        Feature.objects.create(title="Reportes", audience="panel")

        response = self.client.get(reverse("marketing:home"))
        self.assertEqual(len(response.context["features_app"]), 1)
        self.assertEqual(len(response.context["features_panel"]), 1)

    def test_home_expone_la_descarga_de_la_ultima_version(self):
        AppVersion.objects.create(
            app=self.app, platform="android", version="2.0.0",
            external_link="https://ejemplo.com/apk",
        )
        response = self.client.get(reverse("marketing:home"))
        self.assertEqual(response.context["latest_version"].version, "2.0.0")
        self.assertEqual(response.context["latest_download_url"], "https://ejemplo.com/apk")

    def test_home_tolera_una_version_con_formato_invalido(self):
        # latest_version() usa packaging.Version y explota con datos no semanticos.
        AppVersion.objects.create(app=self.app, platform="ios", version="temporada 2")
        response = self.client.get(reverse("marketing:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_funciona_sin_ninguna_app_cargada(self):
        AppVersion.objects.all().delete()
        App.objects.all().delete()
        response = self.client.get(reverse("marketing:home"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["app"])


class PageViewMiddlewareTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_registra_la_visita_a_la_home(self):
        self.client.get(reverse("marketing:home"))
        self.assertEqual(PageView.objects.filter(path="/").count(), 1)

    def test_el_mismo_visitante_cuenta_una_sola_vez_como_unico(self):
        self.client.get(reverse("marketing:home"))
        self.client.get(reverse("marketing:home"))
        self.assertEqual(PageView.objects.count(), 2)
        self.assertEqual(
            PageView.objects.values("visitor_key").distinct().count(), 1
        )

    def test_no_registra_el_admin(self):
        self.client.get("/admin/")
        self.assertEqual(PageView.objects.filter(path__startswith="/admin").count(), 0)

    def test_no_registra_la_api(self):
        app = App.objects.create(name="V-SOS")
        AppVersion.objects.create(app=app, platform="android", version="1.0.0",
                                  external_link="https://ejemplo.com/apk")
        self.client.get(
            reverse("releases:latest_api", args=[app.slug, "android"])
        )
        self.assertEqual(PageView.objects.count(), 0)

    def test_el_contador_llega_a_la_plantilla(self):
        self.client.get(reverse("marketing:home"))
        cache.clear()
        response = self.client.get(reverse("marketing:home"))
        self.assertGreaterEqual(response.context["site_views_total"], 1)
        self.assertEqual(response.context["site_visitors_total"], 1)

    def test_se_puede_desactivar_por_settings(self):
        with self.settings(PAGEVIEW_TRACKING_ENABLED=False):
            self.client.get(reverse("marketing:home"))
        self.assertEqual(PageView.objects.count(), 0)


class RegresionReleasesTests(TestCase):
    """Lo que ya existia tiene que seguir funcionando igual."""

    def setUp(self):
        cache.clear()
        self.app = App.objects.create(name="V-SOS")
        self.version = AppVersion.objects.create(
            app=self.app, platform="android", version="1.0.0",
            external_link="https://ejemplo.com/apk", release_notes="Primera version",
        )

    def test_api_latest_conserva_su_contrato(self):
        response = self.client.get(
            reverse("releases:latest_api", args=[self.app.slug, "android"])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json()),
            {
                "app", "platform", "version", "build_number",
                "is_prerelease", "release_notes", "download_url", "published_at",
            },
        )
        self.assertEqual(response.json()["version"], "1.0.0")
        self.assertEqual(response.json()["download_url"], "https://ejemplo.com/apk")

    def test_app_detail_ya_no_devuelve_una_pagina_vacia(self):
        response = self.client.get(
            reverse("releases:app_detail", args=[self.app.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "V-SOS")
        self.assertContains(response, "1.0.0")

    def test_paginas_legales_siguen_respondiendo(self):
        for name in ("releases:privacy_terms", "releases:delete_account"):
            with self.subTest(url=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_la_raiz_la_sirve_marketing(self):
        response = self.client.get("/")
        self.assertEqual(response.resolver_match.view_name, "marketing:home")


class ContenidoInicialTests(TestCase):
    """La migracion 0002 deja el sitio con contenido listo para editar."""

    def test_se_cargaron_las_funcionalidades(self):
        self.assertEqual(Feature.objects.filter(audience="app").count(), 6)
        self.assertEqual(Feature.objects.filter(audience="panel").count(), 6)

    def test_se_cargaron_los_planes_de_los_dos_publicos(self):
        self.assertEqual(Plan.objects.filter(audience="personas").count(), 3)
        self.assertEqual(Plan.objects.filter(audience="empresas").count(), 3)

    def test_los_planes_sembrados_no_muestran_precio(self):
        self.assertFalse(Plan.objects.filter(show_price=True).exists())
        for plan in Plan.objects.all():
            self.assertEqual(plan.price_display, "Cotizar")

    def test_cada_plan_tiene_caracteristicas(self):
        for plan in Plan.objects.all():
            with self.subTest(plan=plan.slug):
                self.assertGreaterEqual(plan.features.count(), 5)


class ImagenDelPanelTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_la_url_de_la_imagen_llega_al_contexto(self):
        response = self.client.get(reverse("marketing:home"))
        self.assertEqual(response.context["panel_image_url"], "/media/panel/heroEntidad.png")

    def test_la_home_muestra_la_captura_del_panel(self):
        response = self.client.get(reverse("marketing:home"))
        self.assertContains(response, "/media/panel/heroEntidad.png")

    def test_la_ruta_es_configurable(self):
        with self.settings(PANEL_IMAGE="panel/otra.png"):
            response = self.client.get(reverse("marketing:home"))
        self.assertEqual(response.context["panel_image_url"], "/media/panel/otra.png")
