from django.urls import path

from .views import CategoryListView,CategoryProductListView,ProductDetailView



urlpatterns = [
    path('',CategoryListView.as_view(),name='menu'),
    path('category/',CategoryListView.as_view(),name='category'),
    path('category/<int:category_id>/',CategoryProductListView.as_view(),name='category_products'),
    path('product/<int:pk>/',ProductDetailView.as_view(),name='product_detail'),
]

