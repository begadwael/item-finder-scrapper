# Price Filtering Feature - Usage Guide

The Noon.com Item Finder now supports price filtering! You can specify maximum prices for items and only get results that are within your budget.

## 🆕 New Features

### 1. Price Filtering
- Set maximum prices for individual items
- Only see products under your specified price limit
- Get budget information showing how much you're saving

### 2. Flexible Input Format
- Search items with or without price limits in the same file
- Mix items with and without price constraints
- Support for comments in input files

## 📖 Usage Examples

### Command Line Examples

```bash
# Single item without price limit
python simple_noon_scraper.py --single "iPhone 15"

# Single item with price limit (only show items under AED 3000)
python simple_noon_scraper.py --single "iPhone 15,3000"

# Search from file with mixed price limits
python simple_noon_scraper.py --file items_with_prices.txt

# Run in headless mode (no browser window)
python simple_noon_scraper.py --file items_with_prices.txt --headless
```

### File Format Examples

**items_with_prices.txt:**
```
# Items with Price Filtering
# Format: Item Name,MaxPrice (or just Item Name for no limit)

iPhone 15 Pro,3000          # Only show iPhones under AED 3000
Samsung Galaxy S24,2500     # Only show Galaxy S24 under AED 2500
Apple MacBook Air M2,4000   # MacBooks under AED 4000
Sony WH-1000XM5 headphones,1200  # Headphones under AED 1200
Nintendo Switch OLED,1500   # Nintendo Switch under AED 1500
iPad Pro 12.9               # No price limit for iPad
AirPods Pro 2nd generation,800   # AirPods under AED 800

# Comments and empty lines are ignored
Dell XPS 13 laptop,5000
Canon EOS R6,8000
Dyson V15 vacuum cleaner,2000
```

## 🎯 Output Features

### Console Output
- Shows price limits for each search
- Indicates when products are within budget
- Displays savings amount when under budget
- Clear filtering status for each item

### JSON Output
The results include comprehensive price filtering information:

```json
{
  "iPhone 15 Pro": {
    "max_price_filter": 3000.0,
    "products": [
      {
        "title": "Apple iPhone 15 Pro 128GB",
        "price": "AED 2,999",
        "price_value": 2999.0,
        "url": "https://www.noon.com/...",
        "within_budget": true
      }
    ]
  }
}
```

## 🚀 Quick Start

1. **Using the automatic installer:**
   ```bash
   python install_and_run.py
   ```
   Choose option 3 or 4 to test price filtering.

2. **Manual testing:**
   ```bash
   source venv/bin/activate
   python test_price_filtering.py
   ```

3. **Real search with price filtering:**
   ```bash
   source venv/bin/activate
   python simple_noon_scraper.py --file items_with_prices.txt
   ```

## 💡 Tips

- **Price format**: Use numbers only (e.g., 3000 for AED 3000)
- **Mixed usage**: You can mix items with and without price limits in the same file
- **Comments**: Use # at the beginning of lines for comments
- **Budget planning**: The tool shows how much you're saving when items are under budget
- **Filtering**: Products over your price limit are automatically excluded from results

## 🔧 Advanced Usage

### Testing the Feature
Run the test script to see how price filtering works:
```bash
python test_price_filtering.py
```

### Custom Price Limits
You can set different price limits for each item based on your budget:
- Electronics: Higher limits (2000-5000 AED)
- Accessories: Lower limits (500-1500 AED)
- Appliances: Medium limits (1000-3000 AED)

This helps you stay within budget while still finding the products you need!
