# Unified Scraper Usage Examples

## Basic Examples

### 1. Search all sites for a product
```bash
python3 unified_scraper.py "iPhone 15"
```
**What it does:** Searches Noon, Namshi, and Amazon for iPhone 15
**Best for:** Getting comprehensive price comparison

### 2. Search with price limit
```bash
python3 unified_scraper.py "laptop" --max-price 2000
```
**What it does:** Only shows laptops under AED 2000 from all sites
**Best for:** Budget shopping

### 3. Fashion items (Namshi focus)
```bash
python3 unified_scraper.py "dress" --namshi-only
```
**What it does:** Searches only Namshi for dresses
**Best for:** Fashion and clothing items

### 4. Electronics (Noon + Amazon)
```bash
python3 unified_scraper.py "headphones" --noon-only
python3 unified_scraper.py "headphones" --amazon-only
```
**What it does:** Compare electronics prices between Noon and Amazon
**Best for:** Electronics shopping

## Advanced Examples

### 5. Background search (faster)
```bash
python3 unified_scraper.py "smartwatch" --headless
```
**What it does:** Runs without showing browser windows
**Best for:** Quick searches when you don't need to see the process

### 6. Custom output file
```bash
python3 unified_scraper.py "gaming mouse" --output "gaming_gear.json"
```
**What it does:** Saves results to your specified filename
**Best for:** Organizing multiple searches

### 7. Complete example with all options
```bash
python3 unified_scraper.py "wireless earbuds" --max-price 300 --headless --output "earbuds_search.json"
```
**What it does:** 
- Searches all sites for wireless earbuds
- Only shows items under AED 300
- Runs in background (faster)
- Saves to "earbuds_search.json"

## Product Category Examples

### Electronics
```bash
# Mobile phones
python3 unified_scraper.py "Samsung Galaxy S24" --max-price 3000

# Computers
python3 unified_scraper.py "MacBook Air" --amazon-only

# Gaming
python3 unified_scraper.py "PlayStation 5" --noon-only
```

### Fashion & Clothing
```bash
# Clothing
python3 unified_scraper.py "winter jacket" --namshi-only --max-price 400

# Shoes
python3 unified_scraper.py "running shoes" --max-price 500

# Accessories
python3 unified_scraper.py "leather handbag" --namshi-only
```

### Home & Lifestyle
```bash
# Appliances
python3 unified_scraper.py "coffee machine" --max-price 800

# Books
python3 unified_scraper.py "programming books" --amazon-only

# Sports
python3 unified_scraper.py "yoga mat" --max-price 200
```

## Interactive Mode

### Use the quick start helper
```bash
python3 quick_start.py
```
**What it does:** Interactive guide that asks what you want to search
**Best for:** Beginners or when you want guided assistance

## Troubleshooting Examples

### If Amazon is blocked
```bash
# Search other sites first
python3 unified_scraper.py "laptop" --noon-only
python3 unified_scraper.py "laptop" --namshi-only
```

### If searches are slow
```bash
# Use headless mode
python3 unified_scraper.py "product" --headless
```

### For debugging
```bash
# Run without headless to see what's happening
python3 unified_scraper.py "product"
```

## Output Files

Each search creates a JSON file with detailed results:
- `unified_search_[product_name].json` - Default naming
- Custom name with `--output filename.json`

## Tips for Best Results

1. **Use specific product names:** "iPhone 15 Pro" vs "phone"
2. **Set realistic price limits:** Check market prices first
3. **Try different keywords:** "laptop" vs "notebook" vs "MacBook"
4. **Use site-specific searches:** Electronics on Noon/Amazon, Fashion on Namshi
5. **Run in headless mode for speed:** Add `--headless` for faster results
