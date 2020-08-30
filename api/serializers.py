import uuid
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.response import Response
from.models import Collection, Movie, UserCollection


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username',  'password')


class MovieSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=True, read_only=False)

    class Meta:
        model = Movie
        fields = ('uuid', 'title', 'description', 'genres')
        extra_kwargs = {'genres': {'required': 'False'}}


class CollectionSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True, required=False)

    def create(self, validated_data):
        movies = validated_data.pop('movies', None)
        try:
            collection = Collection.objects.create(**validated_data)

            for movie in movies:
                create, _ = Movie.objects.get_or_create(**movie)
                collection.movies.add(create)
            return collection
        except Exception as e:
            return Response(e.args, status=status.HTTP_400_BAD_REQUEST)

    def update(self, instance_data, validated_data):

        movies = validated_data.get('movies')
        collection = instance_data.last()
        collection.title = validated_data.get('title')
        collection.description = validated_data.get('description')
        for movie in movies:
            movie_old = None
            movie_serialize = MovieSerializer(data=movie)
            try:
                movie_old = Movie.objects.get(uuid=movie.get('uuid'))
            except Exception as e:
                pass
            try:
                if movie_serialize.is_valid(raise_exception=True):
                    if movie_old:
                        movie = movie_serialize.update(movie_old, movie)
                    else:
                        movie = movie_serialize.save()
                collection.movies.add(movie)
            except Exception as e:
                return Response(e.args, status=status.HTTP_400_BAD_REQUEST)
        collection.save()

    class Meta:
        model = Collection
        fields = ('uuid', 'title', 'description', 'movies')
