
import random

from django.shortcuts import render
from django.db.models import Q
from .models import TrendingTopic


def home(request):
    topics = TrendingTopic.objects.filter(is_active=True)

    category = request.GET.get("category", "").strip()
    search_query = request.GET.get("q", "").strip()

    if category:
        topics = topics.filter(category=category)

    if search_query:
        topics = topics.filter(
            Q(title__icontains=search_query)
            | Q(summary__icontains=search_query)
        )

    topics = topics.order_by("-created_at")

    # Select 50 random featured news articles with images.
    featured_pool = list(
        TrendingTopic.objects.filter(
            is_active=True,
            image_url__gt="",
        ).order_by("-created_at")[:50]
    )

    featured_news = random.sample(
        featured_pool,
        min(50, len(featured_pool)),
    )

    categories = TrendingTopic.CATEGORY_CHOICES

    context = {
        "topics": topics,
        "categories": categories,
        "selected_category": category,
        "search_query": search_query,
        "featured_news": featured_news,
    }

    return render(request, "trends/home.html", context)
