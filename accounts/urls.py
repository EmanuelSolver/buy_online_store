from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    path('apply/vendor/', views.apply_vendor, name='apply_vendor'),
    path('apply/collection-center/', views.apply_collection_center, name='apply_collection_center'),
    path('select/collection_center/', views.select_collection_center, name='select_collection_center'),
]
