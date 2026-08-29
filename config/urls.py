
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('materials/', include('materials.urls', namespace='materials')),
    # Важно: namespace здесь задает префикс для имен URL (users:payment-list)
    path('users/', include('users.urls', namespace='users')),
]
