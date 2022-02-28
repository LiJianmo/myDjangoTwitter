from django.contrib import admin
from newsfeeds.models import NewsFeed

# Register your models here.
@admin.register(NewsFeed)
class TweetAdmin(admin.ModelAdmin):
    data_hierarchy = "created_at"
    list_display = (
        "created_at",
        "user",
        "tweet",
    )