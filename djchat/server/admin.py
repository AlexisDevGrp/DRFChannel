from django.contrib import admin

# Register your models here.
from .models import Channel, Server, Category

admin.site.register(Channel)
admin.site.register(Server)
admin.site.register(Category)