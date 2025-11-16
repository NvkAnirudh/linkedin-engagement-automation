# LinkedIn Engagement Automation

An intelligent automation tool that tracks LinkedIn influencers, analyzes their posts, and generates contextual comments using AI. Perfect for maintaining consistent engagement with thought leaders in your industry.

## Features

- **Automated Profile Tracking**: Monitor multiple LinkedIn profiles for new posts
- **AI-Powered Comment Generation**: Generate authentic, contextual comments using OpenAI or Anthropic Claude
- **Tone Analysis**: Automatically detect post tone and match your comment style
- **Excel Tracking**: Comprehensive logging of all posts and generated comments
- **Smart Caching**: Avoid reprocessing posts you've already seen
- **Rate Limiting**: Built-in safety features to avoid LinkedIn detection
- **Dry Run Mode**: Test the system without posting actual comments
- **Flexible Configuration**: YAML-based configuration for easy customization

## How It Works

1. **Scraping**: Uses Playwright to scrape LinkedIn profiles (no official API needed)
2. **Detection**: Identifies new posts that haven't been seen before
3. **Analysis**: AI analyzes the post content and tone
4. **Generation**: Creates an appropriate one-liner comment matching the post's tone
5. **Logging**: Records everything in Excel for tracking and analysis

## Use Case Example

**Scenario**: You follow Zach, an influencer with 500k followers. Instead of manually:
- Checking for new posts
- Reading each post
- Thinking of something meaningful to comment
- Typing the comment

This tool **automates** the entire workflow, generating thoughtful, contextual comments that match each post's tone and content.

## Installation

### Prerequisites

- Python 3.8 or higher
- LinkedIn account
- OpenAI API key OR Anthropic API key

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd linkedin-engagement-automation
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:
   ```env
   # LinkedIn Credentials
   LINKEDIN_EMAIL=your.email@example.com
   LINKEDIN_PASSWORD=your_password

   # AI Provider (choose one)
   AI_PROVIDER=openai  # or 'anthropic'

   # OpenAI (if using)
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4

   # Anthropic (if using)
   ANTHROPIC_API_KEY=sk-ant-...
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

   # Browser Settings
   HEADLESS=true
   SLOW_MO=100
   ```

6. **Configure profiles to track**:

   Edit `config.yaml` and add the LinkedIn profiles you want to monitor:
   ```yaml
   profiles:
     - url: "https://www.linkedin.com/in/zach-example/"
       name: "Zach"
       comment_style: "professional"

     - url: "https://www.linkedin.com/in/another-influencer/"
       name: "Jane Doe"
       comment_style: "enthusiastic"
   ```

## Configuration

### Comment Styles

- **professional**: Business-appropriate, formal tone
- **casual**: Friendly and relaxed
- **enthusiastic**: Energetic and excited
- **thoughtful**: Deep and reflective
- **supportive**: Encouraging and positive

### Comment Lengths

- **short**: 5-10 words
- **medium**: 10-20 words
- **long**: 20-30 words

### Monitoring Settings

```yaml
monitoring:
  check_interval: 30          # Check every 30 minutes
  max_posts_per_check: 10     # Process max 10 posts per check
  track_recent_days: 7        # Only track posts from last 7 days
```

### Safety Features

```yaml
safety:
  dry_run: true                    # Don't actually post comments (recommended!)
  max_comments_per_day: 10         # Limit per profile per day
  randomize_timing: true           # Add random delays to avoid detection
```

## Usage

### Check Configuration

Verify your setup is correct:
```bash
python main.py check
```

### Run Single Check

Run once and exit:
```bash
python main.py run
```

### Continuous Monitoring

Run continuously with configured interval:
```bash
python main.py monitor
```

Press `Ctrl+C` to stop.

### View Statistics

See tracking statistics:
```bash
python main.py stats
```

### View Configuration

Display current configuration:
```bash
python main.py config
```

## Output

### Console Output

The tool provides colorful, informative console output:

```
==============================================================================
    LinkedIn Engagement Automation
    Track influencers and generate AI-powered comments
==============================================================================

======================================================================
Checking profile: Zach
URL: https://www.linkedin.com/in/zach-example/
======================================================================

📝 New Post Found!
──────────────────────────────────────────────────────────────────────
Post ID: 1234567890
Date: 2024-01-15 10:30:00
Likes: 234 | Comments: 45 | Shares: 12

Content Preview:
Excited to share that our team just launched a new AI-powered feature...

💬 Generated Comment
──────────────────────────────────────────────────────────────────────
Tone: celebratory
Comment: Congrats on the launch! Excited to see the impact this will have.
Reasoning: The post is celebratory about a product launch, so an encouraging
           comment acknowledging the achievement is appropriate.
──────────────────────────────────────────────────────────────────────
```

