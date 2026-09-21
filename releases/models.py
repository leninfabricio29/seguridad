from django.db import models
from django.utils.text import slugify
from packaging.version import Version

PLATFORMS = (
    ("android", "Android"),
    ("ios", "iOS"),
    ("web", "Web/Desktop"),
)

def upload_path(instance, filename):
    # media/<app-slug>/<platform>/<version>/<filename>
    return f"{instance.app.slug}/{instance.platform}/{instance.version}/{filename}"

class App(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    hero_image = models.ImageField(upload_to="hero/", blank=True, null=True)
    # Nuevos campos para imágenes de referencia
    reference_image1 = models.ImageField(upload_to="reference/", blank=True, null=True, verbose_name="Imagen de referencia 1")
    reference_image2 = models.ImageField(upload_to="reference/", blank=True, null=True, verbose_name="Imagen de referencia 2")
    reference_image3 = models.ImageField(upload_to="reference/", blank=True, null=True, verbose_name="Imagen de referencia 3")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def latest_version(self, platform=None, include_prerelease=False):
        qs = self.versions.all()
        if platform:
            qs = qs.filter(platform=platform)
        if not include_prerelease:
            qs = qs.filter(is_prerelease=False)
        # orden semántico descendente
        versions = sorted(qs, key=lambda v: Version(v.version), reverse=True)
        return versions[0] if versions else None

class AppVersion(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name="versions")
    platform = models.CharField(max_length=20, choices=PLATFORMS, default="android")
    version = models.CharField(max_length=50, help_text="SemVer, ej: 1.2.0")
    build_number = models.CharField(max_length=20, blank=True, help_text="Opcional")
    file = models.FileField(upload_to=upload_path, blank=True, null=True)
    external_link = models.URLField(blank=True, help_text="Si no subes archivo (TestFlight, Play Console, etc.)")
    release_notes = models.TextField(blank=True)
    is_prerelease = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("app", "platform", "version")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.app.name} {self.platform} {self.version}"

    def clean(self):
        # valida semver
        Version(self.version)  # lanza excepción si es inválida

    @property
    def has_download(self):
        return bool(self.file or self.external_link)
