from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from admin_sso import settings
from admin_sso.models import Assignment


User = get_user_model()


class CredentialsMock:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FlowMock:
    """
    object to mock a flow and return all arguments given to __init__
    when calling step2_exchange
    """

    def __init__(self, id_token):
        self.credentials = CredentialsMock(id_token=id_token)

    def step2_exchange(self, *args, **kwargs):
        return self.credentials


class OAuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="admin_sso")
        self.assignment = Assignment.objects.create(
            username="",
            username_mode=settings.ASSIGNMENT_ANY,
            domain="example.com",
            user=self.user,
            weight=100,
        )

    def test_start_view(self):
        start_url = reverse("admin:admin_sso_assignment_start")
        rv = self.client.get(start_url)
        self.assertEqual(rv.status_code, 302)
        self.assertTrue("Location" in rv)
        self.assertTrue(rv["Location"].startswith(settings.DJANGO_ADMIN_SSO_AUTH_URI))

    def test_start_with_next(self):
        start_url = reverse("admin:admin_sso_assignment_start")
        rv = self.client.get(start_url + "?next=/admin/xxx/")
        self.assertEqual(rv.status_code, 302)
        self.assertTrue("Location" in rv)
        self.assertTrue(rv["Location"].startswith(settings.DJANGO_ADMIN_SSO_AUTH_URI))
        self.assertEqual(self.client.cookies["admin_sso-next"].value, "/admin/xxx/")

    def test_end_without_code(self):
        end_url = reverse("admin:admin_sso_assignment_end")
        rv = self.client.get(end_url)
        self.assertEqual(rv.status_code, 302)
        self.assertTrue("Location" in rv)
        self.assertTrue(rv["Location"].endswith("/admin/"))

    def test_end_with_invalid_code(self):
        end_url = reverse("admin:admin_sso_assignment_end")
        rv = self.client.get(end_url + "?code=xxx")
        self.assertEqual(rv.status_code, 302)
        self.assertTrue("Location" in rv)
        self.assertTrue(rv["Location"].endswith("/admin/"))

    def test_end_with_sucess(self):
        from admin_sso import views

        setattr(
            views,
            "flow_override",
            FlowMock({"email_verified": True, "email": "test@example.com"}),
        )
        end_url = reverse("admin:admin_sso_assignment_end")
        rv = self.client.get(end_url + "?code=xxx")
        self.assertEqual(rv.status_code, 302)
        self.assertTrue("Location" in rv)
        self.assertEqual(str(self.client.session["_auth_user_id"]), str(self.user.id))
        self.assertEqual(
            self.client.session["_auth_user_backend"],
            "admin_sso.auth.DjangoSSOAuthBackend",
        )
        setattr(views, "flow_override", None)

    def test_end_with_next(self):
        from admin_sso import views

        setattr(
            views,
            "flow_override",
            FlowMock({"email_verified": True, "email": "test@example.com"}),
        )
        self.client.cookies["admin_sso-next"] = "/admin/xxx/"
        end_url = reverse("admin:admin_sso_assignment_end")
        rv = self.client.get(end_url + "?code=xxx")
        self.assertEqual(rv.status_code, 302)
        self.assertTrue("Location" in rv)
        self.assertTrue(rv["Location"].endswith("/admin/xxx/"))
        self.assertEqual(str(self.client.session["_auth_user_id"]), str(self.user.id))
        self.assertEqual(
            self.client.session["_auth_user_backend"],
            "admin_sso.auth.DjangoSSOAuthBackend",
        )
        setattr(views, "flow_override", None)

    def test_end_with_invalid_next(self):
        from admin_sso import views

        setattr(
            views,
            "flow_override",
            FlowMock({"email_verified": True, "email": "test@example.com"}),
        )
        self.client.cookies["admin_sso-next"] = "http://xxx"
        end_url = reverse("admin:admin_sso_assignment_end")
        rv = self.client.get(end_url + "?code=xxx")
        self.assertEqual(rv.status_code, 302)
        self.assertTrue("Location" in rv)
        self.assertTrue(rv["Location"].endswith("/admin/"))
        self.assertEqual(str(self.client.session["_auth_user_id"]), str(self.user.id))
        self.assertEqual(
            self.client.session["_auth_user_backend"],
            "admin_sso.auth.DjangoSSOAuthBackend",
        )
        setattr(views, "flow_override", None)

    def test_end_with_email_not_verified(self):
        from admin_sso import views

        setattr(
            views,
            "flow_override",
            FlowMock({"email_verified": False, "email": "test@example.com"}),
        )
        end_url = reverse("admin:admin_sso_assignment_end")
        rv = self.client.get(end_url + "?code=xxx")
        self.assertEqual(rv.status_code, 302)
        self.assertTrue("Location" in rv)
        self.assertFalse("_auth_user_id" in self.client.session)
        self.assertFalse("_auth_user_backend" in self.client.session)
        setattr(views, "flow_override", None)
