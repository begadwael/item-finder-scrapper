"""
Simple and working Namshi scraper
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
    brand: Optional[str] = None
    discount: Optional[str] = None
    delivery_info: Optional[str] = None

@dataclass
class SearchItem:
    """Data class to store search item with optional price limit"""
    name: str
    max_price: Optional[float] = None

class SimpleNamshiScraper:
    """Simple working Namshi scraper"""
    
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
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
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
        """Search for an item on namshi.com with optional price filtering"""
        try:
            products = []
            item_name = search_item.name
            max_price = search_item.max_price
            
            search_query = quote_plus(item_name.strip())
            search_url = f"https://www.namshi.com/uae-en/search?q={search_query}"
            
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
            
            # Look for product elements using Namshi-specific selectors
            self.logger.info("Looking for product elements...")
            
            # Wait a bit more for dynamic content to load
            time.sleep(3)
            
            # Namshi-specific product container selectors
            product_selectors = [
                ".ProductBox_detailsContainer__LX4rf",  # Main product container from your HTML
                "[class*='ProductBox_detailsContainer']",  # Flexible class match
                "[class*='ProductBox']",  # Any ProductBox class
                "[data-testid*='product']",  # Test ID selectors
                ".product-card",  # Generic product card
                ".product-item"   # Generic product item
            ]
            
            potential_products = []
            
            for selector in product_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    if elements:
                        potential_products = elements
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            # Fallback: Look for any container that might have product information
            if not potential_products:
                self.logger.info("Trying fallback strategy...")
                all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                
                for div in all_divs:
                    try:
                        text = div.text.strip()
                        # Look for divs that contain product-like content
                        if (50 < len(text) < 800 and 
                            any(keyword.lower() in text.lower() for keyword in [
                                'aed', 'delivery', 'free', 'discount', item_name.lower()
                            ]) and
                            re.search(r'\d+', text)):  # Contains numbers (likely prices)
                            potential_products.append(div)
                            if len(potential_products) >= 10:
                                break
                    except:
                        continue
            
            self.logger.info(f"Found {len(potential_products)} potential product elements")
            
            # Extract information from potential products
            for i, element in enumerate(potential_products[:10]):  # Limit to first 10 products
                try:
                    product_info = self.extract_namshi_product_info(element, item_name)
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
    
    def extract_namshi_product_info(self, element, search_term: str) -> Optional[ProductInfo]:
        """Extract product information using Namshi-specific selectors"""
        try:
            # Get all text from the element
            full_text = element.text.strip()
            
            if len(full_text) < 10:
                return None
            
            # Extract brand using Namshi-specific selector
            brand = None
            brand_selectors = [
                ".ProductBox_brand__oDc9f",  # From your HTML
                "[class*='ProductBox_brand']",
                "[class*='brand']"
            ]
            
            for selector in brand_selectors:
                try:
                    brand_element = element.find_element(By.CSS_SELECTOR, selector)
                    brand = brand_element.text.strip()
                    if brand and len(brand) > 1:
                        break
                except:
                    continue
            
            # Extract title using Namshi-specific selector
            title = None
            title_selectors = [
                ".ProductBox_productTitle__6tQ3b",  # From your HTML
                "[class*='ProductBox_productTitle']",
                "[class*='productTitle']",
                "[title]",
                "h2", "h3", "h4"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip() or title_element.get_attribute("title")
                    if title and len(title) > 5:
                        break
                except:
                    continue
            
            # Fallback to text parsing if no title found
            if not title:
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                for line in lines:
                    if (len(line) > 5 and len(line) < 100 and
                        not line.replace('.', '').replace(',', '').replace(' ', '').isdigit() and
                        'aed' not in line.lower() and
                        '%' not in line and
                        'delivery' not in line.lower() and
                        'free' not in line.lower()):
                        title = line
                        break
            
            # Combine brand and title if both exist
            if brand and title and brand.lower() not in title.lower():
                title = f"{brand} {title}"
            elif not title and brand:
                title = brand
            elif not title:
                title = "Unknown Product"
            
            # Clean title
            title = re.sub(r'\s+', ' ', title).strip()
            if len(title) > 100:
                title = title[:100] + "..."
            
            # Extract price using Namshi-specific selectors
            price = "Price not available"
            price_value = None
            
            # Namshi-specific price selectors from your HTML
            price_selectors = [
                ".ProductPrice_value__hnFSS",  # Main price value from your HTML
                ".ProductPrice_sellingPrice__y8kib .ProductPrice_value__hnFSS",  # More specific
                "[class*='ProductPrice_value']",
                "[class*='sellingPrice'] [class*='value']",
                "[class*='price'] [class*='value']"
            ]
            
            for selector in price_selectors:
                try:
                    price_element = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_element.text.strip()
                    if price_text and re.match(r'^\d+(\.\d+)?$', price_text):
                        price = f"AED {price_text}"
                        price_value = float(price_text)
                        break
                except:
                    continue
            
            # Extract old price (original price before discount)
            old_price = None
            old_price_selectors = [
                ".ProductPrice_preReductionPrice__S72wT",  # From your HTML
                "[class*='ProductPrice_oldPrice']",
                "[class*='preReductionPrice']",
                "[class*='oldPrice']"
            ]
            
            for selector in old_price_selectors:
                try:
                    old_price_element = element.find_element(By.CSS_SELECTOR, selector)
                    old_price_text = old_price_element.text.strip()
                    if old_price_text and re.match(r'^\d+(\.\d+)?$', old_price_text):
                        old_price = f"AED {old_price_text}"
                        break
                except:
                    continue
            
            # Extract discount percentage
            discount = None
            discount_selectors = [
                ".DiscountTag_value__D52x5",  # From your HTML
                "[class*='DiscountTag_value']",
                "[class*='discount']"
            ]
            
            for selector in discount_selectors:
                try:
                    discount_element = element.find_element(By.CSS_SELECTOR, selector)
                    discount_text = discount_element.text.strip()
                    if discount_text and '%' in discount_text:
                        discount = discount_text
                        break
                except:
                    continue
            
            # Fallback: extract price from text using patterns
            if price == "Price not available":
                price_patterns = [
                    r'(\d{1,4}(?:\.\d{2})?)\s*(?:aed|د\.إ)',
                    r'(?:aed|د\.إ)\s*(\d{1,4}(?:\.\d{2})?)',
                    r'\b(\d{1,4})\b(?=\s*(?:aed|د\.إ))',
                ]
                
                for pattern in price_patterns:
                    match = re.search(pattern, full_text, re.IGNORECASE)
                    if match:
                        price_num = match.group(1)
                        if price_num.replace('.', '').isdigit() and float(price_num) > 10:
                            price = f"AED {price_num}"
                            price_value = float(price_num)
                            break
                
                # Look for standalone numbers that could be prices
                if price == "Price not available":
                    lines = full_text.split('\n')
                    for line in lines:
                        numbers = re.findall(r'\b(\d{2,4})\b', line)
                        for num in numbers:
                            if 50 <= int(num) <= 5000:  # Reasonable price range
                                price = f"AED {num}"
                                price_value = float(num)
                                break
                        if price != "Price not available":
                            break
            
            # Extract delivery information
            delivery_info = None
            delivery_selectors = [
                ".RotatingElements_container__cS80Q",  # From your HTML
                ".DeliveryEstimateTag_content__2EErl",  # Delivery estimate
                "[class*='delivery']",
                "[class*='DeliveryEstimate']"
            ]
            
            for selector in delivery_selectors:
                try:
                    delivery_element = element.find_element(By.CSS_SELECTOR, selector)
                    delivery_text = delivery_element.text.strip()
                    if delivery_text and len(delivery_text) < 50:
                        delivery_info = delivery_text
                        break
                except:
                    continue
            
            # Extract URL - try to find product link
            url = f"https://www.namshi.com/uae-en/search?q={quote_plus(search_term)}"
            
            # Look for product links
            link_selectors = [
                "a[href*='/buy/']",  # Namshi product links
                "a[href*='/uae-en/']",  # UAE specific links
                "a"  # Any link within the element
            ]
            
            for selector in link_selectors:
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, selector)
                    href = link_element.get_attribute("href")
                    if href and ("/buy/" in href or "/uae-en/" in href):
                        if href.startswith("/"):
                            url = f"https://www.namshi.com{href}"
                        elif href.startswith("http"):
                            url = href
                        break
                except:
                    continue
            
            # Extract image URL
            image_url = None
            image_selectors = [
                "img[src*='namshi']",
                "img[src*='cloudfront']",
                "img:not([src*='placeholder']):not([src*='icon'])"
            ]
            
            for selector in image_selectors:
                try:
                    img_element = element.find_element(By.CSS_SELECTOR, selector)
                    src = img_element.get_attribute("src")
                    if src and src.startswith("http") and "placeholder" not in src:
                        image_url = src
                        break
                except:
                    continue
            
            # Build final price string with discount info
            if old_price and discount:
                price = f"{price} (was {old_price}, {discount} off)"
            elif old_price:
                price = f"{price} (was {old_price})"
            elif discount:
                price = f"{price} ({discount} off)"
            
            self.logger.info(f"Extracted: {title[:30]}... | Price: {price} | Brand: {brand}")
            
            return ProductInfo(
                title=title,
                price=price,
                url=url,
                image_url=image_url,
                rating=None,  # Namshi doesn't seem to show ratings in search results
                price_value=price_value,
                brand=brand,
                discount=discount,
                delivery_info=delivery_info
            )
            
        except Exception as e:
            self.logger.warning(f"Error in extraction: {str(e)}")
            return None
    
    def save_results(self, results: dict, output_file: str = "namshi_search_results.json"):
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
                            'brand': product.brand,
                            'discount': product.discount,
                            'delivery_info': product.delivery_info,
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
    
    def save_results_csv(self, results: dict, output_file: str = "namshi_search_results.csv"):
        """Save results to CSV file with price filtering information"""
        import csv
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'search_term', 'title', 'price', 'price_value', 'brand', 'discount', 
                    'delivery_info', 'within_budget', 'url', 'image_url'
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
                            'brand': product.brand or '',
                            'discount': product.discount or '',
                            'delivery_info': product.delivery_info or '',
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
        print("NAMSHI.COM SEARCH RESULTS")
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
                if product.brand:
                    print(f"   🏷️  Brand: {product.brand}")
                if product.delivery_info:
                    print(f"   🚚 Delivery: {product.delivery_info}")
                if product.price_value and max_price:
                    savings = max_price - product.price_value
                    if savings > 0:
                        print(f"   💚 Within budget (AED {savings:.0f} under limit)")
                print(f"   🔗 URL: {product.url}")
    
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
    
    parser = argparse.ArgumentParser(description="Simple Namshi.com Scraper with Price Filtering")
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
            print("   jacket                       # No price limit")
            print("   dress,200                    # Max price AED 200")
            print("   # This is a comment line")
            return
            
        print(f"📝 Found {len(items_to_search)} items in {args.file}")
    
    scraper = SimpleNamshiScraper(headless=args.headless)
    
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
