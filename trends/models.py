
from django.db import models
from django.utils.text import slugify


class TrendingTopic(models.Model):
    CATEGORY_CHOICES = [
        ("India", "India"),
        ("World", "World"),
        ("Technology", "Technology"),
        ("Business", "Business"),
        ("Sports", "Sports"),
        ("Entertainment", "Entertainment"),
        ("Weather", "Weather"),
        ("Science", "Science"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="India",
    )
    summary = models.TextField()
    trend_score = models.PositiveSmallIntegerField(default=50)
    source_url = models.URLField(blank=True)
    image_url = models.URLField(max_length=1000, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "topic"
            candidate = base_slug
            number = 2

            while TrendingTopic.objects.filter(
                slug=candidate
            ).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{number}"
                number += 1

            self.slug = candidate

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
