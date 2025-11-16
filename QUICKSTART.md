# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install

### Quick Setup (Recommended)

**Linux/macOS:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

The setup script uses [uv](https://github.com/astral-sh/uv) for fast dependency installation.

### Manual Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install deps
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
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
# With activated venv
python main.py check

# Or with uv (no activation needed)
uv run main.py check
```

## Step 5: Run!

### Single check:
```bash
uv run main.py run
```

### Continuous monitoring:
```bash
uv run main.py monitor
```

## Step 6: Review Results

Check `data/tracked_posts.xlsx` for all tracked posts and generated comments!

## Common Commands

| Command | Description |
|---------|-------------|
| `uv run main.py check` | Verify setup |
| `uv run main.py run` | Run once |
| `uv run main.py monitor` | Run continuously |
| `uv run main.py stats` | View statistics |
| `uv run main.py config` | Show configuration |

> **Tip:** Use `uv run` to run commands without activating the virtual environment!

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
