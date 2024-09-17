import os
import smtplib, jwt, datetime
import requests, uuid, secrets
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from rest_framework import viewsets, status, generics, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, BookSerializer, AuthorSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from .models import UserData, Book, Author, Favorite, Log
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail import send_mail
from django.conf import settings
from .permission import CheckAuth
from .notification import send_email_verification
from rest_framework.decorators import api_view 
import numpy as np 


secret = os.environ.get('secret')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM')
AUTHORIZATION = 'Authorization'
FRONTEND_URL = ""


def generate_code():
    code = secrets.token_urlsafe(12)
    return str(code)

       
class CheckToken(APIView):
    def post(self, request):
        if request.headers['Authorization']:
            token  = request.headers['Authorization']
            if not token:
                raise AuthenticationFailed('Unauthenticated')
            try:
                payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Unathenticated')
        else:
            raise AuthenticationFailed('Unathenticated')

class GenerateToken(APIView):
    """
        Generates web token 
        for internal calls only
        Returns a web token
    """
    def post(self, request):
        email = request.data['email']
        payload = {
                'email': email,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                'iat': datetime.datetime.utcnow()
            }

        token = jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)
        response = Response()
        response.data = {
            "ok": True,
            'token': token
        }
        
        return response

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        email = request.data.get('email')
        response = Response()

        # Instantiate GenerateToken class
        generate_token = GenerateToken()
        token_response = generate_token.post(request)

        verification_url = FRONTEND_URL + "/auth/verify/" + str(token_response.data['token'])

        # Send email verification notification 
        verification_response = send_email_verification(verification_url, email)

        if verification_response.status_code == 200:
            if UserData.objects.filter(username=request.data['username']).exists():
                response.data = {
                    "ok": False,
                    "message": "User already exists"
                }
                response.status_code = 400
            else:
                code = UserData.generate_code()
                data = request.data.copy()
                data['user_id'] = code
                serializer = UserSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    response.data = {
                        "ok": True,
                        "message": "User registered successfully. Please verify your email."
                    }
                    response.status_code = 200
                else:
                    response.data = {
                        "ok": False,
                        "message": "Invalid user data",
                        "errors": serializer.errors
                    }
                    response.status_code = 400
        else:
            # Email not sent successfully
            response.data = {
                "ok": False,
                "message": "Failed to send email verification"
            }
            response.status_code = 400

        return response
    
       
def login(request):
    response = Response()
    try:
        if 'username' not in request.data or 'password' not in request.data:
            response.data = {
                "ok": False,
                "details": "Invalid request. Missing username or password."
            }
            return response

        username = request.data['username']
        password = request.data['password']
        user = UserData.objects.filter(username=username).first()

        if user is None:
            response.data = {
                "ok": False,
                "message": "User not found"
            }
            return response

        if not user.check_password(password):
            response.data = {
                "ok": False,
                "message": "Incorrect password"
            }
            return response

        if user.user_verification == 0:
            response.data = {
                "ok": False,
                "message": "User not verified"
            }
            return response

        if not user.is_active:
            response.data = {
                "ok": False,
                "message": "User is not active"
            }
            return response

        payload = {
            'id': user.user_id,  
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=180),
            'iat': datetime.datetime.utcnow()
        }

        user.last_login = timezone.now()
        user.save()

        token = jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)
        response.set_cookie(
            key='plt', 
            value=token, 
            httponly=True, 
            samesite='None', 
            secure=False
        )
        response.data = {
            "ok": True,
            "token": token,
            "user_id": user.user_id,
        }

        Log.objects.create(user_id=user, action='User login', ip_address=request.META.get('REMOTE_ADDR'))

    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred. Please try again later."
        }

    return response

#  Get a single user
@api_view(['POST'])
@CheckAuth
def get_user(request):
    response = Response()
    try:
        user = UserData.objects.filter(user_id=request.data['user_id']).first()
        if user is not None:
            serializer = UserSerializer(user)
            response.data = {"ok": True, "details": "User exists", "data": serializer.data, "role": user.UserRole}
        else:
            response.data = {"ok": False, "details": "user does not exist"}
    except KeyError:
        response.data = {"ok": False, "details": "Invalid request"}
    
    return response

#  Logout user
@api_view(['POST'])
@CheckAuth
def logout(request):
    """
    Delete user token
    Returns True
    """
    response = Response()
    response.delete_cookie('plt')
    response.data = {
        'ok': True
    }
    return response

#  Retrieve a list of all books.
@api_view(['GET'])
def get_books(request):
    response = Response()
    try:
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        response.data = {
            "ok": True,
            "books": serializer.data
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while fetching the books."
        }
    return response

#  Retrieve a specific book by ID.
@api_view(['GET'])
def get_book(request, id):
    response = Response()
    try:
        book = Book.objects.filter(id=id).first()
        if book is None:
            response.data = {
                "ok": False,
                "details": "Book not found"
            }
            return response

        serializer = BookSerializer(book)
        response.data = {
            "ok": True,
            "book": serializer.data
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while fetching the book."
        }
    return response

#  Create a new book (protected).
@api_view(['POST'])
@CheckAuth
def create_book(request):
    response = Response()
    try:
        if 'title' not in request.data or 'author_id' not in request.data:
            response.data = {
                "ok": False,
                "details": "Invalid request. Missing title or author."
            }
            return response

        title = request.data['title']
        author = Author.objects.filter(id=request.data['author_id']).first()

        if author is None:
            response.data = {
                "ok": False,
                "details": "Author not found"
            }
            return response

        book = Book.objects.create(title=title, author=author)
        book.save()

        response.data = {
            "ok": True,
            "details": "Book created successfully."
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while creating the book."
        }
    return response

