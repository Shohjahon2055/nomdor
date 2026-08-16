from django.views.generic import ListView, DetailView
from .models import Category, Product


class CategoryListView(ListView):
    model = Product
    template_name = 'nomdor/menyu_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()

        return context


class CategoryProductListView(ListView):
    model = Product
    template_name = 'nomdor/menyu_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_id = self.kwargs['category_id']

        return Product.objects.filter(
            category_id=category_id,
            is_available=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()

        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'nomdor/product_detail.html'
    context_object_name = 'product'