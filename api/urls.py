from django.contrib import admin
from django.urls import path
from .views import sign_up, login, get_user, logout, get_books, get_book, create_book, update_book, delete_book, get_authors, get_author, create_author, update_author, delete_author, add_to_favorites, get_recommendations

urlpatterns = [
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('get.user', get_user, name='get_user'),
    path('logout', logout, name='logout'),
    
    # Book routes
    path('books/', get_books, name='get_books'),
    path('books/<int:id>/', get_book, name='get_book'),
    path('books/create/', create_book, name='create_book'),
    path('books/<int:id>/update/', update_book, name='update_book'),
    path('books/<int:id>/delete/', delete_book, name='delete_book'),

    # Author routes
    path('authors/', get_authors, name='get_authors'),
    path('authors/<int:id>/', get_author, name='get_author'),
    path('authors/create/', create_author, name='create_author'),
    path('authors/<int:id>/update/', update_author, name='update_author'),
    path('authors/<int:id>/delete/', delete_author, name='delete_author'),

    # Favorites and Recommendations
    path('favorites/', add_to_favorites, name='add_to_favorites'),
    path('remove.favorite/', remove_from_favorites, name='remove_from_favorites'),
    path('recommendations/', get_recommendations, name='get_recommendations'),
   
]

