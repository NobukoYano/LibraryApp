from django.contrib import admin
from .models import Book, BorrowRecord

# Register your models here.
admin.site.register(Book)
admin.site.register(BorrowRecord)