### Excel Tracking

All data is logged to `data/tracked_posts.xlsx` with columns:

| Column | Description |
|--------|-------------|
| Post ID | Unique post identifier |
| Profile Name | Name of the influencer |
| Profile URL | LinkedIn profile URL |
| Post URL | Direct link to the post |
| Post Date | When the post was published |
| Scraped At | When we discovered it |
| Post Content | Full post text |
| Detected Tone | AI-detected tone |
| Generated Comment | The AI-generated comment |
| Comment Style | Style used for generation |
| Reasoning | Why this comment was chosen |
| Likes, Comments, Shares | Engagement metrics |
| Posted Comment | Whether comment was posted |
| Posted At | When comment was posted |
| Notes | Your custom notes |

## Project Structure

```
linkedin-engagement-automation/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── scraper.py             # LinkedIn scraping with Playwright
│   ├── comment_generator.py   # AI comment generation
│   ├── tracker.py             # Excel tracking and logging
│   └── monitor.py             # Main orchestration logic
├── data/
│   ├── tracked_posts.xlsx     # Excel tracking file
│   └── seen_posts.json        # Cache of processed posts
├── config.yaml                # Main configuration
├── .env                       # Environment variables (credentials)
├── requirements.txt           # Python dependencies
├── main.py                    # CLI entry point
└── README.md                  # This file
```

## Advanced Usage

### Custom Comment Generation

You can customize the AI prompts by editing `src/comment_generator.py`. The `_build_prompt()` method controls how comments are generated.

### Posting Comments (Experimental)

By default, the tool runs in dry-run mode. To enable actual posting:

1. Set `dry_run: false` in `config.yaml`
2. Implement the posting logic in `src/monitor.py` (currently a placeholder)
3. **Use with caution** - automated posting may violate LinkedIn's ToS

### Running as a Service

You can run this as a background service using:

**Linux (systemd)**:
```bash
# Create service file at /etc/systemd/system/linkedin-monitor.service
# Enable and start: systemctl enable linkedin-monitor && systemctl start linkedin-monitor
```

**macOS (launchd)**:
```bash
# Create plist file in ~/Library/LaunchAgents/
```

**Windows (Task Scheduler)**:
```bash
# Create a scheduled task to run main.py monitor
```

## Important Notes & Disclaimers

### LinkedIn Terms of Service

⚠️ **Important**: This tool uses web scraping to access LinkedIn, which may violate LinkedIn's Terms of Service. Use at your own risk. The authors are not responsible for any account restrictions or bans.

**Recommendations**:
- Use a secondary LinkedIn account for testing
- Keep `dry_run: true` to avoid posting
- Use conservative rate limits
- Enable `randomize_timing`
- Monitor for unusual activity

### Rate Limiting

LinkedIn actively monitors for bot activity. This tool includes safety features:
- Randomized timing
- Configurable delays
- Daily comment limits
- Slow browser automation

### Privacy & Security

- **Never** commit your `.env` file to version control
- Store credentials securely
- Use environment-specific configurations
- Monitor API usage costs (OpenAI/Anthropic charge per request)

### AI Costs

Each comment generation makes an API call:
- **OpenAI GPT-4**: ~$0.03 per 1K tokens (~$0.01 per comment)
- **Anthropic Claude**: ~$0.015 per 1K tokens (~$0.005 per comment)

Monitor your usage to avoid unexpected charges.

## Troubleshooting

### Login Issues

If you encounter LinkedIn login problems:
- Check credentials in `.env`
- LinkedIn may require 2FA - handle the checkpoint manually when prompted
- Use `HEADLESS=false` to see the browser
- Check for CAPTCHA challenges

### Scraping Errors

If posts aren't being detected:
- LinkedIn frequently changes their HTML structure
- Update selectors in `src/scraper.py`
- Check browser console for errors
- Try reducing `check_interval`

### AI Generation Issues

If comments aren't being generated:
- Verify API keys are correct
- Check API quota/billing
- Review error messages in console
- Try switching providers (OpenAI ↔ Anthropic)

### Excel Errors

If Excel file issues occur:
- Close the file if open in Excel
- Check file permissions
- Delete `data/tracked_posts.xlsx` to regenerate

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Future Enhancements

- [ ] Support for LinkedIn Company pages
- [ ] Browser extension for easier authentication
- [ ] Real-time notifications for new posts
- [ ] Analytics dashboard
- [ ] Comment posting functionality
- [ ] Multi-language support
- [ ] Local LLM support (Ollama, etc.)

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- Built with Playwright for reliable browser automation
- Powered by OpenAI GPT-4 and Anthropic Claude
- Excel tracking with openpyxl and pandas

---

**Happy Engaging!** 🚀
