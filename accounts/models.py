from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email



class Store(models.Model):
    storeName = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to the CustomUser
    registered_on = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # True if approved, False otherwise

    def __str__(self):
        return self.storeName


class CollectionCenter(models.Model):
    centerName = models.CharField(max_length=255)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link to the CustomUser
    county = models.CharField(max_length=255)
    town = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    registered_on = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # True if approved, False otherwise

    def __str__(self):
        return self.centerName


class UserCollectionCenter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    collection_center = models.ForeignKey(CollectionCenter, on_delete=models.CASCADE)
    selected_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Collection Center: {self.collection_center.centerName}"

