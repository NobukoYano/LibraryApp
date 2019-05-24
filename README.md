# LibraryApp

Manage books online. 
Runs on django 2.2 and some little tools.

# Usage

The environment is already built in the myvenv, you can run 
```pip install virtualenv```
```cd [the project repo] ```
```source myvenv/Script/activate ```
to start the virtualenv, then run 
```python manage.py runserver ``` 
to start the service, the web runs on **127.0.0.1:8000/books** as default

to entry admin page, use 
```python manage.py createsuperuser```

# Static Files
css, js and pics
they are stored in 

./books/static


# Features
**1. Add a book** 
you can add your book 
 - enter isbn code and search (extract infos from openbd API) or 
 - enter all information manually.

**2. Borrow a book**
you can borrow a book if it's available. 
you can also see all of borrowed books on My Bookshelf and return it.
