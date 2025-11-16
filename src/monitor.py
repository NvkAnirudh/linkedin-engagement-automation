"""Monitor and orchestrate LinkedIn engagement automation."""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict
from colorama import Fore, Style, init

from .config import Config
from .scraper import LinkedInScraper
from .comment_generator import CommentGenerator
from .tracker import PostTracker

# Initialize colorama
init(autoreset=True)


class LinkedInMonitor:
    """Monitor LinkedIn profiles and automate engagement."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the monitor.

        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self.tracker = PostTracker(
            excel_file=self.config.excel_file,
            cache_file=self.config.cache_file
        )

        # Initialize comment generator
        api_key = (
            self.config.openai_api_key
            if self.config.ai_provider == "openai"
            else self.config.anthropic_api_key
        )
        model = (
            self.config.openai_model
            if self.config.ai_provider == "openai"
            else self.config.anthropic_model
        )

        self.comment_generator = CommentGenerator(
            provider=self.config.ai_provider,
            api_key=api_key,
            model=model,
            default_style=self.config.default_comment_style,
            length=self.config.comment_length,
            include_emojis=self.config.include_emojis,
            analyze_tone=self.config.analyze_tone
        )

        # Track daily comment counts
        self.daily_comment_counts = {}

    async def check_profile(self, profile: Dict) -> int:
        """Check a single profile for new posts.

        Args:
            profile: Profile configuration dictionary

        Returns:
            Number of new posts processed
        """
        profile_url = profile.get('url', '')
        profile_name = profile.get('name', 'Unknown')
        comment_style = profile.get('comment_style', self.config.default_comment_style)

        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"Checking profile: {profile_name}")
        print(f"URL: {profile_url}")
        print(f"{'='*70}{Style.RESET_ALL}\n")

        # Check daily limit
        today = datetime.now().date()
        profile_key = f"{profile_url}_{today}"

        if profile_key not in self.daily_comment_counts:
            self.daily_comment_counts[profile_key] = 0

        if self.daily_comment_counts[profile_key] >= self.config.max_comments_per_day:
            print(f"{Fore.YELLOW}⚠️  Daily comment limit reached for {profile_name}{Style.RESET_ALL}")
            return 0

        # Scrape posts
        async with LinkedInScraper(
            email=self.config.linkedin_email,
            password=self.config.linkedin_password,
            headless=self.config.headless,
            slow_mo=self.config.slow_mo
        ) as scraper:
            posts = await scraper.get_profile_posts(
                profile_url=profile_url,
                max_posts=self.config.max_posts_per_check,
                recent_days=self.config.track_recent_days
            )

        # Process new posts
        new_posts_count = 0

        for post in posts:
            post_id = post.get('post_id')

            # Skip if already seen
            if self.tracker.is_post_seen(post_id):
                print(f"{Fore.YELLOW}⏭️  Skipping already seen post: {post_id}{Style.RESET_ALL}")
                continue

            # Check daily limit again
            if self.daily_comment_counts[profile_key] >= self.config.max_comments_per_day:
                print(f"{Fore.YELLOW}⚠️  Daily comment limit reached{Style.RESET_ALL}")
                break

            # Process new post
            await self._process_post(post, profile_name, profile_url, comment_style)
            new_posts_count += 1
            self.daily_comment_counts[profile_key] += 1

            # Add delay between posts to avoid rate limiting
            if self.config.randomize_timing:
                delay = random.uniform(2, 5)
                await asyncio.sleep(delay)

        return new_posts_count

    async def _process_post(
        self,
        post: Dict,
        profile_name: str,
        profile_url: str,
        comment_style: str
    ):
        """Process a single post.

        Args:
            post: Post data dictionary
            profile_name: Name of profile
            profile_url: URL of profile
            comment_style: Comment style to use
        """
        print(f"\n{Fore.GREEN}{'─'*70}")
        print(f"📝 New Post Found!")
        print(f"{'─'*70}{Style.RESET_ALL}")

        # Display post info
        print(f"{Fore.CYAN}Post ID:{Style.RESET_ALL} {post.get('post_id')}")
        print(f"{Fore.CYAN}Date:{Style.RESET_ALL} {post.get('timestamp')}")
        print(f"{Fore.CYAN}Likes:{Style.RESET_ALL} {post.get('likes')} | "
              f"{Fore.CYAN}Comments:{Style.RESET_ALL} {post.get('comments')} | "
              f"{Fore.CYAN}Shares:{Style.RESET_ALL} {post.get('shares')}")

        content_preview = post.get('content', '')[:200]
        print(f"\n{Fore.CYAN}Content Preview:{Style.RESET_ALL}")
        print(f"{content_preview}...")

        # Generate comment
        print(f"\n{Fore.CYAN}Generating comment...{Style.RESET_ALL}")
        comment_data = self.comment_generator.generate_comment(
            post_content=post.get('content', ''),
            style=comment_style,
            author_name=profile_name
        )

        # Display generated comment
        print(f"\n{Fore.GREEN}{'─'*70}")
        print(f"💬 Generated Comment")
        print(f"{'─'*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Tone:{Style.RESET_ALL} {comment_data.get('tone')}")
        print(f"{Fore.CYAN}Comment:{Style.RESET_ALL} {comment_data.get('comment')}")
        print(f"{Fore.CYAN}Reasoning:{Style.RESET_ALL} {comment_data.get('reasoning')}")
        print(f"{Fore.GREEN}{'─'*70}{Style.RESET_ALL}\n")

        # Check if we should post the comment
        posted = False
        if not self.config.dry_run:
            # In a real implementation, this would post the comment to LinkedIn
            # For now, we just mark it as not posted since dry_run is likely true
            print(f"{Fore.YELLOW}⚠️  Dry run mode - comment not posted{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Dry run mode enabled - comment not posted{Style.RESET_ALL}")

        # Track in Excel
        self.tracker.add_post(
            post_data=post,
            profile_name=profile_name,
            profile_url=profile_url,
            comment_data=comment_data,
            comment_style=comment_style,
            posted=posted
        )

    async def run_once(self):
        """Run a single check cycle for all profiles."""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"🚀 LinkedIn Engagement Monitor")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}{Style.RESET_ALL}\n")

        total_new_posts = 0

        for profile in self.config.profiles:
            try:
                new_posts = await self.check_profile(profile)
                total_new_posts += new_posts

            except Exception as e:
                print(f"{Fore.RED}Error checking profile {profile.get('name', 'Unknown')}: {str(e)}{Style.RESET_ALL}")
                continue

        # Print statistics
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"✅ Check Cycle Complete")
        print(f"{'='*70}{Style.RESET_ALL}")
        print(f"New Posts Found: {total_new_posts}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.tracker.print_stats()

    async def run_continuous(self):
        """Run continuous monitoring with configured interval."""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"🔄 Starting Continuous Monitoring")
        print(f"Check Interval: {self.config.check_interval} minutes")
        print(f"Profiles: {len(self.config.profiles)}")
        print(f"{'='*70}{Style.RESET_ALL}\n")

        while True:
            try:
                await self.run_once()

                # Calculate next check time
                base_interval = self.config.check_interval * 60  # Convert to seconds

                if self.config.randomize_timing:
                    # Add randomization (±20% of interval)
                    variance = base_interval * 0.2
                    interval = base_interval + random.uniform(-variance, variance)
                else:
                    interval = base_interval

                next_check = datetime.now() + timedelta(seconds=interval)

                print(f"\n{Fore.CYAN}⏳ Next check at: {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Waiting {interval/60:.1f} minutes...{Style.RESET_ALL}\n")

                await asyncio.sleep(interval)

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}🛑 Monitoring stopped by user{Style.RESET_ALL}")
                break

            except Exception as e:
                print(f"{Fore.RED}Error in monitoring loop: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Retrying in 5 minutes...{Style.RESET_ALL}")
                await asyncio.sleep(300)


# Example usage
if __name__ == "__main__":
    monitor = LinkedInMonitor()
    asyncio.run(monitor.run_once())
