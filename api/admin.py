from django.contrib import admin
from .models import UserData, Author, Book, Favorite, Log, Recommendation

# Register your models here.
admin.site.register(UserData)
admin.site.register(Author)
admin.site.register(Log)
admin.site.register(Book)
admin.site.register(Favorite)
admin.site.register(Recommendation)
