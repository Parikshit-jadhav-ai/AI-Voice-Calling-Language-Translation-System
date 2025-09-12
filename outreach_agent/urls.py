from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin URLs - handle both with and without trailing slash
    path('admin', RedirectView.as_view(url='/admin/', permanent=True)),
    path('admin/', admin.site.urls),
    
    # API URLs
    re_path(r'^api/auth/token/?$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^api/auth/token/refresh/?$', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('leads.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
