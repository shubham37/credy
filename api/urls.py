from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from .views import Signup, movie_view, request_count,\
    reset_count, CollectionViewSet, MovieView


credy_router = DefaultRouter()

urlpatterns = [
    url(r'^register/$', Signup.as_view(), name='register'),
    url(r'^request_count/$', request_count, name='request_count'),
    url(r'^request_count/reset/$', reset_count, name='reset_count'),
    url(r'^external_movies/$', MovieView.as_view(), name='internal_movie'),
    url(r'^movies/$', movie_view, name='external_movie')
]

credy_router.register(r'collection', CollectionViewSet)

urlpatterns += credy_router.urls
