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
user_id: Unique identifier for the user.
username: User's username.
first_name: User's first name.
last_name: User's last name.
email: User's email address.
phone: User's phone number.
address: User's address.
created_at: Timestamp when the user was created.
updated_at: Timestamp when the user was last updated.
is_active: Boolean indicating if the user is active.
is_staff: Boolean indicating if the user has staff privileges.

Author
name: Author's name.
Genre
name: Genre name.

Book
title: Book title.
author: Foreign key to Author.
published_date: Date when the book was published.
genres: Many-to-many relationship with Genre.
summary: Book summary.

Favorite
user: Foreign key to UserData.
book: Foreign key to Book.
added_at: Timestamp when the book was added to favorites.

Recommendation
user: Foreign key to UserData.
recommended_books: Many-to-many relationship with Book.
recommended_at: Timestamp when recommendations were made.

NotifyMessage
user: Foreign key to UserData.
message: Notification message.
url: Optional URL related to the message.
date: Timestamp when the message was created.
is_read: Boolean indicating if the message has been read.

Log
user_id: Foreign key to UserData.
action: Description of the action.
timestamp: Timestamp when the action occurred.
ip_address: IP address from which the action was performed.

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

