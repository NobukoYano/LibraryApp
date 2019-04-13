# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Book(models.Model):
    ISBN = models.CharField(max_length = 30)
    BookName = models.CharField(max_length = 250)
    FrontPage = models.CharField (max_length = 400, default = 'static/no_frontpage.png')
    Author = models.CharField(max_length = 100,default = "unknown")
    Publisher = models.CharField(max_length = 100,default = "unknown")
    Quantity = models.IntegerField(default=1)
    Introduction = models.TextField()
    DatePublished = models.DateField(null=True, blank=True)
    DateRegistered = models.DateTimeField(auto_now_add=True)
    
     
    def get_absolute_urls(self): 
        return reverse(
            "books:detail", 
            kwargs={ 'pk': self.pk} 
        )

    def __str__(self):
        return self.BookName


class BorrowRecord(models.Model):
    Borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    BookBorrowed = models.ForeignKey(Book, null = True, on_delete = models.CASCADE)
    BeginTime = models.DateTimeField(auto_now_add=True)
    EndTime = models.DateField(null=True, blank=True)
    finished = models.BooleanField(default = False)
    def __str__(self):
        return self.Borrower.username + " borrowed " + self.BookBorrowed.BookName

