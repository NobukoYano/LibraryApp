from django.shortcuts import render , HttpResponseRedirect
from django.views import generic
from .models import *
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from .form import UserForm, BookForm
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login,logout
from django.db.models import Q
from . import openbd

import urllib.request 
from PIL import Image
import os
from django.core.files import File
from django.core.files.base import ContentFile
import requests
from django.contrib import messages


# Create your views here.
 
all_book = Book.objects.all()


def index_guest(request):
    # ToDo filter books
    books = Book.objects.all()

    return render(request, 'book/homepage_guest.html', {'books': books})


def index(request):
    if not request.user.is_authenticated:
        books = Book.objects.all()
        return HttpResponseRedirect('/books/login')
    else:
        books = Book.objects.all()
        query = request.GET.get("q")
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(publisher__icontains=query)
            ).distinct()
            books.filter(~Q(quantity = 0))
            return render(request, 'book/homepage.html', {
                'books': books,
            })
        else:
            #books = Book.objects.filter(~Q(quantity = 0))
            books = Book.objects.all()
            return render(request, 'book/homepage.html', {'books': books})

def logout_user(request):
    if not request.user.is_authenticated:
        return render(request, 'book/login.html', {'error_message' :'Please login'})
    else:
        logout(request)
        return HttpResponseRedirect('/books')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            books = Book.objects.all()
            context = {
                'books' : books
            }
            return HttpResponseRedirect('/books')
        else :
            return render(request, 'book/login_u.html',{'error_message' : "Please sign up"} )
    else:
        return render(request, 'book/login_u.html')


# def Detail(request,book_id):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect('book/login')
#     else:
#         book = get_object_or_404(Book, pk=book_id)
#         context = {
#             'book' : book,
#         }
#         return render(request,'book/item.html',context)
    


def create_book(request):
    if not request.user.is_authenticated: 
        return HttpResponseRedirect('book/login')
    else:
        form = BookForm(request.POST or None, request.FILES or None)
        info = request.POST.copy()
        if form.is_valid():
            #print(info)
            #print(info.__getitem__('isbn'))
            book = form.save(commit=False)

            thisISBN = book.isbn
            existingISBN = Book.objects.filter(isbn = thisISBN)
            existingTitle = Book.objects.filter(title = book.title)
            if existingISBN.count() > 0:
                existingbook = existingISBN[0]
                existingbook.quantity += 1
                existingbook.save()
                return HttpResponseRedirect('/books')
            if existingTitle.count() > 0:
                existingbook = existingTitle[0]
                existingbook.quantity += 1
                existingbook.save()
                return HttpResponseRedirect('/books')
            # save the image front internet
            book.save()
            response = requests.get(book.cover_url)
            filename = str(book.id) + '_frontpage.jpg'
            book.cover_image.save(filename, ContentFile(response.content), save=True)
            #book.cover_image.save(
            #    os.path.basename(book.cover_url),
            #    File(open(data[0], encoding="utf-8_sig"))
            #    )

            book.save()

            messages.success(request, 'The book {} was successfully added!'.format(book.title)) 

            return HttpResponseRedirect('/books')
        #context = {
        #    "form": form,
        #    "all_user" : User.objects.all(),
        #}
        #return render(request, 'book/add_book.html', context)
        return render(request, 'book/add_book.html')



def BorrowBook(request, book_id):
    if not request.user.is_authenticated:
        return render(request , 'book/login.html' ,{ 'error_message' : "You need to login"} )
    else:    

        borrowRecords = BorrowRecord.objects.filter( Borrower = request.user ).filter(finished = False)
        if borrowRecords.count() > 4:
            return HttpResponseRedirect('/books')
        borrowed_books = set()
        for record in borrowRecords:
            borrowed_books.add(record.BookBorrowed.pk)
        if book_id in borrowed_books:
            messages.warning(request, 'You have already borrowed this book.') 
            return HttpResponseRedirect('/books')
        
        user = request.user
        book = Book.objects.get(pk=book_id)
        record = BorrowRecord(Borrower=request.user,BookBorrowed = book)
        if book.quantity >= 1:
            book.quantity -= 1
            book.save()
            record.save() 
            return HttpResponseRedirect("/books/%d/borrowed" % user.id)
        else:
            return Http404


def returnBook(request, book_id):
    if not request.user.is_authenticated:
        return render(request , 'books/login.html' ,{ error_message : "Please login first"} )
    else:
        borrowRecords = BorrowRecord.objects.filter( Borrower = request.user)
        borrowed_books_id = set()
        for record in borrowRecords:
            borrowed_books_id.add(record.BookBorrowed.pk)
        borrowed_books = Book.objects.filter(pk__in = borrowed_books_id)
        if book_id not in borrowed_books_id:
            return HttpResponseRedirect('/books/%d/borrowed' % request.user.id)
        else:
            print('success')
            thisRecord = BorrowRecord.objects.filter(Borrower = request.user , BookBorrowed = Book.objects.get(id = book_id)).filter(finished = False)
            thisRecord = thisRecord[0]
            source = Book.objects.get(id = thisRecord.BookBorrowed.id)
            source.quantity += 1
            source.save()
            
            thisRecord.finished = True
            thisRecord.save()

            return HttpResponseRedirect('/books/%d/borrowed' % request.user.id)


def borrowed(request,user_id):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect("/books/login")
    else:
        books = Book.objects.all()
        query = request.GET.get("q")
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(publisher__icontains=query)
            ).distinct()
            books.filter(~Q(quantity = 0))
            return render(request, 'book/homepage.html', {
                'books': books,
            })
        else:
            borrowRecords = BorrowRecord.objects.filter( Borrower = request.user ).filter(finished = False)
            borrowed_books = set()

            for record in borrowRecords:
                borrowed_books.add(record.BookBorrowed.pk)

            borrowed_books = Book.objects.filter(pk__in = borrowed_books)

            return render(request , 'book/borrowed.html' , {'books': borrowed_books})
        


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # borrowed_books = Book.objects.filter(user=request.user)
                return render(request, 'book/homepage.html', {'books': Book.objects.all()})
    context = {
        "form": form,
    }
    return render(request, 'book/register.html', context)

#def devoterlist(request):
#    if not request.user.is_authenticated:
#        return HttpResponseRedirect("/books/login")
#    else:
#        context = {
#            'all_records': DevoteRecord.objects.all(),
#        }
#        return render(request,'book/devote.html',context)


def search(request):
    if request.method == 'GET':
        isbn = request.GET.get('isbn',False)

        isbn.replace('-','')
        if not isbn.isdigit() or len(isbn) != 13:
            messages.warning(request, 'The isbn code should be 13 digits (without hyphen)') 
            return render(request, 'book/add_book.html')

        api = openbd.openBD()
        data = api.get_json(isbn)

        if data == None:
            messages.warning(request, 'The book was not found!') 
            return render(request, 'book/add_book.html')

        form = BookForm({
            'isbn':data['isbn'],
            'title':data['title'],
            'cover_url':data['cover'],
            'author':data['author'],
            'publisher':data['publisher'],
            'pubdate':data['pubdate'],        
            })
        return render(request, 'book/confirm_book.html', {'form1': form, 'cover_url': data['cover']})


def create_book_manually(request):
    f = BookForm()
    return render(request, 'book/add_book_manually.html', {'BookForm':f})


def confirm_book(request):
    print('book confirm')
    return HttpResponseRedirect("/books")

def howto(request):
    return render(request, 'book/howto.html')


def ownedbooks(request):
    return render(request, 'book/ownedbooks.html')
