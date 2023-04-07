from rest_framework.test import APITestCase
from Team.models import Team
from User.models import User

# Create your tests here.
# path("login", views.Login.as_view()),
# path("signup", views.SignUp.as_view()),
# path("logout", views.LogOut.as_view()),


class TestLogin(APITestCase):
    URL = "/api/v1/users/login"

    @classmethod
    def setUpTestData(cls) -> None:
        print("")
        print("Test Login")
        user = User.objects.create(username="TestUser")
        user.set_password("TestPassword")
        user.save()

    def test_login(self):
        response = self.client.post(
            self.URL,
            data={
                "username": "TestUser",
                "password": "TestPassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, "정상적인 로그인")

    def test_login_diff_password(self):
        response = self.client.post(
            self.URL,
            data={
                "username": "TestUser",
                "password": "Error Password",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "잘못된 비밀번호")

    def test_login_diff_username(self):
        response = self.client.post(
            self.URL,
            data={
                "username": "ErrorUser",
                "password": "Test Password",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "잘못된 아이디")


class TestSignUp(APITestCase):
    URL = "/api/v1/users/signup"

    @classmethod
    def setUpTestData(cls) -> None:
        print("")
        print("Test Signup")
        for name in Team.TeamChoices.values:
            Team.objects.create(name=name)

    def test_sign_up(self):
        response = self.client.post(
            self.URL,
            data={
                "username": "TestUser",
                "password": "TestPassword1!",
                "team": "단비",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, "정상적인 경우")

    def test_sign_up_non_team(self):
        response = self.client.post(
            self.URL,
            data={
                "username": "TestUser",
                "password": "TestPassword1!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "팀 없이 생성")

    def test_sign_up_non_username(self):
        response = self.client.post(
            self.URL,
            data={
                "password": "TestPassword1!",
                "team": "단비",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "아이디 없이 생성")

    def test_sign_up_non_password(self):
        response = self.client.post(
            self.URL,
            data={
                "username": "TestUser",
                "team": "단비",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "비밀번호 없이 생성")

    def test_sign_up_password_validate(self):
        response = self.client.post(
            self.URL,
            data={
                "username": "TestUser",
                "team": "단비",
                "password": "111",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, "비밀번호 유효성 검사")


class TestLogOut(APITestCase):

    URL = "/api/v1/users/logout"

    @classmethod
    def setUpTestData(cls) -> None:
        print("")
        print("Test Logout")
        cls.user = User.objects.create(username="TestUser")

    def test_logout(self):

        self.client.force_login(self.user)

        response = self.client.post(
            self.URL,
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, 200, "로그아웃 테스트")
        self.assertFalse(response.wsgi_request.user.is_authenticated, "로그아웃 여부 확인")

    def test_logout_non_login_user(self):

        response = self.client.post(
            self.URL,
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, 403, "비 로그인 유저")
