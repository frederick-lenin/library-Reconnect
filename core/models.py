from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'admin'),
        ('librarian', 'librarian'),
        ('member', 'member')
    ]
    
    role = models.CharField(max_length=9, choices=ROLE_CHOICES, default='member')

    class Meta:
        verbose_name_plural = 'Users'

    def clean(self):
        if CustomUser.objects.exclude(pk=self.pk).filter(username=self.username).exists():
            raise ValidationError({'username': 'Username already exists'})
        super().clean()

class Book(TimestampModel):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField(null=True, blank=True)
    pages = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()
    
    def __str__(self):
        return self.title

class BorrowedBook(TimestampModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
