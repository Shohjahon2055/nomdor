from django.urls import path

from accounts.permissions import check_admin
from nomdor import views

from .views import CategoryListView,CategoryProductListView,ProductDetailView,AbooutView,AksiyalarListView,product_list



urlpatterns = [
    path('',CategoryListView.as_view(),name='menu'),
    path('category/',CategoryListView.as_view(),name='category'),
    path('category/<int:category_id>/',CategoryProductListView.as_view(),name='category_products'),
    path('product/<int:pk>/',ProductDetailView.as_view(),name='product_detail'),
    path('about/',AbooutView.as_view(),name='about'),
    path('aksiyalar/',AksiyalarListView.as_view(),name='aksiya'),
    path('search/',views.product_list,name='search'),

    # Likes
    path('product/<int:product_id>/like/',views.toggle_like,name='toggle_like'),

#     Savat
    path('cart/add/<int:product_id>/',views.add_to_cart,name='add-to-cart'),
    path('cart/remove/<int:product_id>/',views.remove_from_cart,name='remove-from-cart'),
    path('cart/',views.cart,name='cart'),



#     CREATE UPDETE DELETE

    path('product/create/',check_admin(views.ProductCreateView.as_view()),name='create-about'),
    path('product/update/<int:pk>/',check_admin(views.ProductUpdateView.as_view()),name='update-about'),
    path('product/delete/<int:pk>/',check_admin(views.ProductDeleteView.as_view()),name='delete-about'),
]

