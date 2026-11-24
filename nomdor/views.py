
from .forms import AboutForm, ProductForm, CheckoutForm
from .models import Order
from .services import create_order
from telegram_bot.notify import send_new_order

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







# SAVAT
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def remove_from_cart(request, product_id):

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def cart(request):
    cart=request.session.get('cart',{})
    products=[]
    total=0
    for product_id,quantity in cart.items():
        product=get_object_or_404(Product, id=product_id)
        subtotal=product.price*quantity
        total+=subtotal
        products.append({
            'product':product,
            'quantity':quantity,
            'subtotal':subtotal,
        })
    context={
        'products':products,
        'total':total,
    }

    return render(request, 'nomdor/cart.html', context)










# LIKES

from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,Like


@login_required
def toggle_like(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    user=request.user

    like,created=Like.objects.get_or_create(user=user,product=product)
    if created:
        product.likes.add(user)

    else:
        product.likes.remove(user)

    return redirect('product_detail',pk=product.id)


# LAKATSIYA

def lokasions(request):
    return render(request,'nomdor/lokasions.html')


# CHEK BUYURTMANI SAQLASH

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    products = Product.objects.filter(id__in=cart.keys(), is_available=True)
    items = [(p, cart[str(p.id)]) for p in products]
    if not items:
        return redirect('cart')
    total = sum(p.price * q for p, q in items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            order = create_order(
                items=items,
                phone=d['phone'],
                name=d['name'],
                delivery_type=d['delivery_type'],
                address=d['address'],
                source=Order.Source.SITE,
                user=request.user,
            )
            send_new_order(order)
            request.session['cart'] = {}
            request.session['last_order_id'] = order.id
            return redirect('order_success')
    else:
        form = CheckoutForm(initial={
            'name': request.user.get_full_name() or request.user.username,
            'phone': request.user.phone,
        })

    return render(request, 'nomdor/checkout.html', {
        'form': form,
        'items': [{'product': p, 'quantity': q, 'subtotal': p.price * q} for p, q in items],
        'total': total,
    })


def order_success(request):
    order_id = request.session.get('last_order_id')
    order = Order.objects.filter(id=order_id).first() if order_id else None
    return render(request, 'nomdor/order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return render(request, 'nomdor/my_orders.html', {'orders': orders})