import os
import requests
from collections import Counter

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import api_view, permission_classes

from .redis import redis_obj
from .decorators import retry
from .pagination import CredyMoviesPagination
from .models import UserCollection, Collection, Movie
from .serializers import SignupSerializer, CollectionSerializer, MovieSerializer
from .utils import get_genres


class Signup(APIView):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    def post(self, request, format=None):
        UserModel = User
        serializer = self.serializer_class(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                return_dic = serializer.validated_data
                try:
                    created = UserModel.objects.create(**return_dic)
                    user_collection = UserCollection.objects.create(
                        user=created)
                    access = AccessToken.for_user(created)

                    tokens = {
                        'access_access': str(access.get('jti')),
                    }
                    return Response(data=tokens, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response(e.args, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response(e.detail, status=e.status_code)


class CollectionViewSet(ViewSet):
    queryset = Collection.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = CollectionSerializer

    def get_object(self, request, uuid):
        user = request.user
        collections = self.queryset.filter(
            usercollection__user=user, uuid=uuid)
        return collections

    # list of collection related to user
    def list(self, request):
        query_params = request.query_params
        query_set = self.queryset.filter(
            usercollection__user=request.user)
        if query_set.exists():
            genres = query_set.values_list('movies__genres', flat=True)
            genres = get_genres(genres)
            serialize = self.serializer_class(query_set, many=True)

            collections = []
            for collection in serialize.data:
                collection.pop('movies', None)
                collections.append(collection)
            genres = list(genres) if len(genres) < 4 else list(genres)[:3]
        else:
            collections = None
            genres = None

        context = {
            "is_success": True,
            "data": {
                "collections": collections,
                "faviourite_geners": genres
            }
        }
        return Response(context, status=status.HTTP_200_OK)

    # Create collection with movies
    def create(self, request):
        user = request.user
        data = request.data[0]
        try:
            collection = self.serializer_class(data=data)
            if collection.is_valid(raise_exception=True):
                collection = collection.save()
                uc, _ = UserCollection.objects.get_or_create(user=user)
                uc.collections.add(collection)
        except Exception as e:
            return Response(e.args, status=status.HTTP_400_BAD_REQUEST)
        return Response("Created Succesfully", status=status.HTTP_201_CREATED)

    # Retreive an object
    def retrieve(self, request, pk=None):
        collections = self.get_object(request, pk)
        if collections.exists():
            serialized = self.serializer_class(collections, many=True)
            return Response(serialized.data, status=status.HTTP_200_OK)
        return Response("Please Check uuid", status=status.HTTP_404_NOT_FOUND)

    # Update an object
    def update(self, request, pk=None):
        data = request.data[0]
        instance = self.get_object(request, pk)
        if instance.exists():
            serializer = self.serializer_class(instance.last(), data=data)
            try:
                if serializer.is_valid(raise_exception=True):
                    serializer.update(instance, serializer.validated_data)
                    return Response("Update Successfull", status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                return Response(e.args, status=status.HTTP_400_BAD_REQUEST)
        return Response("This collection is not your collection", status=status.HTTP_404_NOT_FOUND)

    # Delete an object
    def destroy(self, request, *args, **kwargs):
        collection = self.get_object(request, kwargs.get('pk', ''))
        if collection.exists():
            collection.delete()
            return Response("Delete Successfully", status=status.HTTP_204_NO_CONTENT)
        return Response("This collection is not your collection", status=status.HTTP_404_NOT_FOUND)


class MovieView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = MovieSerializer
    pagination_class = CredyMoviesPagination()

    def get(self, request, format=None):
        page = request.query_params.get('page', 1)
        query_set = Movie.objects.all()

        if query_set:
            page = self.pagination_class.paginate_queryset(
                query_set, page
            )
            serialize = MovieSerializer(page, many=True)
            return self.pagination_class.get_paginated_response(serialize.data)
        else:
            return Response("No Content", status=status.HTTP_204_NO_CONTENT)


@retry
def get_movies(url):
    username = settings.CLIENT_ID
    password = settings.CLIENT_SECRET
    try:
        response = requests.get(url, auth=(username, password))
    except Exception as e:
        response = None
    if response and response.status_code == status.HTTP_200_OK:
        return response.json()
    return {}


@api_view(['GET'])
@permission_classes([AllowAny, ])
def movie_view(request):
    page = int(request.query_params.get('page', 1))
    url = settings.CLIENT_URL + '?page=' + str(page)
    local_url = settings.LOCAL_URL
    response = get_movies(url)
    if response:
        if response['next']:
            next_page = page+1
            response['next'] = local_url + '?page=' + str(next_page)
        else:
            response['next'] = None

        if response['previous']:
            prev_page = page-1
            response['previous'] = local_url + '?page=' + str(prev_page) \
                if prev_page != 1 else local_url
        else:
            response['previous'] = None
    return Response(data=response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def request_count(request):
    count = 0
    count = redis_obj.get('counter')
    return Response(data={'requests': int(count)}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_count(request):
    count = redis_obj.set('counter', 0)
    return Response(data={'message': 'request count reset successfully'}, status=status.HTTP_200_OK)
