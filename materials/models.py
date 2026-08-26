from django.db import models


class Course(models.Model):
    title = models.CharField(
        max_length=100, verbose_name="Название курса", help_text="Введите название"
    )
    preview = models.ImageField(
        upload_to="materials/preview/courses",
        blank=True,
        null=True,
        verbose_name="Превью курса",
        help_text="Добавьте превью",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание курса",
        help_text="Введите описание",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    title = models.CharField(
        max_length=100, verbose_name="Название урока", help_text="Введите название"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание урока",
        help_text="Введите описание",
    )
    preview = models.ImageField(
        upload_to="materials/preview/lessons",
        blank=True,
        null=True,
        verbose_name="Превью урока",
        help_text="Добавьте превью",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Вставьте ссылку на видео",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        verbose_name="Курс",
        help_text="Выберите курс",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
