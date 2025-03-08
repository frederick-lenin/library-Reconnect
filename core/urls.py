from django.urls import path

from core.apis.apis import BookDetailAPIView, BookListCreateAPIView, BorrowedBookListCreateAPIView, BorrowedBookReturnAPIView, LoginAPIView, LogoutApi, RefreshTokenApiview, UserRegistrationApiView


urlpatterns = [
    path('registration/', UserRegistrationApiView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('RefreshTokenApiview/', RefreshTokenApiview.as_view()),
    path('LogoutApi/', LogoutApi.as_view()),

    #Books add put delete
    path('books/', BookListCreateAPIView.as_view(), name='book-list-create'),
    path('books/<int:book_id>/', BookDetailAPIView.as_view(), name='book-detail'),
    path('books/<int:book_id>/', BookDetailAPIView.as_view(), name='book-delete'),

    #Book Borrow
    path('borrow/<int:book_id>/', BorrowedBookListCreateAPIView.as_view(), name = 'borrow-books'),
    path("return/<int:book_id>/", BorrowedBookReturnAPIView.as_view(), name='return-books')
]