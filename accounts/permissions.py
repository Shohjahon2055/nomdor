from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied

def login_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper


def admin_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.role !="Admin":
            raise PermissionDenied
        return func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_dashboard(request):
    return render(request,"accounts/admin_dashborat.html")