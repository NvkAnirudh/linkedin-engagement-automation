"""Configuration management for LinkedIn engagement automation."""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration.

        Args:
            config_path: Path to YAML configuration file
        """
        # Load environment variables
        load_dotenv()

        # Load YAML config
        self.config_path = Path(config_path)
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

    @property
    def linkedin_email(self) -> str:
        """Get LinkedIn email from environment."""
        return os.getenv("LINKEDIN_EMAIL", "")

    @property
    def linkedin_password(self) -> str:
        """Get LinkedIn password from environment."""
        return os.getenv("LINKEDIN_PASSWORD", "")

    @property
    def ai_provider(self) -> str:
        """Get AI provider (openai or anthropic)."""
        return os.getenv("AI_PROVIDER", "openai")

    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key."""
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def openai_model(self) -> str:
        """Get OpenAI model."""
        return os.getenv("OPENAI_MODEL", "gpt-4")

    @property
    def anthropic_api_key(self) -> str:
        """Get Anthropic API key."""
        return os.getenv("ANTHROPIC_API_KEY", "")

    @property
    def anthropic_model(self) -> str:
        """Get Anthropic model."""
        return os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    @property
    def headless(self) -> bool:
        """Get headless browser setting."""
        return os.getenv("HEADLESS", "true").lower() == "true"

    @property
    def slow_mo(self) -> int:
        """Get slow motion delay for browser."""
        return int(os.getenv("SLOW_MO", "100"))

    @property
    def profiles(self) -> List[Dict[str, str]]:
        """Get list of profiles to track."""
        return self.config.get("profiles", [])

    @property
    def check_interval(self) -> int:
        """Get check interval in minutes."""
        return self.config.get("monitoring", {}).get("check_interval", 30)

    @property
    def max_posts_per_check(self) -> int:
        """Get maximum posts to fetch per check."""
        return self.config.get("monitoring", {}).get("max_posts_per_check", 10)

    @property
    def track_recent_days(self) -> int:
        """Get number of recent days to track."""
        return self.config.get("monitoring", {}).get("track_recent_days", 7)

    @property
    def default_comment_style(self) -> str:
        """Get default comment style."""
        return self.config.get("comment_generation", {}).get("default_style", "professional")

    @property
    def comment_length(self) -> str:
        """Get comment length preference."""
        return self.config.get("comment_generation", {}).get("length", "short")

    @property
    def include_emojis(self) -> bool:
        """Get emoji preference for comments."""
        return self.config.get("comment_generation", {}).get("include_emojis", False)

    @property
    def analyze_tone(self) -> bool:
        """Get tone analysis preference."""
        return self.config.get("comment_generation", {}).get("analyze_tone", True)

    @property
    def excel_file(self) -> str:
        """Get Excel file path."""
        return self.config.get("tracking", {}).get("excel_file", "data/tracked_posts.xlsx")

    @property
    def cache_file(self) -> str:
        """Get cache file path."""
        return self.config.get("tracking", {}).get("cache_file", "data/seen_posts.json")

    @property
    def include_metrics(self) -> bool:
        """Get metrics tracking preference."""
        return self.config.get("tracking", {}).get("include_metrics", True)

    @property
    def dry_run(self) -> bool:
        """Get dry run mode setting."""
        return self.config.get("safety", {}).get("dry_run", True)

    @property
    def max_comments_per_day(self) -> int:
        """Get maximum comments per day per profile."""
        return self.config.get("safety", {}).get("max_comments_per_day", 10)

    @property
    def randomize_timing(self) -> bool:
        """Get timing randomization preference."""
        return self.config.get("safety", {}).get("randomize_timing", True)

    def get_profile_comment_style(self, profile_url: str) -> str:
        """Get comment style for specific profile.

        Args:
            profile_url: Profile URL to check

        Returns:
            Comment style for the profile
        """
        for profile in self.profiles:
            if profile.get("url") == profile_url:
                return profile.get("comment_style", self.default_comment_style)
        return self.default_comment_style
