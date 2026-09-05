from django.urls import path
from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import UserViewSet, PaymentListApiView, PaymentRetrieveApiView, PaymentCreateApiView, \
    PaymentDestroyApiView, PaymentUpdateApiView

app_name = UsersConfig.name

router = SimpleRouter()
router.register("", UserViewSet)

urlpatterns = [
    path("payments/", PaymentListApiView.as_view(), name="payments_list"),
    path("payments/<int:pk>/", PaymentRetrieveApiView.as_view(), name="payments_retrieve"),
    path("payments/create/", PaymentCreateApiView.as_view(), name="payments_create"),
    path(
        "payments/<int:pk>/delete/",
        PaymentDestroyApiView.as_view(),
        name="payments_delete",
    ),
    path(
        "payments/<int:pk>/update/", PaymentUpdateApiView.as_view(), name="payments_update"
    ),
]
urlpatterns += router.urls
