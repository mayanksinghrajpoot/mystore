from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from store.models import Product, Category, Order
from django.db.models import Sum

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin, login_url='/user/login/')
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    }
    return render(request, 'adminapp/dashboard.html', context)

@user_passes_test(is_admin, login_url='/user/login/')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'adminapp/category_list.html', {'categories': categories})

@user_passes_test(is_admin, login_url='/user/login/')
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        if 'image' in request.FILES:
            image = request.FILES['image']
        else:
            image = None
            
        Category.objects.create(name=name, slug=slug, image=image)
        messages.success(request, 'Category created successfully')
        return redirect('admin_category_list')
    return render(request, 'adminapp/category_form.html')

@user_passes_test(is_admin, login_url='/user/login/')
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        if 'image' in request.FILES:
            category.image = request.FILES['image']
        category.save()
        messages.success(request, 'Category updated successfully')
        return redirect('admin_category_list')
    return render(request, 'adminapp/category_form.html', {'category': category})

@user_passes_test(is_admin, login_url='/user/login/')
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully')
        return redirect('admin_category_list')
    return render(request, 'adminapp/confirm_delete.html', {'object': category, 'type': 'Category'})

@user_passes_test(is_admin, login_url='/user/login/')
def product_list(request):
    products = Product.objects.all().select_related('category')
    return render(request, 'adminapp/product_list.html', {'products': products})

@user_passes_test(is_admin, login_url='/user/login/')
def product_add(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        category_id = request.POST.get('category')
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        
        image = None
        if 'image' in request.FILES:
            image = request.FILES['image']
            
        category = get_object_or_404(Category, pk=category_id)
        
        Product.objects.create(
            category=category,
            name=name,
            slug=slug,
            description=description,
            price=price,
            stock=stock,
            image=image
        )
        messages.success(request, 'Product created successfully')
        return redirect('admin_product_list')
        
    return render(request, 'adminapp/product_form.html', {'categories': categories})

@user_passes_test(is_admin, login_url='/user/login/')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        product.category = get_object_or_404(Category, pk=category_id)
        product.name = request.POST.get('name')
        product.slug = request.POST.get('slug')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
            
        product.save()
        messages.success(request, 'Product updated successfully')
        return redirect('admin_product_list')
        
    return render(request, 'adminapp/product_form.html', {'product': product, 'categories': categories})

@user_passes_test(is_admin, login_url='/user/login/')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully')
        return redirect('admin_product_list')
    return render(request, 'adminapp/confirm_delete.html', {'object': product, 'type': 'Product'})

@user_passes_test(is_admin, login_url='/user/login/')
def order_list(request):
    orders = Order.objects.order_by('-created_at')
    return render(request, 'adminapp/order_list.html', {'orders': orders})

@user_passes_test(is_admin, login_url='/user/login/')
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'adminapp/order_detail.html', {'order': order})

@user_passes_test(is_admin, login_url='/user/login/')
def order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {new_status}')
    return redirect('admin_order_detail', pk=pk)
