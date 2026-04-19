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
    path('api/v1/', include([
        path('', api_root, name='api-root'),
        path('auth/', include([
            path('register/', RegisterView.as_view(), name='auth-register'),
            path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
            path('profile/', ProfileView.as_view(), name='auth-profile'),
            path('activities/', UserActivityListView.as_view(), name='auth-activities'),
            path('activities/<int:pk>/', UserActivityDestroyView.as_view(), name='auth-activity-delete'),
        ])),
        path('tools/', include('tools.urls')),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
