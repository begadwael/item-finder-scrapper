"""
Simple and working Amazon.ae scraper
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
    review_count: Optional[str] = None
    delivery_info: Optional[str] = None
    availability: Optional[str] = None
    discount_info: Optional[str] = None

@dataclass
class SearchItem:
    """Data class to store search item with optional price limit"""
    name: str
    max_price: Optional[float] = None

class SimpleAmazonScraper:
    """Simple working Amazon.ae scraper"""
    
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
            
            # Amazon-specific options to avoid detection
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
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
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup driver: {str(e)}")
            return False
    
    def search_item(self, search_item: SearchItem) -> List[ProductInfo]:
        """Search for an item on amazon.ae with optional price filtering"""
        try:
            products = []
            item_name = search_item.name
            max_price = search_item.max_price
            
            search_query = quote_plus(item_name.strip())
            search_url = f"https://www.amazon.ae/s?k={search_query}&ref=nb_sb_noss"
            
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
            
            # Check for error pages or captcha
            if "robot" in page_title.lower() or "captcha" in page_title.lower():
                self.logger.error("Captcha or robot detection triggered")
                return products
            
            # Look for product elements using Amazon-specific selectors
            self.logger.info("Looking for product elements...")
            
            # Wait a bit more for dynamic content to load
            time.sleep(3)
            
            # Amazon-specific product container selectors based on your HTML
            product_selectors = [
                "[data-component-type='s-search-result']",  # Main search result container
                ".s-result-item",  # Alternative search result item
                "[data-asin]",  # Elements with ASIN attribute
                ".s-card-container",  # Card containers
                ".s-widget-container"  # Widget containers
            ]
            
            potential_products = []
            
            for selector in product_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    if elements:
                        # Filter out empty or invalid elements
                        valid_elements = []
                        for element in elements:
                            try:
                                text = element.text.strip()
                                # Check if element has substantial content
                                if len(text) > 30 and any(keyword in text.lower() for keyword in ['aed', 'price', item_name.lower()]):
                                    valid_elements.append(element)
                            except:
                                continue
                        
                        if valid_elements:
                            potential_products = valid_elements
                            self.logger.info(f"Found {len(valid_elements)} valid product elements")
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
                        # Look for divs that contain Amazon product-like content
                        if (100 < len(text) < 1500 and 
                            any(keyword.lower() in text.lower() for keyword in [
                                'aed', 'delivery', 'prime', 'add to cart', item_name.lower()
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
                    product_info = self.extract_amazon_product_info(element, item_name)
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
    
    def extract_amazon_product_info(self, element, search_term: str) -> Optional[ProductInfo]:
        """Extract product information using Amazon-specific selectors"""
        try:
            # Get all text from the element
            full_text = element.text.strip()
            
            if len(full_text) < 20:
                return None
            
            # Extract title using Amazon-specific selectors
            title = None
            title_selectors = [
                "h2 a span",  # Main title from your HTML
                ".a-size-base-plus",  # Size class from your HTML
                "h2.a-size-base-plus span",  # More specific
                "[data-cy='title-recipe'] h2 span",  # Data attribute from your HTML
                "h2 span",  # Generic h2 span
                ".s-line-clamp-4 span",  # Line clamp class
                "a[class*='s-link-style'] span"  # Link style class
            ]
            
            for selector in title_selectors:
                try:
                    title_element = element.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip()
                    if title and len(title) > 10:
                        break
                except:
                    continue
            
            # Fallback to text parsing if no title found
            if not title:
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                for line in lines:
                    if (len(line) > 10 and len(line) < 200 and
                        not line.replace('.', '').replace(',', '').replace(' ', '').isdigit() and
                        'aed' not in line.lower() and
                        '%' not in line and
                        'delivery' not in line.lower() and
                        'add to cart' not in line.lower() and
                        'only' not in line.lower() and
                        'left' not in line.lower()):
                        title = line
                        break
            
            if not title:
                title = "Unknown Product"
            
            # Clean title
            title = re.sub(r'\s+', ' ', title).strip()
            if len(title) > 150:
                title = title[:150] + "..."
            
            # Extract price using Amazon-specific selectors
            price = "Price not available"
            price_value = None
            
            # Amazon-specific price selectors from your HTML
            price_selectors = [
                ".a-price-whole",  # Whole price part from your HTML
                ".a-price .a-price-whole",  # More specific
                "[data-cy='price-recipe'] .a-price-whole",  # Data attribute
                ".a-price-symbol + .a-price-whole",  # After currency symbol
                ".a-offscreen",  # Screen reader price
                "[class*='a-price'] .a-price-whole"  # Flexible price class
            ]
            
            for selector in price_selectors:
                try:
                    price_element = element.find_element(By.CSS_SELECTOR, selector)
                    whole_price = price_element.text.strip()
                    
                    # Try to get fraction part
                    try:
                        fraction_element = element.find_element(By.CSS_SELECTOR, ".a-price-fraction")
                        fraction = fraction_element.text.strip()
                        price_text = f"{whole_price}.{fraction}"
                    except:
                        price_text = whole_price
                    
                    if price_text and re.match(r'^\d+(\.\d+)?$', price_text.replace(',', '')):
                        price = f"AED {price_text}"
                        price_value = float(price_text.replace(',', ''))
                        break
                except:
                    continue
            
            # Fallback: try to extract from offscreen text (screen reader text)
            if price == "Price not available":
                try:
                    offscreen_elements = element.find_elements(By.CSS_SELECTOR, ".a-offscreen")
                    for offscreen in offscreen_elements:
                        offscreen_text = offscreen.text.strip()
                        if 'aed' in offscreen_text.lower():
                            # Extract price from "AED 229.00" format
                            price_match = re.search(r'aed[^\d]*(\d+(?:\.\d+)?)', offscreen_text.lower())
                            if price_match:
                                price_num = price_match.group(1)
                                price = f"AED {price_num}"
                                price_value = float(price_num)
                                break
                except:
                    pass
            
            # Extract rating using Amazon-specific selectors
            rating = None
            rating_selectors = [
                ".a-icon-alt",  # Rating alt text from your HTML
                "[data-cy='reviews-block'] .a-size-small",  # Reviews block
                ".a-icon-star-mini .a-icon-alt",  # Star mini alt text
                "[aria-label*='out of 5 stars']"  # Aria label
            ]
            
            for selector in rating_selectors:
                try:
                    rating_element = element.find_element(By.CSS_SELECTOR, selector)
                    rating_text = rating_element.text.strip()
                    if not rating_text:
                        rating_text = rating_element.get_attribute("aria-label") or ""
                    
                    # Extract rating number from text like "4.6 out of 5 stars"
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating_val = float(rating_match.group(1))
                        if 0 <= rating_val <= 5:
                            rating = str(rating_val)
                            break
                except:
                    continue
            
            # Extract review count
            review_count = None
            review_selectors = [
                "[aria-label*='ratings']",  # From your HTML
                ".s-underline-text",  # Underline text class
                "a[aria-label*='ratings']"  # Link with ratings aria label
            ]
            
            for selector in review_selectors:
                try:
                    review_element = element.find_element(By.CSS_SELECTOR, selector)
                    review_text = review_element.get_attribute("aria-label") or review_element.text.strip()
                    
                    # Extract number from text like "91,260 ratings" or "(91.2K)"
                    if 'rating' in review_text.lower():
                        review_match = re.search(r'([\d,]+(?:\.\d+)?[kK]?)', review_text)
                        if review_match:
                            review_count = review_match.group(1)
                            break
                except:
                    continue
            
            # Extract delivery information
            delivery_info = None
            delivery_selectors = [
                "[data-cy='delivery-recipe']",  # From your HTML
                ".udm-delivery-block",  # Delivery block
                "[class*='delivery']",  # Any delivery class
                ".a-text-bold"  # Bold text (often delivery dates)
            ]
            
            for selector in delivery_selectors:
                try:
                    delivery_element = element.find_element(By.CSS_SELECTOR, selector)
                    delivery_text = delivery_element.text.strip()
                    if delivery_text and len(delivery_text) < 100 and ('delivery' in delivery_text.lower() or 'tomorrow' in delivery_text.lower() or 'prime' in delivery_text.lower()):
                        delivery_info = delivery_text
                        break
                except:
                    continue
            
            # Extract availability/stock information
            availability = None
            availability_selectors = [
                ".a-color-price",  # Price color class (often used for stock info)
                "[class*='stock']",  # Stock related classes
                ".a-size-base.a-color-secondary"  # Secondary text
            ]
            
            for selector in availability_selectors:
                try:
                    availability_element = element.find_element(By.CSS_SELECTOR, selector)
                    availability_text = availability_element.text.strip()
                    if availability_text and ('left' in availability_text.lower() or 'stock' in availability_text.lower()):
                        availability = availability_text
                        break
                except:
                    continue
            
            # Extract discount information
            discount_info = None
            discount_selectors = [
                ".a-color-secondary",  # Secondary color (often discounts)
                "[class*='discount']",  # Discount classes
                "[class*='off']"  # Off/sale classes
            ]
            
            for selector in discount_selectors:
                try:
                    discount_element = element.find_element(By.CSS_SELECTOR, selector)
                    discount_text = discount_element.text.strip()
                    if discount_text and ('off' in discount_text.lower() or '%' in discount_text):
                        discount_info = discount_text
                        break
                except:
                    continue
            
            # Extract URL
            url = f"https://www.amazon.ae/s?k={quote_plus(search_term)}"
            
            # Look for product links
            link_selectors = [
                "a[href*='/dp/']",  # Amazon product links
                ".s-link-style",  # Link style class
                "h2 a",  # Title links
                "a[class*='s-link']"  # Any s-link class
            ]
            
            for selector in link_selectors:
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, selector)
                    href = link_element.get_attribute("href")
                    if href and "/dp/" in href:
                        if href.startswith("/"):
                            url = f"https://www.amazon.ae{href}"
                        elif href.startswith("http"):
                            url = href
                        break
                except:
                    continue
            
            # Extract image URL
            image_url = None
            image_selectors = [
                "img[src*='images-amazon']",  # Amazon CDN images
                ".s-image",  # Search image class
                "img[data-src*='amazon']",  # Lazy loaded images
                "img:not([src*='transparent']):not([src*='spinner'])"  # Valid images
            ]
            
            for selector in image_selectors:
                try:
                    img_element = element.find_element(By.CSS_SELECTOR, selector)
                    src = img_element.get_attribute("src") or img_element.get_attribute("data-src")
                    if src and src.startswith("http") and "transparent" not in src:
                        image_url = src
                        break
                except:
                    continue
            
            self.logger.info(f"Extracted: {title[:30]}... | Price: {price} | Rating: {rating}")
            
            return ProductInfo(
                title=title,
                price=price,
                url=url,
                image_url=image_url,
                rating=rating,
                price_value=price_value,
                review_count=review_count,
                delivery_info=delivery_info,
                availability=availability,
                discount_info=discount_info
            )
            
        except Exception as e:
            self.logger.warning(f"Error in extraction: {str(e)}")
            return None
    
    def save_results(self, results: dict, output_file: str = "amazon_search_results.json"):
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
                            'review_count': product.review_count,
                            'delivery_info': product.delivery_info,
                            'availability': product.availability,
                            'discount_info': product.discount_info,
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
    
    def save_results_csv(self, results: dict, output_file: str = "amazon_search_results.csv"):
        """Save results to CSV file with price filtering information"""
        import csv
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'search_term', 'title', 'price', 'price_value', 'rating', 'review_count',
                    'delivery_info', 'availability', 'discount_info', 'within_budget', 'url', 'image_url'
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
                            'review_count': product.review_count or '',
                            'delivery_info': product.delivery_info or '',
                            'availability': product.availability or '',
                            'discount_info': product.discount_info or '',
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
        print("AMAZON.AE SEARCH RESULTS")
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
                if product.rating:
                    rating_display = f"⭐ {product.rating}"
                    if product.review_count:
                        rating_display += f" ({product.review_count} reviews)"
                    print(f"   {rating_display}")
                if product.delivery_info:
                    print(f"   🚚 Delivery: {product.delivery_info}")
                if product.availability:
                    print(f"   📦 Stock: {product.availability}")
                if product.discount_info:
                    print(f"   💸 Offer: {product.discount_info}")
                if product.price_value and max_price:
                    if product.price_value <= max_price:
                        savings = max_price - product.price_value
                        print(f"   💚 Within budget (AED {savings:.0f} under limit)")
                    else:
                        print(f"   🔴 Over budget")
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
    
    parser = argparse.ArgumentParser(description="Simple Amazon.ae Scraper with Price Filtering")
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
    
    scraper = SimpleAmazonScraper(headless=args.headless)
    
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
                delay = 5  # 5 second delay between searches (Amazon is stricter)
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
