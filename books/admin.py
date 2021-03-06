from django.contrib import admin
from .models import Book, BorrowRecord

# Register your models here.


class BookAdmin(admin.ModelAdmin):
    readonly_fields = ('regdate',)
    list_display=['get_location_display']


class BorrowRecordAdmin(admin.ModelAdmin):
    readonly_fields = ('BeginTime',)


admin.site.register(Book, BookAdmin)
admin.site.register(BorrowRecord, BorrowRecordAdmin)
