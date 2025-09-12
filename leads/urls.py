from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views

# Configure router without enforcing trailing slashes
router = DefaultRouter(trailing_slash=False)
router.register(r'leads', views.LeadViewSet, basename='lead')

# Get the search view
search_view = views.LeadViewSet.as_view({'post': 'search'})

urlpatterns = [
    # Handle both slashed and non-slashed search URLs
    re_path(r'^leads/search/?$', search_view, name='lead-search'),
    path('', include(router.urls)),
]
