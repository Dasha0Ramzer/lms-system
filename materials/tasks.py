from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, Subscription


@shared_task
def send_course_update_email(course_id):

    try:
        course = Course.objects.get(pk=course_id)
        subs = Subscription.objects.filter(course=course)
        emails = [s.user.email for s in subs if s.user.email and s.user.is_active]
        if emails:
            send_mail(
                subject=f"Курс «{course.title}» обновлён",
                message="Материалы курса были обновлены. Проверьте новые файлы.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails,
            )
    except Course.DoesNotExist:
        pass
