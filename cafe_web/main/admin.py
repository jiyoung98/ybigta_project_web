from django.contrib import admin

# Register your models here.
from .models import Loc,Cafe,Review

admin.site.register(Loc)
admin.site.register(Cafe)
admin.site.register(Review)