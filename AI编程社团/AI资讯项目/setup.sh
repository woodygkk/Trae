#!/bin/bash
# AI News Skill Setup Script

echo "🤖 Setting up AI News Skill..."

# Get script directory
SKILL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SKILL_DIR"

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.7+"
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠️  Failed to install some dependencies. Try: pip3 install -r requirements.txt"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p data logs

# Make scripts executable
echo "Setting permissions..."
chmod +x scripts/*.py
chmod +x setup.sh

# Initialize database
echo "Initializing database..."
python3 scripts/ai_news.py update

if [ $? -eq 0 ]; then
    echo "✅ Setup complete!"
    echo ""
    echo "📚 Next steps:"
    echo "1. Configure push channels in config/push.yaml"
    echo "2. Test: python3 scripts/ai_news.py today"
    echo "3. Push: python3 scripts/ai_news.py push"
    echo "4. Start scheduler: python3 scripts/scheduler.py"
    echo ""
    echo "📖 Read README.md for detailed instructions"
else
    echo "⚠️  Initial update failed. Check your network connection and try again:"
    echo "   python3 scripts/ai_news.py update"
fi
