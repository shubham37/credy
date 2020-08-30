from django.contrib import admin
from .models import Movie, Collection, UserCollection

# Register your models here.
admin.site.register(Movie)
admin.site.register(Collection)
admin.site.register(UserCollection)
