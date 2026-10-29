
from django.contrib import admin
from .models import TrendingTopic


@admin.register(TrendingTopic)
class TrendingTopicAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "trend_score",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "is_active")
    search_fields = ("title", "summary")
    list_editable = ("trend_score", "is_active")
    readonly_fields = ("created_at",)
    prepopulated_fields = {"slug": ("title",)}
