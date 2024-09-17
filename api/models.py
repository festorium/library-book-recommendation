import secrets
import datetime
import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, Permission, PermissionsMixin
from django.core.validators import MinValueValidator

    
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The username must be set')
        if not email:
            raise ValueError('The email must be set')
        user = self.model(username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class UserData(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)    
    user_verification = models.BooleanField(default=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['user_id', 'email']

    def generate_code():
        code = secrets.token_urlsafe(12)
        return str(code)

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(Group, related_name='userdata_groups', verbose_name='groups')
    user_permissions = models.ManyToManyField(Permission, related_name='userdata_user_permissions', verbose_name='user permissions')

class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    published_date = models.DateField()
    genres = models.ManyToManyField('Genre', related_name='books') 
    summary = models.TextField(null=True, blank=True) 
    def __str__(self):
        return self.title

    def get_feature_vector(self):
        genre_vector = [genre.id for genre in self.genres.all()]
        author_vector = [self.author.id]
        return genre_vector + author_vector

class Favorite(models.Model):
    user = models.ForeignKey(UserData, related_name='favorites', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='favorited_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.email} - {self.book.title}'

class Recommendation(models.Model):
    user = models.ForeignKey(UserData, related_name='recommendations', on_delete=models.CASCADE)
    recommended_books = models.ManyToManyField(Book)
    recommended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Recommendations for {self.user.email} on {self.recommended_at}'

class NotifyMessage(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    url = models.URLField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
class Log(models.Model):
    user_id = models.ForeignKey(UserData, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
    
