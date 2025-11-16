# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install

### Linux/macOS
```bash
./setup.sh
```

### Windows
```bash
setup.bat
```

Or manually:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

## Step 2: Configure Credentials

Edit `.env`:
```env
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password

AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

## Step 3: Add Profiles to Track

Edit `config.yaml`:
```yaml
profiles:
  - url: "https://www.linkedin.com/in/example-profile/"
    name: "Influencer Name"
    comment_style: "professional"
```

## Step 4: Test Setup

```bash
python main.py check
```

## Step 5: Run!

### Single check:
```bash
python main.py run
```

### Continuous monitoring:
```bash
python main.py monitor
```

## Step 6: Review Results

Check `data/tracked_posts.xlsx` for all tracked posts and generated comments!

## Common Commands

| Command | Description |
|---------|-------------|
| `python main.py check` | Verify setup |
| `python main.py run` | Run once |
| `python main.py monitor` | Run continuously |
| `python main.py stats` | View statistics |
| `python main.py config` | Show configuration |

## Tips

1. **Start with dry_run: true** (default) to test without posting
2. **Use conservative limits** to avoid detection
3. **Check Excel file** to see generated comments
4. **Monitor API costs** if using paid AI providers

## Troubleshooting

### "LinkedIn credentials not configured"
→ Add credentials to `.env` file

### "No profiles configured"
→ Add profiles to `config.yaml`

### "OpenAI API key not configured"
→ Add API key to `.env` or switch to Anthropic

### Browser not opening
→ Run `playwright install chromium`

### Login issues
→ Set `HEADLESS=false` in `.env` to see browser

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Customize comment styles in `config.yaml`
- Adjust monitoring intervals
- Review generated comments in Excel

**Happy automating!** 🚀
