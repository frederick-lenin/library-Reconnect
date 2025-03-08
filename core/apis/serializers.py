from rest_framework import serializers
from django.contrib.auth.hashers import check_password, make_password
from core.models import Book, BorrowedBook, CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'role')

    def create(self, data):
        try:    
            username = data['username']
            password = data['password']
            role = data['role']
            hashedpassword = make_password(password) 
            user= CustomUser.objects.create(
                username = username,
                password = hashedpassword,
                role = role
            )
            return user
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})
        
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class BorrowedBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = BorrowedBook
        fields = '__all__'