#  Update an existing book (protected).
@api_view(['PUT'])
@CheckAuth
def update_book(request, id):
    response = Response()
    try:
        book = Book.objects.filter(id=id).first()

        if book is None:
            response.data = {
                "ok": False,
                "details": "Book not found"
            }
            return response

        title = request.data.get('title', book.title)
        author = Author.objects.filter(id=request.data.get('author_id', book.author.id)).first()

        if author is None:
            response.data = {
                "ok": False,
                "details": "Author not found"
            }
            return response

        book.title = title
        book.author = author
        book.save()

        response.data = {
            "ok": True,
            "details": "Book updated successfully."
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while updating the book."
        }
    return response

#  Delete a book (protected).
@api_view(['DELETE'])
@CheckAuth
def delete_book(request, id):
    response = Response()
    try:
        book = Book.objects.filter(id=id).first()

        if book is None:
            response.data = {
                "ok": False,
                "details": "Book not found"
            }
            return response

        book.delete()

        response.data = {
            "ok": True,
            "details": "Book deleted successfully."
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while deleting the book."
        }
    return response

#  Retrieve a list of all authors.
@api_view(['GET'])
def get_authors(request):
    response = Response()
    try:
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        response.data = {
            "ok": True,
            "authors": serializer.data
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while fetching the authors."
        }
    return response

#  Retrieve a specific author by ID
@api_view(['GET'])
def get_author(request, id):
    response = Response()
    try:
        author = Author.objects.filter(id=id).first()
        if author is None:
            response.data = {
                "ok": False,
                "details": "Author not found"
            }
            return response

        serializer = AuthorSerializer(author)
        response.data = {
            "ok": True,
            "author": serializer.data
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while fetching the author."
        }
    return response

#  Create a new author (protected).
@api_view(['POST'])
@CheckAuth
def create_author(request):
    response = Response()
    try:
        if 'name' not in request.data:
            response.data = {
                "ok": False,
                "details": "Invalid request. Missing author name."
            }
            return response

        name = request.data['name']
        author = Author.objects.create(name=name)
        author.save()

        response.data = {
            "ok": True,
            "details": "Author created successfully."
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while creating the author."
        }
    return response

#  Update an existing author (protected).
@api_view(['PUT'])
@CheckAuth
def update_author(request, id):
    response = Response()
    try:
        author = Author.objects.filter(id=id).first()

        if author is None:
            response.data = {
                "ok": False,
                "details": "Author not found"
            }
            return response

        name = request.data.get('name', author.name)
        author.name = name
        author.save()

        response.data = {
            "ok": True,
            "details": "Author updated successfully."
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while updating the author."
        }
    return response

#  Delete an author (protected).
@api_view(['DELETE'])
@jCheckAuth
def delete_author(request, id):
    response = Response()
    try:
        author = Author.objects.filter(id=id).first()

        if author is None:
            response.data = {
                "ok": False,
                "details": "Author not found"
            }
            return response

        author.delete()

        response.data = {
            "ok": True,
            "details": "Author deleted successfully."
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while deleting the author."
        }
    return response

#  Add a book to a user's favorites (protected).
@api_view(['POST'])
@CheckAuth
def add_to_favorites(request):
    response = Response()
    try:
        user = UserData.objects.filter(user_id=request.data['user_id']).first()
        book_id = request.data['book_id']

        book = Book.objects.filter(id=book_id).first()
        if book is None:
            response.data = {
                "ok": False,
                "details": "Book not found"
            }
            return response

        favorite, created = Favorite.objects.get_or_create(user=user.id, book=book)
        if not created:
            response.data = {
                "ok": False,
                "details": "Book already in favorites"
            }
            return response

        response.data = {
            "ok": True,
            "details": "Book added to favorites."
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while adding to favorites."
        }
    return response

#  Retrieve a list of recommended books for the user based on their favorites.
@api_view(['GET'])
@CheckAuth
def get_recommendations(request):
    response = Response()
    try:
        user = UserData.objects.filter(user_id=request.data['user_id']).first()
        recommendations = recommend_books(user) 
        serializer = BookSerializer(recommendations, many=True)

        response.data = {
            "ok": True,
            "recommendations": serializer.data
        }
    except Exception as e:
        response.data = {
            "ok": False,
            "details": "An error occurred while fetching recommendations."
        }
    return response

def recommend_books(user):
    # Get the user's favorite books (up to 20)
    favorites = Favorite.objects.filter(user=user).select_related('book')[:20]

    if not favorites.exists():
        return []

    # Generate feature matrix for favorite books (e.g., genre, author)
    favorite_books = [favorite.book for favorite in favorites]
    favorite_features = np.array([book.get_feature_vector() for book in favorite_books])

    # Get all other books not in the favorite list
    all_books = Book.objects.exclude(id__in=[book.id for book in favorite_books])
    all_books_features = np.array([book.get_feature_vector() for book in all_books])

    # Calculate similarity between favorites and all other books
    similarity_scores = cosine_similarity(favorite_features, all_books_features)

    # Get top 5 recommended books based on the highest similarity scores
    recommended_indices = similarity_scores.argsort()[-5:][::-1]
    recommended_books = [all_books[i] for i in recommended_indices]

    return recommended_books