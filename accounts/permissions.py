from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Role


def login_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return func(request, *args, **kwargs)
    return wrapper


def admin_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.role != Role.ADMIN:
            raise PermissionDenied("Sizga ruxsat yo'q.")
        return func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    return render(request, "accounts/admin_dashborat.html")


def check_admin(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.role != Role.ADMIN:
            return HttpResponse("Sizga ruxsat yo'q", status=403)
        return func(request, *args, **kwargs)
    return wrapper