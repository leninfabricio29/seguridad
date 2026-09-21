from django.contrib import admin
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import Feature, PageView, Plan, PlanFeature, SiteImage


class PlanFeatureInline(TabularInline):
    model = PlanFeature
    extra = 3
    fields = ("text", "is_included", "order")
    ordering = ("order",)


@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    list_display = ("name", "audience", "price_column", "is_featured", "is_active", "order")
    list_filter = ("audience", "is_featured", "is_active", "show_price")
    list_editable = ("is_featured", "is_active", "order")
    search_fields = ("name", "tagline", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PlanFeatureInline]
    fieldsets = (
        ("Identificacion", {"fields": ("name", "slug", "audience", "badge")}),
        ("Contenido", {"fields": ("tagline", "description", "image")}),
        (
            "Precio",
            {
                "fields": ("price", "currency", "billing_period", "show_price"),
                "description": (
                    "El sitio muestra 'Cotizar' mientras 'Mostrar precio' este desactivado. "
                    "Puedes cargar el precio desde ya."
                ),
            },
        ),
        ("Contacto", {"fields": ("whatsapp_message",)}),
        ("Publicacion", {"fields": ("is_featured", "is_active", "order")}),
    )

    @display(description="Precio")
    def price_column(self, obj):
        return obj.price_display


@admin.register(Feature)
class FeatureAdmin(ModelAdmin):
    list_display = ("title", "audience", "icon_preview", "has_image", "is_active", "order")
    list_filter = ("audience", "is_active")
    list_editable = ("is_active", "order")
    search_fields = ("title", "description")
    fieldsets = (
        ("Contenido", {"fields": ("audience", "title", "description")}),
        (
            "Presentacion",
            {
                "fields": ("icon", "image"),
                "description": "Si no cargas imagen se muestra el icono seleccionado.",
            },
        ),
        ("Publicacion", {"fields": ("is_active", "order")}),
    )

    @display(description="Icono")
    def icon_preview(self, obj):
        return mark_safe(
            '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" '
            'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round">{obj.icon_svg}</svg>'
        )

    @display(description="Imagen", boolean=True)
    def has_image(self, obj):
        return bool(obj.image)


@admin.register(SiteImage)
class SiteImageAdmin(ModelAdmin):
    list_display = ("slot", "preview", "updated_at")
    readonly_fields = ("preview", "updated_at")
    fields = ("slot", "image", "preview", "alt_text", "updated_at")

    @display(description="Vista previa")
    def preview(self, obj):
        if not obj.image:
            return "-"
        return mark_safe(
            f'<img src="{obj.image.url}" style="max-height:120px;max-width:320px;'
            'border-radius:8px;border:1px solid #e2e8f0" />'
        )


@admin.register(PageView)
class PageViewAdmin(ModelAdmin):
    list_display = ("path", "created_at", "referer")
    list_filter = ("path", "created_at")
    search_fields = ("path", "referer")
    date_hierarchy = "created_at"
    readonly_fields = ("path", "visitor_key", "referer", "user_agent", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
