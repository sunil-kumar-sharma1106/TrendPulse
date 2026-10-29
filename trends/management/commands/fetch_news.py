import re
import feedparser

from django.core.management.base import BaseCommand
from django.utils.html import strip_tags
from html import unescape
from django.utils.text import slugify

from trends.models import TrendingTopic


RSS_FEEDS = [
    ("India", "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"),
    ("World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("Sports", "https://feeds.bbci.co.uk/sport/rss.xml"),
]


def extract_image_url(entry):
    """Extract an image URL from common RSS image fields."""
    def upgrade_image_url(url):
    """Request a higher-resolution BBC image when available."""
    if not url:
        return ""

    url = url.strip()

    # Upgrade BBC image URLs to a larger resolution.
    url = re.sub(
        r"/ace/standard/\d+/",
        "/ace/standard/1024/",
        url,
    )

    return urldef upgrade_image_url(url):
    """Request a higher-resolution BBC image when available."""
    if not url:
        return ""

    url = url.strip()

    # Upgrade BBC image URLs to a larger resolution.
    url = re.sub(
        r"/ace/standard/\d+/",
        "/ace/standard/1024/",
        url,
    )

    return url

    # 1. RSS media:content
    for media in entry.get("media_content", []):
        url = media.get("url", "").strip()
        if url.startswith(("https://", "http://")):
            return url

    # 2. RSS media:thumbnail
    for media in entry.get("media_thumbnail", []):
        url = media.get("url", "").strip()
        if url.startswith(("https://", "http://")):
            return url

    # 3. RSS enclosure links
    for enclosure in entry.get("enclosures", []):
        url = enclosure.get("href", "").strip()
        mime_type = enclosure.get("type", "")

        if url.startswith(("https://", "http://")) and (
            mime_type.startswith("image/") or
            re.search(r"\.(jpg|jpeg|png|webp|gif)(\?|$)", url, re.I)
        ):
            return url

    # 4. Image links included in RSS content or summary HTML
    html_parts = []

    for content in entry.get("content", []):
        html_parts.append(content.get("value", ""))

    html_parts.append(entry.get("summary", ""))

    for html in html_parts:
        match = re.search(
            r'<img[^>]+src=["\']([^"\']+)["\']',
            html,
            re.IGNORECASE,
        )

        if match:
            url = unescape(match.group(1)).strip()

            if url.startswith(("https://", "http://")):
                return url

    return ""


class Command(BaseCommand):
    help = "Fetch news headlines and available RSS images"

    def handle(self, *args, **options):
        total_saved = 0
        total_updated = 0

        for category, feed_url in RSS_FEEDS:
            self.stdout.write(f"Fetching {category} news...")

            try:
                feed = feedparser.parse(feed_url)

                if feed.bozo and not feed.entries:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Could not read {category} feed."
                        )
                    )
                    continue

                for entry in feed.entries[:15]:
                    title = entry.get("title", "").strip()
                    summary = entry.get("summary", "").strip()
                    source_url = entry.get("link", "").strip()
                    image_url = upgrade_image_url(extract_image_url(entry))

                    if not title or not source_url:
                        continue

                    # Update an existing article if its image is missing.
                    topic = TrendingTopic.objects.filter(
                        source_url=source_url
                    ).first()

                    if topic:
                        if image_url and image_url != topic.image_url:
                            topic.image_url = image_url[:1000]
                            topic.save(update_fields=["image_url"])
                            total_updated += 1
                        continue

                    summary = strip_tags(summary).strip()

                    if not summary:
                        summary = f"Read the original report: {title}"

                    base_slug = slugify(title)[:200] or "news"
                    slug = base_slug
                    number = 2

                    while TrendingTopic.objects.filter(
                        slug=slug
                    ).exists():
                        slug = f"{base_slug[:190]}-{number}"
                        number += 1

                    TrendingTopic.objects.create(
                        title=title[:200],
                        slug=slug,
                        category=category,
                        summary=summary,
                        trend_score=50,
                        source_url=source_url,
                        image_url=image_url[:1000],
                        is_active=True,
                    )

                    total_saved += 1

            except Exception as error:
                self.stdout.write(
                    self.style.WARNING(
                        f"Error fetching {category}: {error}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished! Added {total_saved} new articles. "
                f"Updated images for {total_updated} existing articles."
            )
        )