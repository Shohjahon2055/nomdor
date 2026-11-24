from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, RoleForm, User
from .models import CustomUser


def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request, user)
            return redirect('menu')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('menu')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')



# Role berish

def role_change(request):
    if request.method == 'POST':
        form=RoleForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data.get('username')
            role=form.cleaned_data.get('role')
            user=CustomUser.objects.filter(username=username.username).first()
            if user:
                user.role=role
                user.save()
                return redirect('menu')

    else:
        form=RoleForm()
    return render(request, 'accounts/role_change.html', {'form': form})


