from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from camps.views import camp_redirect_by_id
from camps.sitemaps import StaticViewSitemap, SurfCampSitemap, CountrySitemap

sitemaps = {
    'static': StaticViewSitemap,
    'camps': SurfCampSitemap,
    'countries': CountrySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('camps.urls')),
    path('api/', include('spots.urls')),
    path('api/', include('bookings.urls')),
    path('api/', include('lessons.urls')),
    path('camps/<int:pk>/', camp_redirect_by_id, name='camp-redirect-by-id'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
