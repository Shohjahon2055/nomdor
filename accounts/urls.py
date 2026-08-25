from django.urls import path


from accounts import views,permissions

urlpatterns = [
    path('register/',views.register_user,name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('admin-dashrobot/',permissions.admin_dashboard,name='admin-dashrobot'),
]