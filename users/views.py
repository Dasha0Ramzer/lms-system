from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from users.models import Payment, User
from users.permissions import IsOwnerOrReadOnly
from users.serializers import PaymentSerializer, UserSerializer
from users.services import (COURSE_PRICE, LESSON_PRICE, create_stripe_price,
                            create_stripe_product, create_stripe_sessions)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class UserCreateApiView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)


class PaymentCreateApiView(CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        paid_course = serializer.validated_data.get("paid_course")
        paid_lesson = serializer.validated_data.get("paid_lesson")

        if paid_course:
            product_name = paid_course.title
            amount = COURSE_PRICE
        elif paid_lesson:
            product_name = paid_lesson.title
            amount = LESSON_PRICE
        else:
            raise ValidationError("Укажите курс или урок для оплаты.")

        # 1. Создаём продукт в Stripe
        stripe_product = create_stripe_product(product_name)

        # 2. Создаём цену
        price = create_stripe_price(
            {
                "id": stripe_product.id,
                "amount": amount,
            }
        )

        # 3. Создаём сессию
        session_id, session_url = create_stripe_sessions(price)

        # 4. Сохраняем платёж
        serializer.save(
            user=self.request.user,
            amount=amount,
            session_id=session_id,
            link=session_url,
        )


class PaymentListApiView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = (
        "payment_method",
        "paid_course",
        "paid_lesson",
    )
    ordering_fields = ("payment_date",)


class PaymentRetrieveApiView(RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentUpdateApiView(UpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentDestroyApiView(DestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
