#!/usr/bin/env python3
"""
LinkedIn Engagement Automation
Main entry point for the application.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from colorama import Fore, Style, init

from src.monitor import LinkedInMonitor
from src.config import Config
from src.tracker import PostTracker

# Initialize colorama
init(autoreset=True)


def print_banner():
    """Print application banner."""
    banner = f"""
{Fore.CYAN}{'='*70}
    LinkedIn Engagement Automation
    Track influencers and generate AI-powered comments
{'='*70}{Style.RESET_ALL}
"""
    print(banner)


def check_setup():
    """Check if the application is properly set up."""
    issues = []

    # Check if .env exists
    if not Path('.env').exists():
        issues.append("❌ .env file not found. Copy .env.example to .env and configure it.")

    # Check if config.yaml exists
    if not Path('config.yaml').exists():
        issues.append("❌ config.yaml not found.")

    # Try to load config
    try:
        config = Config()

        # Check LinkedIn credentials
        if not config.linkedin_email or not config.linkedin_password:
            issues.append("❌ LinkedIn credentials not configured in .env")

        # Check AI provider configuration
        if config.ai_provider == "openai" and not config.openai_api_key:
            issues.append("❌ OpenAI API key not configured in .env")
        elif config.ai_provider == "anthropic" and not config.anthropic_api_key:
            issues.append("❌ Anthropic API key not configured in .env")

        # Check if profiles are configured
        if not config.profiles:
            issues.append("⚠️  No profiles configured in config.yaml")

    except Exception as e:
        issues.append(f"❌ Error loading configuration: {str(e)}")

    if issues:
        print(f"{Fore.RED}Setup Issues Found:{Style.RESET_ALL}")
        for issue in issues:
            print(f"  {issue}")
        print(f"\n{Fore.YELLOW}Please fix these issues before running the application.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}See README.md for setup instructions.{Style.RESET_ALL}\n")
        return False

    print(f"{Fore.GREEN}✅ Configuration check passed!{Style.RESET_ALL}\n")
    return True


async def run_once():
    """Run a single check cycle."""
    print_banner()

    if not check_setup():
        sys.exit(1)

    monitor = LinkedInMonitor()
    await monitor.run_once()


async def run_continuous():
    """Run continuous monitoring."""
    print_banner()

    if not check_setup():
        sys.exit(1)

    monitor = LinkedInMonitor()
    await monitor.run_continuous()


def show_stats():
    """Show tracking statistics."""
    print_banner()

    try:
        config = Config()
        tracker = PostTracker(
            excel_file=config.excel_file,
            cache_file=config.cache_file
        )
        tracker.print_stats()

    except Exception as e:
        print(f"{Fore.RED}Error loading statistics: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


def show_config():
    """Show current configuration."""
    print_banner()

    try:
        config = Config()

        print(f"{Fore.CYAN}Configuration:{Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}Profiles:{Style.RESET_ALL}")
        for i, profile in enumerate(config.profiles, 1):
            print(f"  {i}. {profile.get('name', 'Unknown')} - {profile.get('url', '')}")

        print(f"\n{Fore.YELLOW}Monitoring:{Style.RESET_ALL}")
        print(f"  Check Interval: {config.check_interval} minutes")
        print(f"  Max Posts per Check: {config.max_posts_per_check}")
        print(f"  Track Recent Days: {config.track_recent_days}")

        print(f"\n{Fore.YELLOW}Comment Generation:{Style.RESET_ALL}")
        print(f"  AI Provider: {config.ai_provider}")
        print(f"  Default Style: {config.default_comment_style}")
        print(f"  Length: {config.comment_length}")
        print(f"  Include Emojis: {config.include_emojis}")
        print(f"  Analyze Tone: {config.analyze_tone}")

        print(f"\n{Fore.YELLOW}Safety:{Style.RESET_ALL}")
        print(f"  Dry Run: {config.dry_run}")
        print(f"  Max Comments per Day: {config.max_comments_per_day}")
        print(f"  Randomize Timing: {config.randomize_timing}")

        print(f"\n{Fore.YELLOW}Files:{Style.RESET_ALL}")
        print(f"  Excel File: {config.excel_file}")
        print(f"  Cache File: {config.cache_file}")

        print()

    except Exception as e:
        print(f"{Fore.RED}Error loading configuration: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='LinkedIn Engagement Automation - Track influencers and generate AI comments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py run              # Run a single check cycle
  python main.py monitor          # Run continuous monitoring
  python main.py stats            # Show statistics
  python main.py config           # Show configuration

For more information, see README.md
        """
    )

    parser.add_argument(
        'command',
        choices=['run', 'monitor', 'stats', 'config', 'check'],
        help='Command to execute'
    )

    args = parser.parse_args()

    try:
        if args.command == 'run':
            asyncio.run(run_once())

        elif args.command == 'monitor':
            asyncio.run(run_continuous())

        elif args.command == 'stats':
            show_stats()

        elif args.command == 'config':
            show_config()

        elif args.command == 'check':
            print_banner()
            check_setup()

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(0)

    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == '__main__':
    main()
