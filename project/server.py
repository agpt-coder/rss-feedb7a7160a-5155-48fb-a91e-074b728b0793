import logging
from contextlib import asynccontextmanager

import project.parse_feed_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="rss feed",
    lifespan=lifespan,
    description="Based on the requirements and responses gathered, to build an endpoint that parses RSS XML and returns a structured JSON representation, the following steps need to be implemented: 1. Use the 'feedparser' library to parse the RSS XML from a provided URL. This library will handle the extraction of feed metadata and item (article) details including titles and links which are required for navigating the content efficiently. 2. Once the RSS XML is parsed, employ best practices for converting XML to JSON, such as using 'xmltodict' for parsing and the 'json' module for conversion, ensuring proper handling of namespaces, attributes, arrays, and objects, and extensively testing the conversion process. 3. With the data converted into a structured JSON format, the endpoint will return this JSON, making the RSS feed content more accessible and easier to integrate with other applications or services. This process will be implemented using Python, taking advantage of its rich ecosystem of libraries for XML parsing and JSON conversion, and ensuring a streamlined and effective workflow for consuming RSS feed content.",
)


@app.post(
    "/api/feedparser/parse", response_model=project.parse_feed_service.ParseFeedResponse
)
async def api_post_parse_feed(
    feed_url: str,
) -> project.parse_feed_service.ParseFeedResponse | Response:
    """
    Takes a URL of an RSS or Atom feed as input and returns structured metadata and articles.
    """
    try:
        res = project.parse_feed_service.parse_feed(feed_url)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
