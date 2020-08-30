import uuid
from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=True)
    title = models.CharField(max_length=256)
    description = models.TextField()
    genres = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return str(self.uuid)

    class Meta:
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'


class Collection(models.Model):
    uuid = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=256, unique=True)
    description = models.TextField()
    movies = models.ManyToManyField(Movie)

    def __str__(self):
        return str(self.uuid)

    class Meta:
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'


class UserCollection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collections = models.ManyToManyField(Collection)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        verbose_name = 'UserCollection'
        verbose_name_plural = 'UserCollections'
