from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from accounts.permissions import login_required
from .models import Category, Product , About
from .forms import AboutForm,ProductForm

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


class AbooutView(TemplateView):
    template_name = 'nomdor/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['abouts'] = About.objects.all()
        context['products'] = Product.objects.all()

        return context

class AksiyalarListView(ListView):
    model = Product
    template_name = 'nomdor/aksiyalar_list.html'


def product_list(request):
    query=request.GET.get('q')
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'nomdor/product_list.html', context)


# CLASSDA CREATE DELETE UPDATE



class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'nomdor/create.html'
    success_url = reverse_lazy("menu")
    context_object_name = 'form'


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'nomdor/create.html'
    success_url = reverse_lazy("menu")
    context_object_name = 'form'
    pk_url_kwarg = 'pk'


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'nomdor/delete.html'
    success_url = reverse_lazy("menu")
    pk_url_kwarg = 'pk'
    context_object_name = 'product'