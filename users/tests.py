from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User, Payment
from materials.models import Course, Lesson


class UserTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="user@test.com")
        self.user.set_password("testpass123")
        self.user.save()
        self.other_user = User.objects.create(email="other@test.com")
        self.other_user.set_password("testpass123")
        self.other_user.save()
        self.client.force_authenticate(user=self.user)

    def test_user_list_authenticated(self):
        url = reverse("users:user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_anonymous(self):
        self.client.force_authenticate(user=None)
        url = reverse("users:user-list")
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_user_retrieve_owner(self):
        url = reverse("users:user-detail", args=(self.user.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("email"), self.user.email)

    def test_user_retrieve_other(self):
        url = reverse("users:user-detail", args=(self.other_user.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_retrieve_anonymous(self):
        self.client.force_authenticate(user=None)
        url = reverse("users:user-detail", args=(self.user.pk,))
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_user_update_owner(self):
        url = reverse("users:user-detail", args=(self.user.pk,))
        data = {"email": "updated@test.com"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_other(self):
        url = reverse("users:user-detail", args=(self.other_user.pk,))
        data = {"email": "hacked@test.com"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_owner(self):
        url = reverse("users:user-detail", args=(self.user.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_other(self):
        url = reverse("users:user-detail", args=(self.other_user.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_register_anonymous(self):
        self.client.force_authenticate(user=None)
        url = reverse("users:register")
        data = {"email": "newuser@test.com", "password": "newpass123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@test.com").exists())

    def test_login_success(self):
        self.client.force_authenticate(user=None)
        url = reverse("users:login")
        data = {"email": "user@test.com", "password": "testpass123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_wrong_password(self):
        self.client.force_authenticate(user=None)
        url = reverse("users:login")
        data = {"email": "user@test.com", "password": "wrongpass"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        self.client.force_authenticate(user=None)
        login_url = reverse("users:login")
        login_data = {"email": "user@test.com", "password": "testpass123"}
        login_response = self.client.post(login_url, login_data)
        refresh_token = login_response.json()["refresh"]

        url = reverse("users:token_refresh")
        data = {"refresh": refresh_token}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())


class PaymentTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="user@test.com")
        self.user.set_password("testpass123")
        self.user.save()
        self.course = Course.objects.create(title="test_course", owner=self.user)
        self.lesson = Lesson.objects.create(title="test_lesson", course=self.course, owner=self.user)

        self.payment = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            payment_method="cash",
            amount=1000,
        )
        self.client.force_authenticate(user=self.user)

    def test_payment_create(self):
        url = reverse("users:payments_create")
        data = {
            "paid_course": self.course.pk,
            "payment_method": "transfer",
            "amount": "2000.00",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_payment = Payment.objects.last()
        self.assertEqual(new_payment.user, self.user)
        self.assertEqual(str(new_payment.amount), "2000.00")

    def test_payment_list(self):
        url = reverse("users:payments_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_payment_list_filter_by_method(self):
        url = reverse("users:payments_list") + "?payment_method=cash"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["payment_method"], "cash")

    def test_payment_list_filter_by_course(self):
        url = reverse("users:payments_list") + f"?paid_course={self.course.pk}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_payment_list_ordering_by_date(self):
        url = reverse("users:payments_list") + "?ordering=payment_date"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_retrieve(self):
        url = reverse("users:payments_retrieve", args=(self.payment.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("payment_method"), "cash")

    def test_payment_retrieve_anonymous(self):
        self.client.force_authenticate(user=None)
        url = reverse("users:payments_retrieve", args=(self.payment.pk,))
        response = self.client.get(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_payment_update(self):
        url = reverse("users:payments_update", args=(self.payment.pk,))
        data = {"amount": 5000}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("amount"), "5000.00")

    def test_payment_delete(self):
        url = reverse("users:payments_delete", args=(self.payment.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Payment.objects.all().count(), 0)

    def test_payment_delete_anonymous(self):
        self.client.force_authenticate(user=None)
        url = reverse("users:payments_delete", args=(self.payment.pk,))
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

