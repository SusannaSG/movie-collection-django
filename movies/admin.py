from django.contrib import admin
from .models import Movie, TrailerLog

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'has_trailer')
    search_fields = ('title',)
        
    def has_trailer(self, obj):
        return bool(obj.trailer_url)
    has_trailer.short_description = 'Has Trailer'
    has_trailer.boolean = True

@admin.register(TrailerLog)
class TrailerLogAdmin(admin.ModelAdmin):
    list_display = ('movie', 'is_valid', 'created_at')
    list_filter = ('is_valid',)
    readonly_fields = ('created_at',)