"""Registra en el admin la captura del panel que ya estaba en media/.

Antes la ruta vivia en settings.PANEL_IMAGE y solo se podia cambiar tocando
codigo. Esta migracion crea la fila correspondiente apuntando al mismo archivo,
para que aparezca ya cargada en Sitio web > Imagenes del sitio y se pueda
reemplazar desde ahi.

No copia ni mueve el archivo, y no hace nada si la fila ya existe o si el
archivo no esta en disco.
"""

from django.conf import settings
from django.db import migrations


def registrar_imagen_del_panel(apps, schema_editor):
    SiteImage = apps.get_model("marketing", "SiteImage")
    if SiteImage.objects.filter(slot="panel").exists():
        return

    ruta = getattr(settings, "PANEL_IMAGE", "")
    if not ruta or not (settings.MEDIA_ROOT / ruta).exists():
        return

    SiteImage.objects.create(
        slot="panel",
        image=ruta,
        alt_text="Panel administrativo de monitoreo en tiempo real",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("marketing", "0003_siteimage"),
    ]

    operations = [
        # Revertir no borra la fila: la imagen puede haberse cambiado desde el admin.
        migrations.RunPython(registrar_imagen_del_panel, migrations.RunPython.noop),
    ]
