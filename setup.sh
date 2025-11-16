#!/bin/bash
# Quick setup script for LinkedIn Engagement Automation

echo "=================================="
echo "LinkedIn Engagement Automation"
echo "Setup Script (using uv)"
echo "=================================="
echo ""

# Check if uv is installed
echo "Checking for uv..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed"
    echo ""
    echo "Would you like to install uv? (y/n)"
    read -r install_uv

    if [ "$install_uv" = "y" ] || [ "$install_uv" = "Y" ]; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Add uv to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"

        if command -v uv &> /dev/null; then
            echo "✅ uv installed successfully"
        else
            echo "❌ Failed to install uv. Please install manually:"
            echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
            exit 1
        fi
    else
        echo "Please install uv manually and run this script again:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
else
    echo "✅ uv found ($(uv --version))"
fi
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version found"
echo ""

# Create virtual environment with uv
echo "Creating virtual environment with uv..."
uv venv

if [ $? -eq 0 ]; then
    echo "✅ Virtual environment created"
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies with uv
echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

if [ $? -eq 0 ]; then
    echo "✅ Playwright browsers installed"
else
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi
echo ""

# Create .env from example
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env and add your credentials"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Create data directory
echo "Creating data directory..."
mkdir -p data
echo "✅ Data directory created"
echo ""

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your LinkedIn credentials and API keys"
echo "2. Edit config.yaml and add profiles to track"
echo "3. Activate the environment: source .venv/bin/activate"
echo "4. Run: python main.py check"
echo "5. Run: python main.py run"
echo ""
echo "Or use uv run directly (no activation needed):"
echo "  uv run main.py check"
echo "  uv run main.py run"
echo ""
echo "For more information, see README.md"
echo ""
