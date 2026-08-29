
from django.core.management.base import BaseCommand
from users.models import Payment, User
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = "Создаёт тестовые платежи (без очистки)"

    def handle(self, *args, **kwargs):

        try:
            user = User.objects.get(pk=1)
            course = Course.objects.first()
            lesson = Lesson.objects.first()
        except User.DoesNotExist:
            self.stderr.write("Ошибка: нет пользователя с ID=1. Создай его сначала!")
            return
        except Exception as e:
            self.stderr.write(f"Ошибка: не хватает данных (курс/урок). Детали: {e}")
            return

        if not course or not lesson:
            self.stderr.write("Ошибка: в базе нет ни одного курса или урока")
            return

        Payment.objects.create(
            user=user,
            paid_course=course,
            amount=5000.00,
            payment_method="transfer",
        )
        Payment.objects.create(
            user=user,
            paid_lesson=lesson,
            amount=1500.00,
            payment_method="cash",
        )

        self.stdout.write(self.style.SUCCESS("Тестовые платежи успешно созданы!"))