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
from django.core.mail import EmailMessage

from .models import Book, BorrowRecord
from .form import UserForm, BookForm
from . import openbd
from . import rakutenapi


# Create your views here.

all_book = Book.objects.all()


def query_borrowed(user_id):
    books = Book.objects.all()
    

def query_book(query):
    books = Book.objects.all()
    books = books.filter(
        Q(title__icontains=query) |
        Q(author__icontains=query) |
        Q(publisher__icontains=query)
    ).distinct()
    # books.filter(~Q(quantity=0))
    return books


def top(request):
    # ToDo filter books
    books = Book.objects.all()

    return render(request, 'book/top.html', {'books': books})


@login_required(login_url='/')
def index(request):
    query = request.GET.get("q")
    if query:
        books = query_book(query)
        return render(request, 'book/homepage.html', {
            'books': books,
        })
    else:
        # books = Book.objects.filter(~Q(quantity = 0))
        # books = Book.objects.all()
        books = Book.objects.order_by('-regdate')[:20]
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

        # If same isbn & owner, count up
        thisISBN = book.isbn
        existingISBN = Book.objects.filter(isbn=thisISBN, owner=request.user)
        # existingTitle = Book.objects.filter(title=book.title)
        if existingISBN.count() > 0:
            existingbook = existingISBN[0]
            existingbook.quantity += 1
            existingbook.save()

            messages.success(
                request, 'The book ' +
                '{} was successfully counted up!'.format(book.title))

            return HttpResponseRedirect('/books')
    
        book.owner = request.user
        book.save()

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
def borrowBook(request, book_id):
    """borrowed a book"""
    borrowRecords = BorrowRecord.objects.filter(
        Borrower=request.user
        ).filter(finished=False)
    
    # Limited the number to borrow a same book
    if borrowRecords.count() > 4:
        messages.warning(request, "You have already borrowed 5 books.")
        return HttpResponseRedirect('/books')
    
    borrowed_books = set()
    for record in borrowRecords:
        borrowed_books.add(record.BookBorrowed.pk)
    if book_id in borrowed_books:
        messages.warning(request, 'You have already borrowed this book.')
        return HttpResponseRedirect('/books')

    user = request.user
    book = Book.objects.get(pk=book_id)

    if book.owner == request.user:
        messages.warning(request, "You cant't borrow your own book.")
        return HttpResponseRedirect('/books')

    record = BorrowRecord(Borrower=request.user, BookBorrowed=book)
    if book.quantity >= 1:
        book.quantity -= 1
        book.save()
        record.save()

        email = EmailMessage(
            '{} has borrowed {}'.format(request.user.first_name, book.title),
            '*** This is automatically generated email, please do not reply ***\n',
            to=[book.owner.email,],
            cc=[request.user.email,],
        )
        email.send()

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

        email = EmailMessage(
            '{} has returned {}'.format(request.user.first_name, source.title),
            '*** This is automatically generated email, please do not reply ***\n',
            to=[source.owner.email,],
            cc=[request.user.email,],
        )
        email.send()

        messages.success(request, 'You have returned ' +
                         '{} !'.format(source.title))

        # return render(request, 'book/borrowed.html',
        #           {'books': borrowed_books})
        print('here')
        return HttpResponseRedirect('/books/%d/borrowed' % request.user.id)


@login_required(login_url='/accounts/login/')
def borrowed(request, user_id):
    books = Book.objects.all()
    query = request.GET.get("q")
    if query:
        books = query_book(query)

    borrowRecords = BorrowRecord.objects.filter(
        Borrower=request.user
        ).filter(finished=False)
    
    borrowed_books_id = set()

    for record in borrowRecords:
        borrowed_books_id.add(record.BookBorrowed.pk)

    borrowed_books = books.filter(pk__in=borrowed_books_id)

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


