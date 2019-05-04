from . import views
from django.urls import path

app_name = "books"

urlpatterns = [
    path('', views.index, name='homepage'),
    path('add', views.create_book, name="book-add"),
    path('register', views.register, name='register'),
#    path('login', views.login_user, name='login'),
#    path('logout', views.logout_user, name='logout'),
    path('<int:book_id>/borrow', views.borrowBook, name='borrow'),
    path('<int:book_id>/return', views.returnBook, name='return'),
    path('<int:book_id>/delete', views.deleteBook, name='delete'),
    path('<int:user_id>/borrowed', views.borrowed, name='borrowed'),
    path('search', views.search, name='search'),
    path('addmanually', views.create_book_manually, name="book-addman"),
    path('confirm', views.confirm_book, name="confirm"),
    path('howto', views.howto, name="howto"),
    path('<int:user_id>/ownedbooks', views.ownedbooks, name="ownedbooks"),

#    path('devoterlist',views.devoterlist,name = 'devoter')
    ]
