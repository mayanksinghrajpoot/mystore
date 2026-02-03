from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    featured_products = Product.objects.all()[:4] # Just 4 for now
    categories = Category.objects.all()
    return render(request, 'index.html', {'featured_products': featured_products, 'categories': categories})

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Updated quantity")
    else:
        messages.success(request, "Added to cart")
    
    return redirect('cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.get_total_price() for item in items)
    return render(request, 'cart/cart.html', {'cart': cart, 'items': items, 'total': total})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart")
    return redirect('cart')

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.get_total_price() for item in items)
    
    if request.method == 'POST':
        # Create Order
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        phone = request.POST.get('phone')
        
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            address=address,
            city=city,
            phone=phone,
            total_price=total
        )
        
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
        
        # Clear cart
        cart.items.all().delete()
        messages.success(request, "Order placed successfully!")
        return redirect('order_history')
        
    return render(request, 'cart/checkout.html', {'cart': cart, 'items': items, 'total': total})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})
