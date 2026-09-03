from rest_framework.serializers import ModelSerializer, SerializerMethodField

from materials.models import Course, Lesson


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    lessons_count = SerializerMethodField()

    @staticmethod
    def get_lessons_count(obj):
        return obj.lesson_set.count()

    class Meta:
        model = Course
        fields = "__all__"
