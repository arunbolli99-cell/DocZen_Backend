from django.contrib import admin
from django.urls import path, include
from core.views import api_root, RegisterView, ProfileView, UserActivityListView, UserActivityDestroyView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root Heartbeat
    path('', api_root, name='health-check'),
    
    # Root API view
    path('api/v1/', api_root, name='api-root'),
    
    # Auth Endpoints
    path('api/v1/auth/register/', RegisterView.as_view(), name='auth-register'),
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/profile/', ProfileView.as_view(), name='auth-profile'),
    path('api/v1/auth/activities/', UserActivityListView.as_view(), name='auth-activities'),
    path('api/v1/auth/activities/<int:pk>/', UserActivityDestroyView.as_view(), name='auth-activity-delete'),
    
    # Tools Endpoints
    path('api/v1/tools/', include('tools.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
