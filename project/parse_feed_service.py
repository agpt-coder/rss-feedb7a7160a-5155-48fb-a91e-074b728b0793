from typing import List, Optional

import feedparser
from pydantic import BaseModel


class FeedMetadata(BaseModel):
    """
    The structure encapsulating feed metadata information.
    """

    title: str
    description: str
    last_updated: Optional[str] = None


class Article(BaseModel):
    """
    Represents an individual article or content item within the feed.
    """

    title: str
    link: str
    published: Optional[str] = None
    summary: Optional[str] = None


class ParseFeedResponse(BaseModel):
    """
    Structured metadata and article information extracted from the RSS or Atom feed, presented in a JSON format.
    """

    success: bool
    feed_metadata: FeedMetadata
    articles: List[Article]
    error: Optional[str] = None


def parse_feed(feed_url: str) -> ParseFeedResponse:
    try:
        data = feedparser.parse(feed_url)
        if data.bozo:
            return ParseFeedResponse(
                success=False,
                feed_metadata=FeedMetadata(title="", description=""),
                articles=[],
                error=f"Failed to parse feed: {data.bozo_exception}",
            )
        feed_metadata = FeedMetadata(
            title=data.feed.title,
            description=data.feed.description,
            last_updated=getattr(data.feed, "updated", None),
        )
        articles = [
            Article(
                title=entry.title,
                link=entry.link,
                published=getattr(entry, "published", None),
                summary=getattr(entry, "summary", None),
            )
            for entry in data.entries
        ]
        return ParseFeedResponse(
            success=True, feed_metadata=feed_metadata, articles=articles, error=None
        )
    except Exception as e:
        return ParseFeedResponse(
            success=False,
            feed_metadata=FeedMetadata(title="", description=""),
            articles=[],
            error=str(e),
        )
