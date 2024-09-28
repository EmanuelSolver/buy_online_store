from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, StoreForm, CollectionCenterForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CollectionCenter, UserCollectionCenter

User = get_user_model()  # Reference to the CustomUser model


def register(request):
    if request.method == 'POST':
        print(request.POST)  # Log the POST data
        print(request.META['CSRF_COOKIE'])  # Log the CSRF cookie
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


# User login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # 'username' will be the email in this case
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')  # Redirect to home page or any desired page
            else:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Invalid credentials')
    
    form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# User logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')  # Redirect to home page or any desired page

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


def home(request):
    return render(request, 'accounts/home.html')

#redirected at the dashboard after a successful login
def dashboard(request):
    collection_centers = CollectionCenter.objects.all()  # Get all collection centers
    cart_item_count = ...  # Logic to get the cart item count
    return render(request, 'accounts/dashboard.html', {
        'cart_item_count': cart_item_count,
        'collection_centers': collection_centers,
    })
    
  # Fetch all approved collection centers   
def select_collection_center(request):
    collection_centers = CollectionCenter.objects.filter(approved=True)  
    
    if request.method == 'POST':
        collection_center_id = request.POST.get('collection_center')
        try:
            collection_center = CollectionCenter.objects.get(id=collection_center_id)
            
            # Create or update the user's collection center choice
            user_collection_center, created = UserCollectionCenter.objects.update_or_create(
                user=request.user,
                defaults={'collection_center': collection_center}
            )
            
            messages.success(request, 'Collection center selected successfully!')
            return redirect('dashboard')  # Redirect back to the dashboard
            
        except CollectionCenter.DoesNotExist:
            messages.error(request, 'Selected collection center does not exist.')
            return redirect('select_collection_center')  # Redirect to the same page
    
    return render(request, 'accounts/select_collection_center.html', {'collection_centers': collection_centers})

# Apply to become a vendor (Store)
def apply_vendor(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.vendor = request.user  # Assign the logged-in user as the vendor
            store.approved = False  # Initially set approved to False
            store.save()
            messages.success(request, 'Your application to become a vendor has been submitted for approval.')
            return redirect('dashboard')  # Redirect to the dashboard or any desired page
    else:
        form = StoreForm()
    
    return render(request, 'accounts/apply_vendor.html', {'form': form})

# Apply for a Collection Center
def apply_collection_center(request):
    if request.method == 'POST':
        form = CollectionCenterForm(request.POST)
        if form.is_valid():
            collection_center = form.save(commit=False)
            collection_center.owner = request.user  # Assign the logged-in user as the owner
            collection_center.registered_on = timezone.now()  # Set the registered date
            collection_center.save()
            messages.success(request, 'Your application for a collection center has been submitted for approval.')
            return redirect('dashboard')  # Redirect to the dashboard or any desired page
    else:
        form = CollectionCenterForm()
    
    return render(request, 'accounts/apply_collection_center.html', {'form': form})

