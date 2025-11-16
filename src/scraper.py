"""LinkedIn scraper using Playwright."""

import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from colorama import Fore, Style


class LinkedInScraper:
    """Scraper for LinkedIn profiles and posts."""

    def __init__(self, email: str, password: str, headless: bool = True, slow_mo: int = 100):
        """Initialize LinkedIn scraper.

        Args:
            email: LinkedIn account email
            password: LinkedIn account password
            headless: Run browser in headless mode
            slow_mo: Slow down operations by specified milliseconds
        """
        self.email = email
        self.password = password
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start browser and login to LinkedIn."""
        print(f"{Fore.CYAN}Starting LinkedIn scraper...{Style.RESET_ALL}")

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )

        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        self.page = await context.new_page()
        await self._login()
        print(f"{Fore.GREEN}Successfully logged in to LinkedIn{Style.RESET_ALL}")

    async def _login(self):
        """Login to LinkedIn."""
        print(f"{Fore.CYAN}Logging in to LinkedIn...{Style.RESET_ALL}")

        try:
            # Navigate to LinkedIn login page
            await self.page.goto('https://www.linkedin.com/login', wait_until='networkidle', timeout=30000)

            # Fill in credentials
            await self.page.fill('input[name="session_key"]', self.email)
            await self.page.fill('input[name="session_password"]', self.password)

            # Click login button
            await self.page.click('button[type="submit"]')

            # Wait for navigation
            await self.page.wait_for_load_state('networkidle', timeout=30000)

            # Check for security checkpoints (multiple possible URLs)
            current_url = self.page.url
            checkpoint_keywords = ['/checkpoint/', '/challenge/', '/uas/login-submit', '/add-phone', '/verify']

            if any(keyword in current_url for keyword in checkpoint_keywords):
                print(f"{Fore.YELLOW}⚠️  LinkedIn security checkpoint detected!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Current URL: {current_url}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}📧 Check your email for verification or solve the CAPTCHA in the browser.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Waiting 120 seconds for manual intervention...{Style.RESET_ALL}")

                # Wait and check every 10 seconds
                for i in range(12):
                    await asyncio.sleep(10)
                    print(f"{Fore.CYAN}  ... {(i+1)*10}s elapsed{Style.RESET_ALL}")

                    # Check if user solved the challenge
                    current_url = self.page.url
                    if not any(keyword in current_url for keyword in checkpoint_keywords):
                        print(f"{Fore.GREEN}✅ Challenge appears to be solved!{Style.RESET_ALL}")
                        break

            # Verify we're logged in (increased timeout)
            print(f"{Fore.CYAN}Verifying login...{Style.RESET_ALL}")
            await self.page.wait_for_selector('nav.global-nav, div.global-nav, header', timeout=30000)

            print(f"{Fore.GREEN}✅ Login verification successful!{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}Login error details: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Current URL: {self.page.url}{Style.RESET_ALL}")
            raise Exception(f"Failed to login to LinkedIn: {str(e)}")

    async def get_profile_posts(
        self,
        profile_url: str,
        max_posts: int = 10,
        recent_days: Optional[int] = None
    ) -> List[Dict]:
        """Scrape posts from a LinkedIn profile.

        Args:
            profile_url: LinkedIn profile URL
            max_posts: Maximum number of posts to fetch
            recent_days: Only fetch posts from last N days

        Returns:
            List of post dictionaries
        """
        print(f"{Fore.CYAN}Fetching posts from {profile_url}...{Style.RESET_ALL}")

        # Navigate to profile activity page
        if not profile_url.endswith('/'):
            profile_url += '/'

        activity_url = f"{profile_url}recent-activity/all/"

        try:
            await self.page.goto(activity_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)  # Wait for dynamic content

        except PlaywrightTimeout:
            print(f"{Fore.YELLOW}Timeout loading profile, trying direct posts URL...{Style.RESET_ALL}")
            # Try alternative URL
            activity_url = f"{profile_url}detail/recent-activity/shares/"
            await self.page.goto(activity_url, wait_until='networkidle', timeout=30000)

        posts = []
        cutoff_date = None

        if recent_days:
            cutoff_date = datetime.now() - timedelta(days=recent_days)

        # Scroll and collect posts
        last_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 10

        while len(posts) < max_posts and scroll_attempts < max_scroll_attempts:
            # Extract posts from current view
            new_posts = await self._extract_posts_from_page(cutoff_date)

            for post in new_posts:
                if post['post_id'] not in [p['post_id'] for p in posts]:
                    posts.append(post)

                    if len(posts) >= max_posts:
                        break

            # Scroll down to load more
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)

            # Check if we've reached the bottom
            new_height = await self.page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0

            last_height = new_height

        print(f"{Fore.GREEN}Found {len(posts)} posts{Style.RESET_ALL}")
        return posts[:max_posts]

    async def _extract_posts_from_page(self, cutoff_date: Optional[datetime] = None) -> List[Dict]:
        """Extract posts from current page view.

        Args:
            cutoff_date: Only extract posts after this date

        Returns:
            List of post dictionaries
        """
        posts = []

        # Find all post containers
        post_containers = await self.page.query_selector_all(
            'div.feed-shared-update-v2, li.profile-creator-shared-feed-update__container'
        )

        for container in post_containers:
            try:
                post_data = await self._extract_post_data(container)

                if post_data and (not cutoff_date or post_data['timestamp'] >= cutoff_date):
                    posts.append(post_data)

            except Exception as e:
                # Skip posts that fail to extract
                continue

        return posts

    async def _extract_post_data(self, container) -> Optional[Dict]:
        """Extract data from a single post container.

        Args:
            container: Playwright element handle for post container

        Returns:
            Dictionary with post data or None if extraction fails
        """
        try:
            # Extract post ID from data attribute or URL
            post_id = None
            urn_element = await container.query_selector('[data-urn]')
            if urn_element:
                urn = await urn_element.get_attribute('data-urn')
                if urn:
                    # Extract ID from URN
                    match = re.search(r':(\d+)', urn)
                    if match:
                        post_id = match.group(1)

            if not post_id:
                # Try to get from permalink
                permalink = await container.query_selector('a[href*="/feed/update/"]')
                if permalink:
                    href = await permalink.get_attribute('href')
                    match = re.search(r'update:urn:li:activity:(\d+)', href)
                    if match:
                        post_id = match.group(1)

            if not post_id:
                return None

            # Extract post content/text
            content = ""
            content_element = await container.query_selector(
                '.feed-shared-update-v2__description, .feed-shared-text, .update-components-text'
            )
            if content_element:
                content = await content_element.inner_text()
                content = content.strip()

            # Extract timestamp
            timestamp = datetime.now()
            time_element = await container.query_selector('time[datetime]')
            if time_element:
                datetime_str = await time_element.get_attribute('datetime')
                try:
                    timestamp = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                except:
                    pass

            # Extract engagement metrics
            likes = await self._extract_metric(container, 'reactions', 'reaction-count')
            comments = await self._extract_metric(container, 'comments', 'comment-count')
            shares = await self._extract_metric(container, 'repost', 'repost-count')

            # Extract post URL
            post_url = ""
            permalink_elem = await container.query_selector('a[href*="/feed/update/"]')
            if permalink_elem:
                post_url = await permalink_elem.get_attribute('href')
                if post_url and not post_url.startswith('http'):
                    post_url = f"https://www.linkedin.com{post_url}"

            return {
                'post_id': post_id,
                'content': content,
                'timestamp': timestamp,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'url': post_url,
                'scraped_at': datetime.now()
            }

        except Exception as e:
            return None

    async def _extract_metric(self, container, keyword: str, aria_label: str) -> int:
        """Extract engagement metric from post.

        Args:
            container: Post container element
            keyword: Keyword to search for in text
            aria_label: Aria label to search for

        Returns:
            Metric count
        """
        try:
            # Try multiple selectors
            selectors = [
                f'button[aria-label*="{keyword}"]',
                f'span[class*="{aria_label}"]',
                f'button:has-text("{keyword}")'
            ]

            for selector in selectors:
                element = await container.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    # Extract number from text
                    match = re.search(r'([\d,]+)', text)
                    if match:
                        return int(match.group(1).replace(',', ''))

            return 0

        except:
            return 0

    async def close(self):
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
            print(f"{Fore.CYAN}Browser closed{Style.RESET_ALL}")
