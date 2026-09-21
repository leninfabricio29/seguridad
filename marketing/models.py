from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from .icons import ICON_CHOICES, ICONS


class Audience(models.TextChoices):
    """Los dos publicos a los que se le vende el servicio."""

    PERSONAS = "personas", "Personas y familias"
    EMPRESAS = "empresas", "Entidades de seguridad"


class BillingPeriod(models.TextChoices):
    MENSUAL = "mensual", "Mensual"
    ANUAL = "anual", "Anual"
    UNICO = "unico", "Pago unico"
    PERSONALIZADO = "personalizado", "Personalizado"


def whatsapp_url(message):
    """Construye el enlace de WhatsApp al numero comercial configurado."""
    return f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(message)}"


class IconMixin(models.Model):
    icon = models.CharField(
        max_length=30,
        choices=ICON_CHOICES,
        default="shield",
        verbose_name="Icono",
    )

    class Meta:
        abstract = True

    @property
    def icon_svg(self):
        # El contenido viene de un diccionario interno, nunca del usuario.
        return mark_safe(ICONS.get(self.icon, ICONS["shield"]))


class Plan(models.Model):
    name = models.CharField("Nombre", max_length=80)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    audience = models.CharField(
        "Publico", max_length=20, choices=Audience.choices, default=Audience.PERSONAS
    )
    tagline = models.CharField(
        "Frase corta", max_length=140, blank=True,
        help_text="Una linea que resuma para quien es el plan.",
    )
    description = models.TextField("Descripcion", blank=True)

    # El precio se guarda desde ya, pero el sitio no lo muestra mientras
    # show_price sea False. Ver PLAN_SHOW_PRICES en settings.
    price = models.DecimalField(
        "Precio", max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Opcional. Hoy el sitio no muestra precios; se guarda para mas adelante.",
    )
    currency = models.CharField("Moneda", max_length=3, default="USD")
    billing_period = models.CharField(
        "Periodo", max_length=20, choices=BillingPeriod.choices,
        default=BillingPeriod.MENSUAL,
    )
    show_price = models.BooleanField(
        "Mostrar precio en el sitio", default=False,
        help_text="Actualmente el sitio muestra 'Cotizar'. Activalo cuando quieras publicar el precio.",
    )

    image = models.ImageField(
        "Imagen", upload_to="planes/", blank=True, null=True,
        help_text="Opcional. Recomendado 800x600 px (4:3), JPG o PNG.",
    )
    badge = models.CharField(
        "Etiqueta", max_length=30, blank=True,
        help_text="Ej: 'Mas elegido'. Se muestra sobre la tarjeta.",
    )
    whatsapp_message = models.CharField(
        "Mensaje de WhatsApp", max_length=200, blank=True,
        help_text="Opcional. Si lo dejas vacio se usa el mensaje por defecto con el nombre del plan.",
    )

    is_featured = models.BooleanField("Destacado", default=False)
    is_active = models.BooleanField("Activo", default=True)
    order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        ordering = ["audience", "order", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_audience_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.audience}-{self.name}")
        super().save(*args, **kwargs)

    @property
    def whatsapp_url(self):
        message = self.whatsapp_message or (
            f"{settings.WHATSAPP_DEFAULT_MESSAGE} {self.name}"
        )
        return whatsapp_url(message)

    @property
    def price_display(self):
        if self.show_price and self.price is not None:
            return f"{self.currency} {self.price:,.2f}"
        return "Cotizar"


class PlanFeature(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="features")
    text = models.CharField("Caracteristica", max_length=140)
    is_included = models.BooleanField(
        "Incluida", default=True,
        help_text="Si la desmarcas se muestra tachada, util para comparar planes.",
    )
    order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Caracteristica del plan"
        verbose_name_plural = "Caracteristicas del plan"
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


class FeatureAudience(models.TextChoices):
    APP = "app", "App movil (usuarios finales)"
    PANEL = "panel", "Panel administrativo (entidades)"


class Feature(IconMixin):
    """Tarjetas de funcionalidad que se listan en el sitio."""

    audience = models.CharField(
        "Seccion", max_length=20, choices=FeatureAudience.choices,
        default=FeatureAudience.APP,
    )
    title = models.CharField("Titulo", max_length=100)
    description = models.TextField("Descripcion", blank=True)
    image = models.ImageField(
        "Imagen", upload_to="features/", blank=True, null=True,
        help_text="Opcional. Recomendado 1200x900 px (4:3). Si la dejas vacia se muestra el icono.",
    )
    is_active = models.BooleanField("Activa", default=True)
    order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        verbose_name = "Funcionalidad"
        verbose_name_plural = "Funcionalidades"
        ordering = ["audience", "order", "id"]

    def __str__(self):
        return f"{self.title} ({self.get_audience_display()})"


class SiteImageSlot(models.TextChoices):
    """Cada hueco de imagen del sitio que no pertenece a un plan ni a una
    funcionalidad. Antes estaban fijos en las plantillas."""

    PANEL = "panel", "Captura del panel administrativo"
    LOGO = "logo", "Logo de la marca"
    OG = "og", "Imagen para redes sociales"


SITE_IMAGES_CACHE_KEY = "marketing:site_images"


class SiteImage(models.Model):
    slot = models.CharField(
        "Ubicacion", max_length=20, choices=SiteImageSlot.choices, unique=True,
        help_text="Donde se muestra la imagen. Solo puede haber una por ubicacion.",
    )
    image = models.ImageField(
        "Imagen", upload_to="sitio/",
        help_text=(
            "Medidas recomendadas: panel 1600x1000 px, logo 512x512 px (fondo "
            "transparente), redes sociales 1200x630 px."
        ),
    )
    alt_text = models.CharField(
        "Texto alternativo", max_length=200, blank=True,
        help_text="Descripcion breve para lectores de pantalla y buscadores.",
    )
    updated_at = models.DateTimeField("Actualizada", auto_now=True)

    class Meta:
        verbose_name = "Imagen del sitio"
        verbose_name_plural = "Imagenes del sitio"
        ordering = ["slot"]

    def __str__(self):
        return self.get_slot_display()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(SITE_IMAGES_CACHE_KEY)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete(SITE_IMAGES_CACHE_KEY)


class PageView(models.Model):
    """Una visita registrada por PageViewMiddleware."""

    path = models.CharField("Ruta", max_length=255, db_index=True)
    visitor_key = models.CharField(
        "Visitante", max_length=64, db_index=True,
        help_text="Hash de la sesion (o de IP + navegador). No guarda datos identificables.",
    )
    referer = models.CharField("Origen", max_length=500, blank=True)
    user_agent = models.CharField("Navegador", max_length=300, blank=True)
    created_at = models.DateTimeField("Fecha", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.path} - {self.created_at:%Y-%m-%d %H:%M}"
