from django.shortcuts import render
from products.models import Category, Product  # Import the models

def landing_page(request):
    categories = Category.objects.all()  # Fetch all categories

    # Create a dictionary to store products by category
    category_products = {}
    for category in categories:
        category_products[category] = Product.objects.filter(category=category)

    context = {
        'categories': categories,
        'category_products': category_products,
    }
    return render(request, 'landing/landing_page.html', context)