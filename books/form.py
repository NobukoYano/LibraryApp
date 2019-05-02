from django import forms
from django.contrib.auth.models import User

from .models import Book


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    school_ID = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


# class BorrowRecordForm(forms.ModelForm):

#    class Meta:
#        model = BorrowRecord
#        fields = ['BookBorrowed']

class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = [
            'isbn',
            'title',
            'cover_url',
            'author',
            'publisher',
            'pubdate',
            ]
