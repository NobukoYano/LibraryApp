# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
class Book(models.Model):
    CHOICES = (
        (11, 'Tokyo'),
        (12, 'Osaka'),
        (13, 'Fukuoka'),
        (21, 'Berlin'),
        (22, 'Hamburg'),
    )

    isbn = models.CharField(max_length=30)
    title = models.CharField(max_length=250)
    cover_url = models.URLField(blank=True)
    cover_image = models.ImageField(upload_to='images/')
    author = models.CharField(max_length=100, default="unknown")
    publisher = models.CharField(max_length=100, default="unknown")
    quantity = models.IntegerField(default=1)
    pubdate = models.CharField(max_length=20)
    regdate = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.IntegerField(
        choices=CHOICES,
        default=21
    )

    def get_absolute_urls(self):
        return reverse(
            "books:detail",
            kwargs={'pk': self.pk}
        )

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    Borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    BookBorrowed = models.ForeignKey(Book, null=True, on_delete=models.CASCADE)
    BeginTime = models.DateTimeField(auto_now_add=True)
    EndTime = models.DateField(null=True, blank=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return self.Borrower.username + " borrowed " + self.BookBorrowed.title
