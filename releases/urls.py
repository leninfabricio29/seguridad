from django.urls import path
from . import views

app_name = "releases"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("app/<slug:slug>/", views.AppDetailView.as_view(), name="app_detail"),
    path("delete-account/", views.DeleteAccountView.as_view(), name="delete_account"),
    path("privacy-terms/", views.PrivacyTermsView.as_view(), name="privacy_terms"),
    # Endpoints simples para que tu app móvil consulte la última versión:
    path("api/latest/<slug:slug>/<str:platform>/", views.latest_version_api, name="latest_api"),
]
