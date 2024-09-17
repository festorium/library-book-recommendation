from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserData, Author, Genre, Book, Favorite, Recommendation, NotifyMessage, Log

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['user_id', 'username', 'first_name', 'last_name', 'email', 'phone', 'address', 'created_at', 'updated_at', 'is_active', 'is_staff']

        extra_kwargs = {
            'password': {'write_only': True}
        }
    
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    genres = GenreSerializer(many=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'published_date', 'genres', 'summary']


class FavoriteSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'book', 'added_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }


class RecommendationSerializer(serializers.ModelSerializer):
    recommended_books = BookSerializer(many=True)

    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'recommended_books', 'recommended_at']

class NotifyMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyMessage
        fields = ['id', 'user', 'message', 'url', 'date', 'is_read']


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'user_id', 'action', 'timestamp', 'ip_address']