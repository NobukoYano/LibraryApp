# from django.views import generic
# from django.views.generic.edit import CreateView, UpdateView, DeleteView
# from django.contrib.auth.models import User
# from django.http import HttpResponse, Http404
# from django.shortcuts import render, get_object_or_404
# from django.urls import reverse, reverse_lazy
# import urllib.request
# from PIL import Image
# import os
# from django.core.files import File

from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.core.files.base import ContentFile
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date

from .models import Book, BorrowRecord
from .form import UserForm, BookForm
from . import openbd


# Create your views here.

all_book = Book.objects.all()


def top(request):
    # ToDo filter books
    books = Book.objects.all()

    return render(request, 'book/top.html', {'books': books})


@login_required(login_url='/accounts/login/')
def index(request):
    books = Book.objects.all()
    query = request.GET.get("q")
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(publisher__icontains=query)
        ).distinct()
        books.filter(~Q(quantity=0))
        return render(request, 'book/homepage.html', {
            'books': books,
        })
    else:
        # books = Book.objects.filter(~Q(quantity = 0))
        books = Book.objects.all()
        return render(request, 'book/homepage.html', {'books': books})


# def Detail(request,book_id):
#     if not request.user.is_authenticated:
#         return HttpResponseRedirect('book/login')
#     else:
#         book = get_object_or_404(Book, pk=book_id)
#         context = {
#             'book' : book,
#         }
#         return render(request,'book/item.html',context)


@login_required(login_url='/accounts/login/')
def create_book(request):
    form = BookForm(request.POST or None, request.FILES or None)
    # info = request.POST.copy()
    if form.is_valid():
        # print(info)
        # print(info.__getitem__('isbn'))
        book = form.save(commit=False)

        # ToDo revise the condition for count up
        thisISBN = book.isbn
        existingISBN = Book.objects.filter(isbn=thisISBN)
        existingTitle = Book.objects.filter(title=book.title)
    
        if existingISBN.count() > 0:
            existingbook = existingISBN[0]
            existingbook.quantity += 1
            existingbook.save()

            messages.success(
                request, 'The book ' +
                '{} was successfully counted up!'.format(book.title))

            return HttpResponseRedirect('/books')
    
        if existingTitle.count() > 0:
            existingbook = existingTitle[0]
            existingbook.quantity += 1
            existingbook.save()
            return HttpResponseRedirect('/books')
            # save the image front internet

        # Get image file from external url
        response = requests.get(book.cover_url)
        filename = str(book.id) + '_frontpage.jpg'
        book.cover_image.save(filename, ContentFile(response.content),
                              save=True)

        book.save()

        messages.success(request, 'The book ' +
                         '{} was successfully added!'.format(book.title))

        return HttpResponseRedirect('/books')
    else:
        # If form is not fulfilled
        return render(request, 'book/add_book.html')


@login_required(login_url='/accounts/login/')
def BorrowBook(request, book_id):
    """borrowed a book"""
    borrowRecords = BorrowRecord.objects.filter(
        Borrower=request.user
        ).filter(finished=False)
    
    # Limited the number to borrow a same book
    # if borrowRecords.count() > 4:
    #     return HttpResponseRedirect('/books')
    
    borrowed_books = set()
    for record in borrowRecords:
        borrowed_books.add(record.BookBorrowed.pk)
    if book_id in borrowed_books:
        messages.warning(request, 'You have already borrowed this book.')
        return HttpResponseRedirect('/books')

    user = request.user
    book = Book.objects.get(pk=book_id)
    record = BorrowRecord(Borrower=request.user, BookBorrowed=book)
    if book.quantity >= 1:
        book.quantity -= 1
        book.save()
        record.save()
        messages.success(request, 'You have borrowed ' +
                         '{} !'.format(book.title))
        return HttpResponseRedirect("/books/%d/borrowed" % user.id)
    else:
        # not used the book can't be borrowed if quantity = 0.
        messages.warning(request, 'This book is unavailable now.')
        return HttpResponseRedirect('/books')


@login_required(login_url='/accounts/login/')
def returnBook(request, book_id):
    borrowRecords = BorrowRecord.objects.filter(Borrower=request.user)
    borrowed_books_id = set()
    for record in borrowRecords:
        borrowed_books_id.add(record.BookBorrowed.pk)
    # borrowed_books = Book.objects.filter(pk__in=borrowed_books_id)

    if book_id not in borrowed_books_id:
        return HttpResponseRedirect('/books/%d/borrowed' % request.user.id)
    else:
        # print('success')
        thisRecord = BorrowRecord.objects.filter(
            Borrower=request.user,
            BookBorrowed=Book.objects.get(id=book_id)
            ).filter(finished=False)

        thisRecord = thisRecord[0]
        source = Book.objects.get(id=thisRecord.BookBorrowed.id)
        source.quantity += 1
        source.save()

        thisRecord.EndTime = date.today()
        thisRecord.finished = True
        thisRecord.save()

        messages.success(request, 'You have returned ' +
                         '{} !'.format(source.title))

        return HttpResponseRedirect('/books/%d/borrowed' % request.user.id)


@login_required(login_url='/accounts/login/')
def borrowed(request, user_id):
    books = Book.objects.all()
    query = request.GET.get("q")
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(publisher__icontains=query)
        ).distinct()
        books.filter(~Q(quantity=0))
        return render(request, 'book/homepage.html', {
            'books': books,
        })
    else:
        borrowRecords = BorrowRecord.objects.filter(
            Borrower=request.user
            ).filter(finished=False)
        borrowed_books = set()

        for record in borrowRecords:
            borrowed_books.add(record.BookBorrowed.pk)

        borrowed_books = Book.objects.filter(pk__in=borrowed_books)

        return render(request, 'book/borrowed.html',
                      {'books': borrowed_books})


def register(request):

    form = UserForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        login(request, user)
        return HttpResponseRedirect('/books')

    return render(request, 'book/register.html', {'form': form})

# def devoterlist(request):
#    if not request.user.is_authenticated:
#        return HttpResponseRedirect("/books/login")
#    else:
#        context = {
#            'all_records': DevoteRecord.objects.all(),
#        }
#        return render(request,'book/devote.html',context)


def search(request):
    if request.method == 'GET':
        isbn = request.GET.get('isbn', False)

        isbn = isbn.replace('-', '')

        if not isbn.isdigit() or len(isbn) != 13:
            messages.warning(
                request, 'The isbn code should be 13 digits'
                )
            return render(request, 'book/add_book.html')

        api = openbd.openBD()
        data = api.get_json(isbn)

        if data is None:
            messages.warning(request, 'The book was not found!')
            return render(request, 'book/add_book.html')

        form = BookForm({
            'isbn': data['isbn'],
            'title': data['title'],
            'cover_url': data['cover'],
            'author': data['author'],
            'publisher': data['publisher'],
            'pubdate': data['pubdate'],
            })
        return render(request, 'book/confirm_book.html',
                      {'form1': form, 'cover_url': data['cover']})


def create_book_manually(request):
    f = BookForm()
    return render(request, 'book/add_book_manually.html', {'BookForm': f})


def confirm_book(request):
    print('book confirm')
    return HttpResponseRedirect("/books")


def howto(request):
    return render(request, 'book/howto.html')


def ownedbooks(request):
    return render(request, 'book/ownedbooks.html')
