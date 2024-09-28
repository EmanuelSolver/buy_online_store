from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Store, CollectionCenter

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'mobile_number', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'mobile_number', 'address')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'user_type', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),  # Remove 'date_joined' from here
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active', 'user_type')}
        ),
    )
    

class CollectionCenterAdmin(admin.ModelAdmin):
    list_display = ('centerName', 'owner', 'approved', 'registered_on')

class StoreAdmin(admin.ModelAdmin):
    list_display = ('storeName', 'location', 'vendor', 'approved', 'registered_on')
    search_fields = ('storeName', 'vendor__username')  # Allows searching by store name and vendor username
    list_filter = ('approved',)  # Allows filtering by approval status


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(CollectionCenter, CollectionCenterAdmin)
