"""
Simple and working Noon scraper
"""

import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote_plus
import json
from dataclasses import dataclass
from typing import List, Optional
import logging

@dataclass
class ProductInfo:
    """Data class to store product information"""
    title: str
    price: str
    url: str
    image_url: Optional[str] = None
    rating: Optional[str] = None
    price_value: Optional[float] = None  # Numeric price for filtering

@dataclass
class SearchItem:
    """Data class to store search item with optional price limit"""
    name: str
    max_price: Optional[float] = None

class SimpleNoonScraper:
    """Simple working Noon scraper"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_numeric_price(self, price_str: str) -> Optional[float]:
        """Extract numeric price value from price string"""
        try:
            # Remove currency symbols and clean the string
            clean_price = re.sub(r'[^\d.,]', '', price_str)
            clean_price = clean_price.replace(',', '')
            
            # Handle decimal points
            if '.' in clean_price:
                return float(clean_price)
            else:
                return float(clean_price)
        except (ValueError, AttributeError):
            return None

    def setup_driver(self):
        """Setup Chrome driver with minimal options"""
        try:
            options = Options()
            
            if self.headless:
                options.add_argument('--headless')
            
            # Minimal options to avoid conflicts
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Try to create driver without webdriver-manager first
            try:
                self.driver = webdriver.Chrome(options=options)
                self.logger.info("Chrome driver initialized successfully (system)")
            except:
                # Fallback to webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                self.logger.info("Chrome driver initialized successfully (webdriver-manager)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup driver: {str(e)}")
            return False
    
    def search_item(self, search_item: SearchItem) -> List[ProductInfo]:
        """Search for an item on noon.com with optional price filtering"""
        try:
            products = []
            item_name = search_item.name
            max_price = search_item.max_price
            
            search_query = quote_plus(item_name.strip())
            search_url = f"https://www.noon.com/uae-en/search?q={search_query}"
            
            self.logger.info(f"Searching for: {item_name}")
            if max_price:
                self.logger.info(f"Max price filter: AED {max_price}")
            self.logger.info(f"URL: {search_url}")
            
            self.driver.get(search_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Check if page loaded properly
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            self.logger.info(f"Page title: {page_title}")
            self.logger.info(f"Current URL: {current_url}")
            
            # Check for error pages
            if "can't be reached" in page_title.lower() or "error" in page_title.lower():
                self.logger.error("Page failed to load - connection error")
                return products
            
            # Get page source to analyze
            page_source = self.driver.page_source
            
            # Check if we have actual content
            if len(page_source) < 1000:
                self.logger.warning("Page content seems to short")
                return products
            
            # Look for product elements using a broad approach
            self.logger.info("Looking for product elements...")
            
            # Try to find any elements that might contain products
            potential_products = []
            
            # Strategy 1: Look for noon.com specific product containers
            class_selectors = [
                "[data-qa='plp-product-box']",  # Main product container
                ".ProductBoxLinkHandler_linkWrapper__b0qZ9",  # Specific noon selector
                "[class*='product']",
                "[class*='ProductBox']",
                "[class*='item']",
                "[class*='card']"
            ]
            
            for selector in class_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements:
                        text = element.text.strip()
                        if len(text) > 30 and len(text) < 1000:  # Reasonable text length
                            # Check if text contains product-like keywords
                            if any(keyword.lower() in text.lower() for keyword in [
                                'iphone', 'samsung', 'apple', 'gb', 'pro', 'max', 'plus',
                                'aed', 'price', 'rating', 'review'
                            ]):
                                potential_products.append(element)
                                
                    if potential_products:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            # Strategy 2: If no products found, look for divs with substantial text
            if not potential_products:
                self.logger.info("Trying fallback strategy...")
                all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                
                for div in all_divs:
                    try:
                        text = div.text.strip()
                        if (30 < len(text) < 500 and 
                            any(keyword.lower() in text.lower() for keyword in [
                                item_name.lower(), 'iphone', 'samsung', 'aed'
                            ])):
                            potential_products.append(div)
                            if len(potential_products) >= 5:
                                break
                    except:
                        continue
            
            self.logger.info(f"Found {len(potential_products)} potential product elements")
            
            # Extract information from potential products
            for i, element in enumerate(potential_products[:5]):
                try:
                    product_info = self.extract_simple_product_info(element, item_name)
                    if product_info:
                        # Apply price filter if specified
                        if max_price and product_info.price_value:
                            if product_info.price_value <= max_price:
                                products.append(product_info)
                                self.logger.info(f"Product {i+1} matches price filter: {product_info.title[:50]}... (AED {product_info.price_value})")
                            else:
                                self.logger.info(f"Product {i+1} filtered out by price: {product_info.title[:50]}... (AED {product_info.price_value} > {max_price})")
                        else:
                            products.append(product_info)
                            self.logger.info(f"Extracted product {i+1}: {product_info.title[:50]}...")
                except Exception as e:
                    self.logger.warning(f"Error extracting product {i+1}: {str(e)}")
                    continue
            
            return products
            
        except Exception as e:
            self.logger.error(f"Error searching for {item_name}: {str(e)}")
            return []
    
    def extract_simple_product_info(self, element, search_term: str) -> Optional[ProductInfo]:
        """Extract product information using noon.com specific selectors"""
        try:
            # Get all text from the element
            full_text = element.text.strip()
            
            if len(full_text) < 10:
                return None
            
            # Extract title using noon.com specific selector
            title = None
            title_selectors = [
                "[data-qa='plp-product-box-name']",  # Noon specific
                ".ProductDetailsSection_title__JorAV",  # From the HTML
                "h2[title]",
                "h2",
                "[class*='title']"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip() or title_element.get_attribute("title")
                    if title and len(title) > 10:
                        break
                except:
                    continue
            
            # Fallback to text parsing if no title found
            if not title:
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                for line in lines:
                    if (len(line) > 10 and 
                        not line.replace('.', '').replace(',', '').replace(' ', '').isdigit() and
                        'aed' not in line.lower() and
                        '%' not in line and
                        'off' not in line.lower()):
                        title = line
                        break
            
            if not title:
                title = "Unknown Product"
            
            # Clean title
            title = re.sub(r'\s+', ' ', title).strip()
            if len(title) > 100:
                title = title[:100] + "..."
            
            # Extract price using noon.com specific selectors
            price = "Price not available"
            
            # Noon.com specific price selectors from the HTML
            price_selectors = [
                ".Price_amount__2sXa7",  # Main price from HTML
                "[data-qa='plp-product-box-price'] strong",  # Alternative
                ".Price_sellingPrice__HFKZf strong",  # Alternative structure
                "[class*='Price_amount']",  # Flexible class match
                "[class*='sellingPrice'] strong",
                "[class*='price'] strong"
            ]
            
            for selector in price_selectors:
                try:
                    price_element = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_element.text.strip()
                    if price_text and price_text.replace(',', '').replace('.', '').isdigit():
                        # Add AED currency if not present
                        if 'aed' not in price_text.lower():
                            price = f"AED {price_text}"
                        else:
                            price = price_text
                        break
                except:
                    continue
            
            # Fallback: extract price from text using patterns
            if price == "Price not available":
                price_patterns = [
                    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:aed|د\.إ)',
                    r'(?:aed|د\.إ)\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                    r'\b(\d{1,3}(?:,\d{3})*)\b(?=\s*(?:aed|د\.إ))',
                ]
                
                for pattern in price_patterns:
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        price_num = match.group(1)
                        clean_num = price_num.replace(',', '').replace('.', '')
                        if clean_num.isdigit() and int(clean_num) > 50:
                            price = f"AED {price_num}"
                            break
                
                # Last resort: look for any reasonable number in the text
                if price == "Price not available":
                    lines = full_text.split('\n')
                    for line in lines:
                        # Look for numbers that could be prices (between 100-50000)
                        numbers = re.findall(r'\b(\d{1,3}(?:,\d{3})*)\b', line)
                        for num in numbers:
                            clean_num = num.replace(',', '')
                            if clean_num.isdigit() and 100 <= int(clean_num) <= 50000:
                                price = f"AED {num}"
                                break
                        if price != "Price not available":
                            break
            
            # Extract URL using noon.com specific structure
            url = f"https://www.noon.com/uae-en/search?q={quote_plus(search_term)}"
            
            # Look for the main product link
            link_selectors = [
                ".ProductBoxLinkHandler_productBoxLink__FPhjp",  # From HTML
                "a[href*='/p/']",  # Product page links
                "a[href*='N53433298A']",  # Product ID links
                "a[href*='/uae-en/']"  # UAE links
            ]
            
            for selector in link_selectors:
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, selector)
                    href = link_element.get_attribute("href")
                    if href:
                        if href.startswith("/"):
                            url = f"https://www.noon.com{href}"
                        elif href.startswith("http"):
                            url = href
                        break
                except:
                    continue
            
            # If element itself is a link
            if url.endswith(quote_plus(search_term)) and element.tag_name == "a":
                href = element.get_attribute("href")
                if href and "/p/" in href:
                    if href.startswith("/"):
                        url = f"https://www.noon.com{href}"
                    else:
                        url = href
            
            # Extract image URL using noon.com structure
            image_url = None
            image_selectors = [
                ".ProductImageCarousel_productImage__jtsOn",  # From HTML
                "[class*='ProductImage'] img[src*='nooncdn']",
                "img[src*='nooncdn'][alt*='Image 1']",
                "img[src*='nooncdn']:not([src*='placeholder'])"
            ]
            
            for selector in image_selectors:
                try:
                    img_element = element.find_element(By.CSS_SELECTOR, selector)
                    src = img_element.get_attribute("src")
                    if src and "placeholder" not in src and src.startswith("http"):
                        image_url = src
                        break
                except:
                    continue
            
            # Extract rating using noon.com structure
            rating = None
            rating_selectors = [
                ".RatingPreviewStar_textCtr__sfsJG",  # From HTML
                "[class*='RatingPreview'] [class*='textCtr']",
                "[class*='rating'] [class*='text']"
            ]
            
            for selector in rating_selectors:
                try:
                    rating_element = element.find_element(By.CSS_SELECTOR, selector)
                    rating_text = rating_element.text.strip()
                    if rating_text and re.match(r'^\d+\.?\d*$', rating_text):
                        rating_val = float(rating_text)
                        if 0 <= rating_val <= 5:
                            rating = rating_text
                            break
                except:
                    continue
            
            self.logger.info(f"Extracted: {title[:30]}... | Price: {price} | URL: {'✓' if '/p/' in url else '✗'}")
            
            # Extract numeric price value for filtering
            price_value = self.extract_numeric_price(price)
            
            return ProductInfo(
                title=title,
                price=price,
                url=url,
                image_url=image_url,
                rating=rating,
                price_value=price_value
            )
            
        except Exception as e:
            self.logger.warning(f"Error in extraction: {str(e)}")
            return None
    
    def save_results(self, results: dict, output_file: str = "search_results.json"):
        """Save results to JSON file with price filtering information"""
        try:
            serializable_results = {}
            for item, data in results.items():
                products = data['products']
                max_price = data['max_price']
                
                serializable_results[item] = {
                    'max_price_filter': max_price,
                    'products': [
                        {
                            'title': product.title,
                            'price': product.price,
                            'price_value': product.price_value,
                            'url': product.url,
                            'image_url': product.image_url,
                            'rating': product.rating,
                            'within_budget': (product.price_value <= max_price) if (max_price and product.price_value) else None
                        }
                        for product in products
                    ]
                }
            
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(serializable_results, file, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
    
    def save_results_csv(self, results: dict, output_file: str = "search_results.csv"):
        """Save results to CSV file with price filtering information"""
        import csv
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'search_term', 'title', 'price', 'price_value', 'rating', 
                    'within_budget', 'url', 'image_url'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write data
                for item, data in results.items():
                    products = data['products']
                    max_price = data['max_price']
                    
                    for product in products:
                        row = {
                            'search_term': item,
                            'title': product.title,
                            'price': product.price,
                            'price_value': product.price_value,
                            'rating': product.rating or '',
                            'within_budget': (product.price_value <= max_price) if (max_price and product.price_value) else '',
                            'url': product.url,
                            'image_url': product.image_url or ''
                        }
                        writer.writerow(row)
            
            self.logger.info(f"CSV results saved to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving CSV results: {str(e)}")
    
    def print_results(self, results: dict):
        """Print results with price filtering information"""
        print("\n" + "="*80)
        print("NOON.COM SEARCH RESULTS")
        print("="*80)
        
        for item, data in results.items():
            products = data['products']
            max_price = data['max_price']
            
            print(f"\n🔍 SEARCH: {item}")
            if max_price:
                print(f"💰 Price limit: AED {max_price}")
            print("-" * 60)
            
            if not products:
                if max_price:
                    print("❌ No products found within price limit")
                else:
                    print("❌ No products found")
                continue
            
            for i, product in enumerate(products, 1):
                print(f"\n{i}. {product.title}")
                print(f"   💰 Price: {product.price}")
                if product.price_value and max_price:
                    savings = max_price - product.price_value
                    if savings > 0:
                        print(f"   💚 Within budget (AED {savings:.0f} under limit)")
                print(f"   🔗 URL: {product.url}")
                if product.rating:
                    print(f"   ⭐ Rating: {product.rating}")
    
    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

def parse_items_from_file(file_path: str) -> List[SearchItem]:
    """Parse items from file, supporting format: 'Item Name' or 'Item Name,MaxPrice'"""
    items = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            
            # Check if line contains a comma (price limit specified)
            if ',' in line:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 2:
                    item_name = parts[0]
                    try:
                        max_price = float(parts[1])
                        items.append(SearchItem(name=item_name, max_price=max_price))
                        print(f"📝 Line {line_num}: {item_name} (max price: AED {max_price})")
                    except ValueError:
                        print(f"⚠️  Line {line_num}: Invalid price '{parts[1]}', treating as no price limit")
                        items.append(SearchItem(name=item_name))
                else:
                    items.append(SearchItem(name=line))
                    print(f"📝 Line {line_num}: {line}")
            else:
                items.append(SearchItem(name=line))
                print(f"📝 Line {line_num}: {line}")
        
        return items
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return []

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Noon.com Scraper with Price Filtering")
    parser.add_argument("--single", "-s", help="Search for a single item (format: 'item' or 'item,maxprice')")
    parser.add_argument("--file", "-f", default="items.txt", help="Search for items from file")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--csv", action="store_true", help="Export results as CSV instead of JSON")
    
    args = parser.parse_args()
    
    # Determine what to search
    if args.single:
        # Parse single item with optional price
        if ',' in args.single:
            parts = [part.strip() for part in args.single.split(',')]
            if len(parts) >= 2:
                try:
                    max_price = float(parts[1])
                    items_to_search = [SearchItem(name=parts[0], max_price=max_price)]
                    print(f"🔍 Single search: {parts[0]} (max price: AED {max_price})")
                except ValueError:
                    print(f"⚠️  Invalid price '{parts[1]}', searching without price limit")
                    items_to_search = [SearchItem(name=parts[0])]
            else:
                items_to_search = [SearchItem(name=args.single)]
        else:
            items_to_search = [SearchItem(name=args.single)]
            print(f"🔍 Single search: {args.single}")
    else:
        # Read items from file
        items_to_search = parse_items_from_file(args.file)
        
        if not items_to_search:
            print(f"❌ No valid items found in {args.file}")
            print("💡 File format:")
            print("   iPhone 15                    # No price limit")
            print("   Samsung Galaxy S24,2000      # Max price AED 2000")
            print("   # This is a comment line")
            return
            
        print(f"📝 Found {len(items_to_search)} items in {args.file}")
    
    scraper = SimpleNoonScraper(headless=args.headless)
    
    try:
        print("🔧 Setting up browser...")
        if not scraper.setup_driver():
            print("❌ Failed to setup browser")
            return
        
        all_results = {}
        
        for i, search_item in enumerate(items_to_search, 1):
            print(f"\n🚀 Searching {i}/{len(items_to_search)}: {search_item.name}")
            if search_item.max_price:
                print(f"💰 Price limit: AED {search_item.max_price}")
            
            results = scraper.search_item(search_item)
            all_results[search_item.name] = {
                'products': results,
                'max_price': search_item.max_price
            }
            
            # Add delay between searches if multiple items
            if len(items_to_search) > 1 and i < len(items_to_search):
                import time
                delay = 3  # 3 second delay between searches
                print(f"⏳ Waiting {delay} seconds before next search...")
                time.sleep(delay)
        
        if any(data['products'] for data in all_results.values()):
            scraper.print_results(all_results)
            
            # Save in requested format
            if args.csv:
                scraper.save_results_csv(all_results)
                print(f"\n✅ Results saved to CSV!")
            else:
                scraper.save_results(all_results)
                print(f"\n✅ Results saved to JSON!")
        else:
            print("❌ No results found")
            
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
