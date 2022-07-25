from functools import wraps

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from oauth2client.client import FlowExchangeError, OAuth2WebServerFlow

from admin_sso import settings

REDIRECT_COOKIE_NAME = "admin_sso-next"


flow_kwargs = {
    "client_id": settings.DJANGO_ADMIN_SSO_OAUTH_CLIENT_ID,
    "client_secret": settings.DJANGO_ADMIN_SSO_OAUTH_CLIENT_SECRET,
    "scope": "email",
}
if settings.DJANGO_ADMIN_SSO_AUTH_URI:
    flow_kwargs["auth_uri"] = settings.DJANGO_ADMIN_SSO_AUTH_URI

if settings.DJANGO_ADMIN_SSO_TOKEN_URI:
    flow_kwargs["token_uri"] = settings.DJANGO_ADMIN_SSO_TOKEN_URI

if settings.DJANGO_ADMIN_SSO_REVOKE_URI:
    flow_kwargs["revoke_uri"] = settings.DJANGO_ADMIN_SSO_REVOKE_URI

flow_override = None


def set_next_cookie(view):
    @wraps(view)
    def fn(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        if request.GET.get("next"):
            response.set_cookie(REDIRECT_COOKIE_NAME, request.GET["next"], max_age=600)
        return response

    return fn


def retrieve_next(request):
    next = request.COOKIES.get(REDIRECT_COOKIE_NAME)
    return (
        next
        if url_has_allowed_host_and_scheme(
            url=next,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
        else None
    )


@set_next_cookie
def start(request):
    flow = OAuth2WebServerFlow(
        redirect_uri=request.build_absolute_uri(
            reverse("admin:admin_sso_assignment_end")
        ),
        **flow_kwargs
    )

    return HttpResponseRedirect(flow.step1_get_authorize_url())


def end(request):
    if flow_override is None:
        flow = OAuth2WebServerFlow(
            redirect_uri=request.build_absolute_uri(
                reverse("admin:admin_sso_assignment_end")
            ),
            **flow_kwargs
        )
    else:
        flow = flow_override

    code = request.GET.get("code", None)
    if not code:
        return HttpResponseRedirect(reverse("admin:index"))
    try:
        credentials = flow.step2_exchange(code)
    except FlowExchangeError:
        return HttpResponseRedirect(reverse("admin:index"))

    if credentials.id_token["email_verified"]:
        email = credentials.id_token["email"]
        user = authenticate(request, sso_email=email)
        if user and user.is_active:
            login(request, user)
            return HttpResponseRedirect(
                retrieve_next(request) or reverse("admin:index")
            )

    # if anything fails redirect to admin:index
    return HttpResponseRedirect(reverse("admin:index"))
