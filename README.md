# E-commerce Item Finder

A sophisticated web scraper that searches multiple e-commerce sites (Noon.com, Namshi.com, and Amazon.ae) for items and returns product information with prices. This tool uses advanced bot detection bypass techniques with a real browser and supports price filtering.

## Features

- 🤖 **Advanced Bot Detection Bypass**: Uses undetected-chromedriver and multiple anti-detection techniques
- 🌐 **Real Browser Automation**: Uses Selenium with Chrome for realistic browsing behavior
- � **Multi-Site Support**: Search Noon.com, Namshi.com, and Amazon.ae simultaneously or individually
- �💰 **Price Filtering**: Set maximum prices per item to only show products within budget
- 🔄 **Human-like Behavior**: Random delays, scrolling, and user agent rotation
- 📊 **Comprehensive Results**: Returns product titles, prices, URLs, ratings, brands, and images
- 💾 **Multiple Output Formats**: Console output and JSON file export
- 🔍 **Robust Parsing**: Multiple selector strategies for reliable data extraction
- 📝 **Detailed Logging**: Comprehensive logging for debugging and monitoring
- 🎯 **Unified Interface**: Single command to search multiple sites and compare results

## Quick Start (Recommended)

The easiest way to get started is with the automatic installer:

```bash
python3 install_and_run.py
```

This will:
- Create a virtual environment
- Install all dependencies
- Guide you through running the scraper
- Handle everything automatically

## Manual Installation

If you prefer manual setup:

1. Make sure you have Python 3.7+ installed
2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. Or install manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Available Scrapers

This project now includes four main scrapers:

1. **Noon.com Scraper** (`simple_noon_scraper.py`) - Scrapes Noon.com for electronics and general items
2. **Namshi.com Scraper** (`simple_namshi_scraper.py`) - Scrapes Namshi.com for fashion and clothing items
3. **Amazon.ae Scraper** (`simple_amazon_scraper.py`) - Scrapes Amazon.ae for electronics, books, and general items
4. **Unified Scraper** (`unified_scraper.py`) - Searches all three sites simultaneously for comprehensive results

## Usage

### Unified Scraper (Recommended)

Search Noon, Namshi, and Amazon with a single command:

```bash
# Search all sites
python3 unified_scraper.py "jacket"

# Search with price limit
python3 unified_scraper.py "dress" --max-price 200

# Search only Noon
python3 unified_scraper.py "iPhone 15" --noon-only

# Search only Namshi
python3 unified_scraper.py "jacket" --namshi-only

# Search only Amazon
python3 unified_scraper.py "Harry Potter book" --amazon-only

# Run in headless mode (no browser window)
python3 unified_scraper.py "shoes" --headless
```

## How to Use the Unified Scraper

The unified scraper (`unified_scraper.py`) is the recommended way to search across all three sites (Noon.com, Namshi.com, and Amazon.ae) simultaneously. Here's a complete guide:

### Basic Usage

1. **Search all sites for a product:**
   ```bash
   python3 unified_scraper.py "iPhone 15"
   ```
   This searches Noon, Namshi, and Amazon for "iPhone 15" and shows results from all sites.

2. **Search with a price limit:**
   ```bash
   python3 unified_scraper.py "laptop" --max-price 2000
   ```
   Only shows products under AED 2000 from all sites.

3. **Search specific sites only:**
   ```bash
   # Electronics from Noon only
   python3 unified_scraper.py "iPhone 15" --noon-only
   
   # Fashion from Namshi only
   python3 unified_scraper.py "jacket" --namshi-only
   
   # Books/Electronics from Amazon only
   python3 unified_scraper.py "MacBook" --amazon-only
   ```

### Advanced Options

4. **Run in headless mode (no browser window):**
   ```bash
   python3 unified_scraper.py "shoes" --headless
   ```
   Faster execution, but harder to debug if issues occur.

5. **Save results to custom file:**
   ```bash
   python3 unified_scraper.py "gaming laptop" --output "gaming_search.json"
   ```
   Results saved to your specified filename instead of auto-generated name.

6. **Combine multiple options:**
   ```bash
   python3 unified_scraper.py "smartwatch" --max-price 500 --headless --output "watch_results.json"
   ```

### Step-by-Step Example

Let's search for a gaming laptop under AED 3000:

```bash
# 1. Navigate to the project folder
cd "/Users/begadwael/Desktop/item finder"

# 2. Activate virtual environment (if using one)
source venv/bin/activate

# 3. Run the unified scraper
python3 unified_scraper.py "gaming laptop" --max-price 3000
```

**What happens:**
1. The scraper opens Chrome browsers for each site
2. Searches Noon.com, Namshi.com, and Amazon.ae
3. Filters results to show only laptops under AED 3000
4. Displays a unified comparison of all results
5. Saves results to `unified_search_gaming_laptop.json`

