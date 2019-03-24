from django.contrib import admin
from rango.models import Category, Page
# Register your models here.

class PageAdmin(admin.ModelAdmin):
    list_display=['title','category','url']

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    list_display=['name','slug']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page,PageAdmin)
