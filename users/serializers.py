from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField

from users.models import User, Payment


class PaymentHistorySerializer(ModelSerializer):
    course_name = SerializerMethodField()
    lesson_title = SerializerMethodField()
    payment_method_display = CharField(
        source='get_payment_method_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = ['id', 'amount', 'payment_date', 'course_name', 'lesson_title', 'payment_method_display']

    def get_course_name(self, obj):
        return obj.paid_course.title if obj.paid_course else None

    def get_lesson_title(self, obj):
        return obj.paid_lesson.title if obj.paid_lesson else None


class UserSerializer(ModelSerializer):
    payments = PaymentHistorySerializer(many=True, read_only=True, source='payment_set')

    class Meta:
        model = User
        fields = "__all__"


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