### Understanding the Output

The unified scraper shows:
- **🏪 Site name** (Noon.com, Namshi.com, Amazon.ae)
- **Product details** for each item found
- **💰 Price** with budget analysis
- **⭐ Ratings** (when available)
- **🚚 Delivery info** (when available)
- **💚 Budget status** (within/over your price limit)

### Quick Command Reference

| Command | Description |
|---------|-------------|
| `python3 unified_scraper.py "product"` | Search all sites |
| `--max-price 500` | Set price limit to AED 500 |
| `--noon-only` | Search only Noon.com |
| `--namshi-only` | Search only Namshi.com |
| `--amazon-only` | Search only Amazon.ae |
| `--headless` | Run without browser window |
| `--output filename.json` | Save to custom file |
| `--help` | Show all available options |

### Troubleshooting

- **No results found:** Try searching individual sites or different keywords
- **Browser won't open:** Make sure Chrome is installed and requirements are met
- **Slow performance:** Use `--headless` for faster execution
- **Amazon blocked:** Try `--noon-only` or `--namshi-only` first

### Individual Scrapers

#### Noon.com Scraper

```bash
# Search for a single item
python3 simple_noon_scraper.py --single "iPhone 15"

# Search with price limit
python3 simple_noon_scraper.py --single "iPhone 15,3000"

# Search from file
python3 simple_noon_scraper.py --file items.txt

# Run in headless mode
python3 simple_noon_scraper.py --headless --single "laptop"
```

#### Namshi.com Scraper

```bash
# Search for a single item
python3 simple_namshi_scraper.py --single "jacket"

# Search with price limit
python3 simple_namshi_scraper.py --single "dress,300"

# Search from file
python3 simple_namshi_scraper.py --file items.txt

# Run in headless mode
python3 simple_namshi_scraper.py --headless --single "shoes"
```

#### Amazon.ae Scraper

```bash
# Search for a single item
python3 simple_amazon_scraper.py --single "laptop"

# Search with price limit
python3 simple_amazon_scraper.py --single "iPhone 15,3000"

# Search from file
python3 simple_amazon_scraper.py --file amazon_items.txt

# Run in headless mode
python3 simple_amazon_scraper.py --headless --single "HDD"
```

### File-based Searching

Create a text file with items to search. You can specify items with or without price limits:

```
# Basic format (no price limit)
iPhone 15 Pro
Samsung Galaxy S24
jacket
dress

# With price limits (only show items under this price)
iPhone 15 Pro,3000
Samsung Galaxy S24,2500
jacket,200
dress,150
```

### Price Filtering

You can specify maximum prices for items in two ways:

**Method 1: In the file (recommended)**
```
# items_with_prices.txt
iPhone 15 Pro,3000          # Only show iPhones under AED 3000
Samsung Galaxy S24,2500     # Only show Galaxy S24 under AED 2500  
iPad Pro 12.9               # No price limit for this item
AirPods Pro,800            # Only show AirPods under AED 800
```

**Method 2: Command line for single items**
```bash
python simple_noon_scraper.py --single "iPhone 15,3000"
python simple_noon_scraper.py --single "Samsung Galaxy S24"  # No price limit
```

### Advanced Usage

```bash
# Search specific file with price limits
python simple_noon_scraper.py --file items_with_prices.txt

# Single item search with price limit
python simple_noon_scraper.py --single "iPhone 15 Pro,3000"

# Run in headless mode (no browser window)
python simple_noon_scraper.py --file items.txt --headless

# Search single item without price limit
python simple_noon_scraper.py --single "MacBook Air M2"
```

### Command Line Options

- `--file, -f`: Text file containing items to search (default: items.txt)
- `--single, -s`: Search for a single item (format: "item" or "item,maxprice")
- `--headless`: Run browser in headless mode

## Input File Format

The input file supports flexible formatting:

```
# Comments start with # and are ignored
iPhone 15 Pro                    # Item without price limit
Samsung Galaxy S24,2500          # Item with max price AED 2500
MacBook Air M2,4000             # Item with max price AED 4000

# Empty lines are ignored
Sony WH-1000XM5 headphones,1200  # Headphones under AED 1200
```

## Output

The tool provides results in two formats:

### 1. Console Output
Formatted, easy-to-read results displayed in the terminal with:
- 🔍 Search terms and price limits
- 💰 Product prices with budget information
- 💚 Indicators showing items within budget
- ⭐ Product ratings
- 🔗 Direct product URLs

### 2. JSON File
Structured data saved to `search_results.json` with price filtering information:

