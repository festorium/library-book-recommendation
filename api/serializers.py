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
        fields = [
            'id', 
            'name', 
            'gender', 
            'image_url', 
            'about', 
            'ratings_count', 
            'average_rating', 
            'text_reviews_count', 
            'work_ids', 
            'book_ids', 
            'works_count', 
            'fans_count'
        ]

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    genres = GenreSerializer(many=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 
            'title', 
            'genres',
            'author_id', 
            'work_id', 
            'isbn', 
            'isbn13', 
            'asin', 
            'language', 
            'average_rating', 
            'rating_dist', 
            'ratings_count', 
            'text_reviews_count', 
            'publication_date', 
            'original_publication_date', 
            'format', 
            'edition_information', 
            'image_url', 
            'publisher', 
            'num_pages', 
            'series_id', 
            'series_name', 
            'series_position', 
            'shelves', 
            'description'
        ]
        
        def validate_author_id(self, value):
            try:
                author = Author.objects.get(id=value)
                return author
            except Author.DoesNotExist:
                raise serializers.ValidationError("Author not found")

        def create(self, validated_data):
            author = validated_data.pop('author_id')
            book = Book.objects.create(author=author, **validated_data)
            return book

        def update(self, instance, validated_data):
            author = validated_data.pop('author_id', None)
            if author:
                instance.author = author
            instance.title = validated_data.get('title', instance.title)
            instance.save()
            return instance

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