#!/bin/bash

# Install and run the Noon Item Finder

echo "🚀 Setting up Noon Item Finder..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing required packages..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To run the scraper:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the scraper: python noon_scraper.py --file items.txt"
echo ""
echo "Options:"
echo "  --file, -f    : Specify the text file containing items (default: items.txt)"
echo "  --output, -o  : Specify the output JSON file (default: search_results.json)"
echo "  --headless    : Run browser in headless mode (no GUI)"
echo ""
echo "Example: python noon_scraper.py --file my_items.txt --output results.json --headless"
