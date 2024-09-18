# library-book-recommendation
Django Book Management System

-- Overview
This project is a Django-based Book Management System that includes user management, book management, favorite books, recommendations, notifications, and logging features.

-- Features
User Management: Register, login, and manage users.
Book Management: CRUD operations for books and authors.
Favorite Books: Users can mark books as favorites.
Recommendations: Personalized book recommendations for users.
Notifications: System messages for users.
Logging: Track user actions and system events.

-- Models
UserData
Author
Book
Favorite
Recommendation
NotifyMessage
Log

-- Serializers
UserDataSerializer: Serializes user data.
AuthorSerializer: Serializes author data.
GenreSerializer: Serializes genre data.
BookSerializer: Serializes book data with nested authors and genres.
FavoriteSerializer: Serializes favorite books with nested book details.
RecommendationSerializer: Serializes book recommendations with nested book details.
NotifyMessageSerializer: Serializes notification messages.
LogSerializer: Serializes log entries.

-- API Endpoints
User Endpoints
Register: POST /register
Login: POST /login
Get User: GET /get_user
Logout: POST /logout
Book Endpoints
Get Books: GET /books
Get Book: GET /books/<id>
Create Book: POST /books
Update Book: PUT /books/<id>
Delete Book: DELETE /books/<id>
Author Endpoints
Get Authors: GET /authors
Get Author: GET /authors/<id>
Create Author: POST /authors
Update Author: PUT /authors/<id>
Delete Author: DELETE /authors/<id>
Favorites Endpoints
Add to Favorites: POST /favorites
Recommendations Endpoints
Get Recommendations: GET /recommendations
Notifications Endpoints
Get Notifications: GET /notifications
Logs Endpoints
Get Logs: GET /logs