```json
{
  "iPhone 15 Pro": {
    "max_price_filter": 3000,
    "products": [
      {
        "title": "Apple iPhone 15 Pro 128GB Natural Titanium",
        "price": "AED 2,999",
        "price_value": 2999.0,
        "url": "https://www.noon.com/uae-en/...",
        "image_url": "https://...",
        "rating": "4.5",
        "within_budget": true
      }
    ]
  }
}
      "rating": "4.5"
    }
  ]
}
```

## CSV Export Feature

All scrapers now support CSV export for easy data analysis in Excel, Google Sheets, or other tools.

### Using CSV Export

1. **Unified scraper with CSV:**
   ```bash
   python3 unified_scraper.py "laptop" --csv
   python3 unified_scraper.py "iPhone 15" --csv --max-price 3000
   ```

2. **Individual scrapers with CSV:**
   ```bash
   python3 simple_noon_scraper.py --single "laptop" --csv
   python3 simple_namshi_scraper.py --single "jacket" --csv
   python3 simple_amazon_scraper.py --single "headphones" --csv
   ```

3. **Custom CSV filename:**
   ```bash
   python3 unified_scraper.py "gaming laptop" --csv --output "gaming_search"
   # Creates: gaming_search.csv
   ```

### CSV vs JSON Output

| Format | Best For | Advantages |
|--------|----------|------------|
| **CSV** | Data analysis, Excel | Easy to open, smaller size, good for filtering |
| **JSON** | Detailed data, programming | Complete metadata, nested data, API-friendly |

### CSV Columns

The CSV export includes these columns:
- `site` - Which site (Noon.com, Namshi.com, Amazon.ae)
- `title` - Product name
- `price` - Formatted price with currency
- `price_value` - Numeric price for sorting/filtering
- `brand` - Product brand (when available)
- `rating` - Customer rating (when available)
- `review_count` - Number of reviews (when available)
- `delivery_info` - Shipping information
- `within_budget` - TRUE/FALSE if within price limit
- `url` - Product page link
- `image_url` - Product image link

### Demo CSV Export

Try the CSV demo:
```bash
python3 demo_csv_export.py
```

## Anti-Detection Features

- **Undetected Chrome Driver**: Uses undetected-chromedriver for better stealth
- **Random User Agents**: Rotates user agents to avoid fingerprinting
- **Human-like Delays**: Random delays between actions (1-7 seconds)
- **Random Scrolling**: Mimics human browsing behavior
- **Window Size Randomization**: Random browser window sizes
- **Script Execution**: Removes webdriver properties from navigator object

## Requirements

- Python 3.7+
- Chrome browser (automatically managed by webdriver-manager)
- Internet connection

## Dependencies

- `selenium`: Web browser automation
- `undetected-chromedriver`: Stealth Chrome driver
- `webdriver-manager`: Automatic Chrome driver management
- `beautifulsoup4`: HTML parsing backup
- `fake-useragent`: User agent rotation
- `requests`: HTTP requests

## Troubleshooting

### Common Issues

1. **Chrome not found**: Install Google Chrome browser
2. **Timeout errors**: Increase delays or check internet connection
3. **No products found**: Item might not be available on noon.com
4. **Bot detection**: Run with longer delays or in non-headless mode

### Logging

Check the `noon_scraper.log` file for detailed execution logs and error messages.

## Legal Notice

This tool is for educational and personal use only. Please respect noon.com's terms of service and robots.txt. Use responsibly and don't overload their servers with too many requests.

## Example Items File

Create an `items.txt` file with one item per line:

```
iPhone 15 Pro
Samsung Galaxy S24
Apple MacBook Air M2
Sony WH-1000XM5 headphones
Nintendo Switch OLED
iPad Pro 12.9
AirPods Pro 2nd generation
Dell XPS 13 laptop
Canon EOS R6
Dyson V15 vacuum cleaner
```

## Contributing

Feel free to improve the scraper by:
- Adding more anti-detection techniques
- Improving product information extraction
- Adding support for other websites
- Enhancing error handling

## License

This project is for educational purposes. Use at your own risk and responsibility.

## Amazon.ae Specific Features

The Amazon.ae scraper includes additional features:

- **Anti-Detection**: Enhanced anti-bot measures for Amazon's strict detection
- **Rich Product Data**: Extracts ratings, review counts, delivery info, and stock status
- **Prime Detection**: Identifies Prime delivery options
- **Discount Information**: Captures special offers and credit card discounts
- **Stock Alerts**: Shows availability status (e.g., "Only 2 left in stock")

⚠️ **Note**: Amazon has strict anti-bot measures. If you encounter issues:
- Try running without headless mode first
- Use longer delays between searches
- Consider using a VPN if blocked
# item-finder-scrapper
