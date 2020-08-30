from collections import Counter


def get_genres(query_set):
    genres = []
    for genre in query_set:
        if genre:
            genres.extend(str(genre).split(','))
    if genres:
        genres = dict(sorted(dict(Counter(genres)).items(),
                             key=lambda x: x[1], reverse=True)).keys()
    return genres
