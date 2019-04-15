from django import forms
from django.contrib.auth.models import User

from .models import Book,BorrowRecord



class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    school_ID = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


#class BorrowRecordForm(forms.ModelForm):

#    class Meta:
#        model = BorrowRecord
#        fields = ['BookBorrowed']

class BookForm(forms.ModelForm):
    #ISBN = forms.CharField()
    #BookName = forms.CharField()
    #FrontPage = forms.CharField()
    #Author = forms.CharField()
    #Publisher = forms.CharField()
    #DatePublished = forms.DateField()

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