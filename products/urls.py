from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='all_products'),
    path('<int:product_id>/', views.detail, name='detail'),
    path('create/', views.create, name='create-product'),
    path('update/<int:product_id>/', views.update, name='update'),
    path('delete/<int:product_id>/', views.delete, name='delete'),

    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

]