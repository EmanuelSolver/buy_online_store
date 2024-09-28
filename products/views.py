from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Category
from accounts.models import Store
from .forms import ProductForm  

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
