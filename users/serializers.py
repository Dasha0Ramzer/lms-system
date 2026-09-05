from rest_framework.serializers import (CharField, ModelSerializer,
                                        SerializerMethodField)

from users.models import Payment, User


class PaymentHistorySerializer(ModelSerializer):
    course_name = SerializerMethodField()
    lesson_title = SerializerMethodField()
    payment_method_display = CharField(
        source="get_payment_method_display", read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "amount",
            "payment_date",
            "course_name",
            "lesson_title",
            "payment_method_display",
        ]

    def get_course_name(self, obj):
        return obj.paid_course.title if obj.paid_course else None

    def get_lesson_title(self, obj):
        return obj.paid_lesson.title if obj.paid_lesson else None


class UserSerializer(ModelSerializer):
    payments = PaymentHistorySerializer(many=True, read_only=True, source="payment_set")
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if not request or request.user != instance:
            representation.pop('payments', None)
        return representation


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
