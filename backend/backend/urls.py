from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")


urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/v1/', include('api.urls')),
    path("api/v1/assignments/", include('assignments.urls')),
    path("api/v1/dashboard/", include('dashboard.urls')),
    path("api/v1/analytics/", include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)