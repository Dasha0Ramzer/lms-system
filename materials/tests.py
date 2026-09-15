from http.client import responses

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="email_fo_tests@test.com")

        # --- добавлено: модератор ---
        self.moders_group, _ = Group.objects.get_or_create(name="moders")
        self.moderator = User.objects.create(email="moderator@test.com")
        self.moderator.groups.add(self.moders_group)

        self.course = Course.objects.create(title="test_title")
        self.lesson = Lesson.objects.create(
            title="test_title", course=self.course, owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self):
        url = reverse("materials:lessons_retrieve", args=(self.lesson.pk,))

        # владелец — может
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), self.lesson.title)

        # --- добавлено: модератор может retrieve ---
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_lesson_create(self):
        url = reverse("materials:lessons_create")
        data = {
            "title": "test_lesson_create",
            "course": self.course.pk,
            "video_url": "https://www.youtube.com/watch?v=test",
        }

        # обычный пользователь — может (IsNotModer пропускает)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

        # --- добавлено: модератор НЕ может (IsNotModer блокирует) ---
        self.client.force_authenticate(user=self.moderator)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.post(url, data)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_lesson_update(self):
        url = reverse("materials:lessons_update", args=(self.lesson.pk,))
        data = {"title": "test_lesson_update"}

        # владелец — может
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), "test_lesson_update")

        # --- добавлено: модератор может (IsModer | IsOwner) ---
        self.client.force_authenticate(user=self.moderator)
        response = self.client.patch(url, {"title": "updated_by_moderator"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.patch(url, data)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_lesson_delete(self):
        url = reverse("materials:lessons_delete", args=(self.lesson.pk,))

        # владелец — может
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

        # --- добавлено: модератор НЕ может (IsNotModer блокирует) ---
        # пересоздаём урок, т.к. предыдущий удалён
        lesson2 = Lesson.objects.create(
            title="test2", course=self.course, owner=self.user
        )
        url2 = reverse("materials:lessons_delete", args=(lesson2.pk,))
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.delete(url2)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_lesson_list(self):
        url = reverse("materials:lessons_list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.lesson.pk,
                    "video_url": None,
                    "title": self.lesson.title,
                    "description": None,
                    "preview": None,
                    "course": self.course.pk,
                    "owner": self.user.pk,
                },
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


class CourseTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="email_fo_tests@test.com")

        # --- добавлено: модератор ---
        self.moders_group, _ = Group.objects.get_or_create(name="moders")
        self.moderator = User.objects.create(email="moderator@test.com")
        self.moderator.groups.add(self.moders_group)

        self.course = Course.objects.create(title="test_title", owner=self.user)
        self.lesson = Lesson.objects.create(
            title="test_title", course=self.course, owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_course_retrieve(self):
        url = reverse("materials:course-detail", args=(self.course.pk,))

        # владелец — может
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), self.course.title)

        # --- добавлено: модератор может (IsModer | IsOwner) ---
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_course_create(self):
        url = reverse("materials:course-list")
        data = {"title": "test_course_create"}

        # обычный пользователь — может (IsNotModer)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.all().count(), 2)

        # --- добавлено: модератор НЕ может (IsNotModer блокирует) ---
        self.client.force_authenticate(user=self.moderator)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.post(url, data)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_course_update(self):
        url = reverse("materials:course-detail", args=(self.course.pk,))
        data = {"title": "test_course_update"}

        # владелец — может
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("title"), "test_course_update")

        # --- добавлено: модератор может (IsModer | IsOwner) ---
        self.client.force_authenticate(user=self.moderator)
        response = self.client.patch(url, {"title": "updated_by_moderator"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.patch(url, data)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_course_delete(self):
        url = reverse("materials:course-detail", args=(self.course.pk,))

        # владелец — может
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.all().count(), 0)

        # --- добавлено: модератор НЕ может (IsNotModer + IsOwner) ---
        course2 = Course.objects.create(title="course2", owner=self.user)
        url2 = reverse("materials:course-detail", args=(course2.pk,))
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(url2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.delete(url2)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_course_list(self):
        url = reverse("materials:course-list")
        response = self.client.get(url)
        data = response.json()
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.course.pk,
                    "lessons_count": Lesson.objects.all().count(),
                    "is_subscribed": False,
                    "title": self.course.title,
                    "preview": None,
                    "description": None,
                    "owner": self.user.pk,
                }
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_subscription_create(self):
        url = reverse("materials:subscription")
        data = {"course_id": self.course.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

        # --- добавлено: аноним не может ---
        self.client.force_authenticate(user=None)
        response = self.client.post(url, data)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_subscription_delete(self):
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse("materials:subscription")
        data = {"course_id": self.course.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_course_list_with_subscription(self):
        Subscription.objects.create(user=self.user, course=self.course)
        url = reverse("materials:course-list")
        response = self.client.get(url)
        data = response.json()["results"][0]
        self.assertEqual(data["is_subscribed"], True)
