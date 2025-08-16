import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import json
from app.core.config import settings
logger = logging.getLogger(__name__)
class HTTPClient:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    async def __aenter__(self):
        await self._ensure_session()
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout,
                connector=connector
            )
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    async def get_page_content(self, url: str, retries: int = None) -> Optional[str]:
        if retries is None:
            retries = settings.MAX_RETRIES
        await self._ensure_session()
        for attempt in range(retries + 1):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"Successfully fetched {url}")
                        return content
                    elif response.status == 404:
                        logger.debug(f"Page not found: {url}")
                        return None
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching {url} (attempt {attempt + 1})")
            except Exception as e:
                logger.warning(f"Error fetching {url} (attempt {attempt + 1}): {e}")
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)
        logger.error(f"Failed to fetch {url} after {retries + 1} attempts")
        return None
    async def get_json(self, url: str, retries: int = None) -> Optional[Dict[Any, Any]]:
        if retries is None:
            retries = settings.MAX_RETRIES
        await self._ensure_session()
        for attempt in range(retries + 1):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Successfully fetched JSON from {url}")
                        return data
                    elif response.status == 404:
                        logger.debug(f"JSON endpoint not found: {url}")
                        return None
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching JSON from {url} (attempt {attempt + 1})")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {url}")
                return None
            except Exception as e:
                logger.warning(f"Error fetching JSON from {url} (attempt {attempt + 1}): {e}")
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)
        logger.error(f"Failed to fetch JSON from {url} after {retries + 1} attempts")
        return None
    async def post_json(self, url: str, data: Dict[Any, Any], retries: int = None) -> Optional[Dict[Any, Any]]:
        if retries is None:
            retries = settings.MAX_RETRIES
        await self._ensure_session()
        for attempt in range(retries + 1):
            try:
                async with self.session.post(url, json=data) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        logger.debug(f"Successfully posted to {url}")
                        return result
                    else:
                        logger.warning(f"HTTP {response.status} posting to {url}")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout posting to {url} (attempt {attempt + 1})")
            except Exception as e:
                logger.warning(f"Error posting to {url} (attempt {attempt + 1}): {e}")
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)
        logger.error(f"Failed to post to {url} after {retries + 1} attempts")