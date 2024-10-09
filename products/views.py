from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Category, Cart, CartItem
from accounts.models import Store
from .forms import ProductForm  
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse

def all_products(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'products/all_products.html', {'products': products})


def detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Get the product or return 404
    return render(request, 'products/detail.html', {'product': product})


def create(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        store_id = request.POST['store']
        category_id = request.POST['category']  # Change to category_id

        store = get_object_or_404(Store, id=store_id)
        category = get_object_or_404(Category, id=category_id)  # Fetch category

        product = Product(name=name, description=description, price=price, store=store, category=category)
        product.save()
        return redirect('all_products')

    # For GET request, fetch stores and categories to populate the dropdowns
    stores = Store.objects.all()
    categories = Category.objects.all()  # Fetch all categories
    return render(request, 'products/create.html', {'stores': stores, 'categories': categories})


def update(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Get the product or return 404
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)  # Create a form instance with the existing product
        if form.is_valid():
            form.save()  # Save the updated product to the database
            messages.success(request, 'Product updated successfully!')
            return redirect('detail', product_id=product.id)  # Redirect to the product detail page
    else:
        form = ProductForm(instance=product)  # Fill the form with the existing product data

    return render(request, 'products/edit_form.html', {'form': form, 'product': product})


def delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('all_products')

def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return cart

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Create or update cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1  # Increase quantity if item already exists
        cart_item.save()

    print(f"Added {product.name} to the cart!")  # Debugging statement
    return redirect('landing-home') 

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()  # Get all cart items; make sure to use related name

    print(f"\nCart for {request.user.username}:")
    print("Cart items:", items)  # Debugging statement

    return render(request, 'cart/view_cart.html', {'cart': cart, 'items': items})


def update_cart_item(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    
    return redirect('view_cart')

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    
    return redirect('view_cart')
