from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import App, AppVersion



@admin.register(App)
class AppAdmin(ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(AppVersion)
class AppVersionAdmin(ModelAdmin):
    list_display = ("app", "platform", "version", "is_prerelease", "created_at")
    list_filter = ("platform", "is_prerelease", "app")
    search_fields = ("version", "release_notes", "app__name")
    date_hierarchy = "created_at"
