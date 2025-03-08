from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken , TokenError as JWTTokenError


from rest_framework_simplejwt.exceptions import AuthenticationFailed

from core.apis.serializers import BookSerializer, BorrowedBookSerializer, UserRegistrationSerializer
from core.models import Book, BorrowedBook, CustomUser
from library.permissions import IsAdminOrLibrarian, IsMember


'''
    USER REGISTERATION API(USER SHOULD REGISTER WITH USERNAME AND PASSWORD)
'''
class UserRegistrationApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        datas = request.data
        serializer = UserRegistrationSerializer(data = datas)
        if serializer.is_valid():
            serializer.save()
            return Response ({'message': 'Registration Sucessfull'}, status = status.HTTP_200_OK)  
        return Response({'error': serializer.errors}, status= status.HTTP_400_BAD_REQUEST)  



'''
    User can Login using respective username and password
'''

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"detail": "username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed("Invalid username.")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid password.")
        
        if not user.is_active:
            raise AuthenticationFailed("User account is not active.")
        
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'role' : user.role
        }, status=status.HTTP_200_OK)


'''
    THIS API WILL GIVE YOU REFRESH TOKEN
'''
class RefreshTokenApiview(APIView):
    
    def post (self, request):

        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token

            return Response({
                'access': str(new_access_token),
            }, status=status.HTTP_200_OK)

        except JWTTokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        

'''
    THIS IS BLOCK TOKEN API
'''
class LogoutApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class BookListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrLibrarian()]
        return [AllowAny()]
    
    def get(self, request):
        books = Book.objects.all().order_by('-created_at')
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminOrLibrarian()]

    def get_object(self, book_id):
        return get_object_or_404(Book, id=book_id)

    def get(self, request, book_id):
        book = self.get_object(book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, book_id):
        book = self.get_object(book_id)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, book_id):
        book = self.get_object(book_id)
        book.delete()
        return Response({"message": "Book deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class BorrowedBookListCreateAPIView(APIView):
    permission_classes = [IsMember]

    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        if book.available_copies < 1:
            return Response({"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST)

        borrowed_book = BorrowedBook.objects.create(
            user=request.user,
            book=book,
            due_date=request.data.get("due_date"),
        )
        
        book.available_copies -= 1  
        book.save()

        serializer = BorrowedBookSerializer(borrowed_book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BorrowedBookReturnAPIView(APIView):
    permission_classes = [IsMember]

    def post(self, request, book_id):

        borrowed_book = BorrowedBook.objects.filter(
            book_id = book_id , user = request.user
        ).order_by('created_at').first()

        if borrowed_book.returned:
            return Response({"message": "Book already returned"}, status=status.HTTP_400_BAD_REQUEST)

        borrowed_book.returned = True
        borrowed_book.save()

        book = borrowed_book.book
        book.available_copies += 1
        book.save()

        return Response({"message": "Book returned successfully"})
