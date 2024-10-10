from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Category, Cart, CartItem, Order
from accounts.models import Store, CollectionCenter, UserCollectionCenter
from .forms import ProductForm  
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser
from datetime import datetime, timedelta
import base64
import json

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


@login_required
def checkout(request):
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()  # Fetch all cart items

    # Check if the user has selected a collection center
    user_collection_center = UserCollectionCenter.objects.filter(user=request.user).first()

    # If the user hasn't selected a collection center, show the available centers for selection
    if not user_collection_center:
        available_centers = CollectionCenter.objects.filter(approved=True)  # Show only approved centers

        if request.method == 'POST':
            selected_center_id = request.POST.get('collection_center')
            selected_center = get_object_or_404(CollectionCenter, id=selected_center_id)
            # Save the selected collection center for the user
            UserCollectionCenter.objects.create(user=request.user, collection_center=selected_center)
            return redirect('checkout')  # Redirect to reload the page with selected center

        return render(request, 'cart/checkout.html', {
            'items': items,
            'available_centers': available_centers
        })

    # Render the checkout template with the cart items and the selected collection center
    return render(request, 'cart/checkout.html', {
        'items': items,
        'collection_center': user_collection_center.collection_center,
        'cart': cart
    })


def process_payment(request, total):
    # Capture the total amount passed from the checkout
    context = {
        'total': total
    }
    # Here, you would typically initiate the payment process.
    return render(request, 'payments/payment.html', context)


# a view to generate access token
def get_access_token(request):

    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET

    # Combine consumer_key and consumer_secret and encode to base64
    credentials = f"{consumer_key}:{consumer_secret}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()

    # Define the URL and headers
    access_token_url = settings.TOKEN_ACCESS_URL
    headers = {
        'Authorization': f'Basic {base64_credentials}'
    }

    try:
        # Make a GET request to the access token URL with the headers
        response = requests.get(access_token_url, headers=headers)
        
        # Print the response content for debugging purposes
        print(response.text.encode('utf8'))

        response.raise_for_status()  # Raise an exception for HTTP errors
        result = response.json()
        access_token = result.get('access_token')  # Access the access token

        # Return the access token as a JSON response
        return JsonResponse({'access_token': access_token})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)})


# a view to prompt payment
@login_required
@csrf_exempt
def initiate_stk_push(request, total_amount):
    print('Initiating STK push...')

    access_token_response = get_access_token(request)
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')

        if access_token and request.method == 'POST':
            amount = float(total_amount)  
            phone = request.POST.get('mpesa_number')  # Get phone number from form
            
            # Format phone number to start with '254'
            if phone[0] == '0':
                phone = '254' + phone[1:]
            elif phone[0] == '+':
                phone = phone[1:]

            # Safaricom API configuration
            passkey = settings.PASS_KEY 
            business_short_code = settings.BUSINESS_SHORT_CODE
            process_request_url = settings.PROCESS_REQUEST_URL
            callback_url = 'https://strong-donkeys-rhyme.loca.lt/products/stk_callback/'  # Use a valid callback URL
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

            stk_push_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }

            stk_push_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': amount,
                'PartyA': phone,
                'PartyB': business_short_code, 
                'PhoneNumber': phone,
                'CallBackURL': callback_url,
                'AccountReference': "OrderPayment",
                'TransactionDesc': 'Online store order payment'
            }

            try:
                response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
                response.raise_for_status()

                response_data = response.json()
                checkout_request_id = response_data['CheckoutRequestID']

                # Save the `checkout_request_id`, `order_id`, and `user_id` in the session
                request.session['checkout_request_id'] = checkout_request_id
                request.session['user_id'] = request.user.id

                response_code = response_data.get('ResponseCode')
                if response_code == "0":
                    # Payment initiation success
                    success = True
                    return render(request, 'payments/checkout.html', {'success': success, 'checkout_request_id': checkout_request_id})
                else:
                    # Payment initiation failed
                    return render(request, 'payments/payment.html', {'success': False, 'error': 'Payment initiation failed.'})
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)})

        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})

    # Ensure to return an HttpResponse if no conditions are met
    return JsonResponse({'error': 'Invalid request.'}, status=400)


def query_stk_status(request):
    access_token_response = get_access_token(request)
    
    if isinstance(access_token_response, JsonResponse):
        access_token = access_token_response.content.decode('utf-8')
        access_token_json = json.loads(access_token)
        access_token = access_token_json.get('access_token')

        if access_token:
            query_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
            business_short_code = settings.BUSINESS_SHORT_CODE
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            passkey = settings.PASS_KEY
            password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

            # Retrieve `checkout_request_id` from the session
            checkout_request_id = request.session.get('checkout_request_id')

            if not checkout_request_id:
                return JsonResponse({'error': 'CheckoutRequestID not found in session.'})

            query_headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }

            query_payload = {
                'BusinessShortCode': business_short_code,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': checkout_request_id
            }

            try:
                response = requests.post(query_url, headers=query_headers, json=query_payload)
                response.raise_for_status()
                response_data = response.json()

                if 'ResultCode' in response_data:
                    result_code = response_data['ResultCode']
                    if result_code == '0':
                        message = "Transaction was successful"
                    else:
                        message = f"Transaction failed with result code: {result_code}"

                return JsonResponse({'message': message})
            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'error': 'Access token not found.'})
    else:
        return JsonResponse({'error': 'Failed to retrieve access token.'})


@csrf_exempt
def process_stk_callback(request):
    if request.method == 'POST':
        # Parse the callback data
        stk_callback_response = json.loads(request.body)
        
        user_id = request.session.get('user_id')
        user = None
        
        if user_id:
            try:
                user = CustomUser.objects.get(pk=user_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=400)
        
        # Log the callback data (optional)
        log_file = "stkPush_response.json"
        with open(log_file, "a") as log:
            json.dump(stk_callback_response, log)
            log.write("\n")  # Add a newline for better readability

        # Extract relevant data from the callback
        merchant_request_id = stk_callback_response['Body']['stkCallback']['MerchantRequestID']
        checkout_request_id = stk_callback_response['Body']['stkCallback']['CheckoutRequestID']
        result_code = stk_callback_response['Body']['stkCallback']['ResultCode']
        result_desc = stk_callback_response['Body']['stkCallback']['ResultDesc']

        if result_code == 0:
            # Payment is successful
            amount = None
            transaction_id = None
            user_phone_number = None
            
            metadata_items = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item']
            
            for item in metadata_items:
                if item['Name'] == 'Amount':
                    amount = item['Value']
                elif item['Name'] == 'MpesaReceiptNumber':
                    transaction_id = item['Value']
                elif item['Name'] == 'PhoneNumber':
                    user_phone_number = item['Value']
            
            # Create a new Order object
            order = Order.objects.create(
                user=user,
                cart=user.cart,  # Assuming you have a way to retrieve the user's cart
                total_amount=amount,
                payment_status=True,  # Assuming True means paid
                collection_center=user.collection_center,  # Assuming you want to set this as well
            )
            order.save()

        # Return a success response to Safaricom (important for the callback)
        response_data = {
            "ResultCode": 0,
            "ResultDesc": "Success"
        }
        return JsonResponse(response_data)

    # If the request method is not POST, return a 400 Bad Request
    return JsonResponse({"error": "Bad Request"}, status=400)
