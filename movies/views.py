from django.shortcuts import render, get_object_or_404
from .models import Movie


def movie_list(request):
    """
    Display all movies
    """
    movies = Movie.objects.all()

    context = {
        'movies': movies
    }

    return render(request, 'movies/movie_list.html', context)


def movie_detail(request, movie_id):
    """
    Display details for a single movie
    """
    movie = get_object_or_404(Movie, pk=movie_id)

    context = {
        'movie': movie
    }

    return render(request, 'movies/movie_detail.html', context)