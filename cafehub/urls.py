"""
URL configuration for cafehub project.
"""

from django.contrib import admin
from django.urls import path, include

# For media files (uploaded food images)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("core.urls")),

    path("accounts/", include("accounts.urls")),

    path("orders/", include("orders.urls")),

    path("staff/", include("staff.urls")),
]


# Show uploaded images during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )