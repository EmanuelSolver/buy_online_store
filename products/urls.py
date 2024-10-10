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
    path('checkout/', views.checkout, name='checkout'),
    
    path('payments/<int:total>/', views.process_payment, name='process_payment'),
    path('initiate-payment/<int:total_amount>/', views.initiate_stk_push, name='initiate_payment'),  
    path('stk_callback/', views.process_stk_callback, name='stk_callback'),
    path('admin_query_check/', views.query_stk_status, name='query_stk_status'),
]

