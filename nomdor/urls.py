from django.urls import path
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



#     CREATE UPDETE DELETE

    path('product/create/',views.ProductCreateView.as_view(),name='create-about'),
    path('product/update/<int:pk>/',views.ProductUpdateView.as_view(),name='update-about'),
    path('product/delete/<int:pk>/',views.ProductDeleteView.as_view(),name='delete-about'),
]

