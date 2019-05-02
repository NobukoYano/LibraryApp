from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Book


class UserForm(UserCreationForm):
    # password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
#            'password'
            ]


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