@login_required(login_url='/accounts/login/')
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

        # if openBD data is None or cover of openBD is blank
        if data is None or data['cover'] == '':
            rakuten_api = rakutenapi.rakuten()
            data = rakuten_api.get_json(isbn)

        # if data is None
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
            'location': 21,
            })
        return render(request, 'book/confirm_book.html',
                      {'form': form, 'cover_url': data['cover']})


@login_required(login_url='/accounts/login/')
def create_book_manually(request):
    f = BookForm()
    return render(request, 'book/confirm_book.html', {'form': f})
    # return render(request, 'book/add_book_manually.html', {'form': f})


@login_required(login_url='/accounts/login/')
def confirm_book(request):
    print('book confirm')
    return HttpResponseRedirect("/books")


def howto(request):
    return render(request, 'book/howto.html')


@login_required(login_url='/accounts/login/')
def ownedbooks(request, user_id):
    books = Book.objects.all()
    query = request.GET.get("q")
    if query:
        books = query_book(query)

    owned_books = books.filter(owner=user_id)

    return render(request, 'book/ownedbooks.html',
                      {'books': owned_books})


@login_required(login_url='/accounts/login/')
def deleteBook(request, book_id):
    books = Book.objects.filter(pk=book_id, owner=request.user) 
    if books is None:
        messages.warning("The book was not found.")

    if books[0].quantity == 0:
        messages.warning("The book was not found.")

    elif books[0].quantity >= 2:
        book = books[0]
        book.quantity -= 1
        book.save()
        messages.success(
            request,
            "One of the books '{}' was deleted.".format(book.title)
            )
    else:
        book = books[0]
        book.delete()
        messages.success(
            request,
            "The book '{}' was fully deleted.".format(book.title)
            )
    return HttpResponseRedirect("/books/"+str(request.user.id)+"/ownedbooks")


@login_required(login_url='/accounts/login/')
def borrow_req(request, book_id):
    books = Book.objects.filter(pk=book_id)

    email = EmailMessage(
        'Borrow Request for {}'.format(books[0].title),
        'Hi, \nI would like to borrow this book.\n' +
        'Please contact me just replying this email! \n\n' +
        '  book : {} \n'.format(books[0].title) +
        '  Name : {} {} \n'.format(request.user.last_name, request.user.first_name) +
        '  email : {} \n\n'.format(request.user.email) +
        'Best, \nBiblio Team',
        to=[books[0].owner.email,],
        reply_to=[request.user.email,],
        cc=[request.user.email,],
    )
    email.send()

    # subject = 'Borrow Request for {}'.format(books[0].title)
    # body = 'Hi, I would like to borrow this book./n' +
    #        'Please contact me! /n' +
    #        'Name : {} {}'.format(request.user.last_name, request.user.first_name) +
    #        'email : {}'.format(request.user.email)
    # sender = request.user.email
    # receiver = [books[0].owner.email,]
    # send_mail(subject, body, sender, receiver)
    messages.success(
            request,
            "You have sent an email to borrow '{}' owned by {}."
            .format(books[0].title, books[0].owner.first_name)
            )
    return HttpResponseRedirect("/books/")


@login_required(login_url='/accounts/login/')
def return_req(request, book_id):
    books = Book.objects.filter(pk=book_id)

    email = EmailMessage(
        'Return Request for {}'.format(books[0].title),
        'Hi, \nThanks for lending me this book. I would like to return it.\n' +
        'Please contact me just replying this email! \n\n' +
        '  book : {} \n'.format(books[0].title) +
        '  Name : {} {} \n'.format(request.user.last_name, request.user.first_name) +
        '  email : {} \n\n'.format(request.user.email) +
        'Best, \nBiblio Team',
        to=[books[0].owner.email,],
        reply_to=[request.user.email,],
        cc=[request.user.email,],
    )
    email.send()

    messages.success(
            request,
            "You have sent an email to return '{}' owned by {}."
            .format(books[0].title, books[0].owner.first_name)
            )
    return HttpResponseRedirect("/books/"+str(request.user.id)+"/borrowed")