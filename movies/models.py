from django.db import models
from django.core.exceptions import ValidationError
import re

class Movie(models.Model):
    """Movie model with trailer information"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    poster_url = models.URLField(blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-release_date']


class TrailerLog(models.Model):
    """Log trailer access and errors for monitoring"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='trailer_logs')
    url = models.URLField()
    is_valid = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie.title} - {self.created_at}"