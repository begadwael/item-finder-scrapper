#!/usr/bin/env python3
"""
Unified scraper for Noon.com, Namshi.com, and Amazon.ae
"""

import sys
import os
import argparse
import time
from typing import List, Dict, Any

# Add current directory to path so we can import our scrapers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def search_all_sites(search_term: str, max_price: float = None, headless: bool = False):
    """Search Noon, Namshi, and Amazon for the given term"""
    try:
        from simple_noon_scraper import SimpleNoonScraper, SearchItem as NoonSearchItem
        from simple_namshi_scraper import SimpleNamshiScraper, SearchItem as NamshiSearchItem
        from simple_amazon_scraper import SimpleAmazonScraper, SearchItem as AmazonSearchItem
        
        all_results = {}
        
        print(f"🔍 Searching for: {search_term}")
        if max_price:
            print(f"💰 Max price: AED {max_price}")
        print("=" * 60)
        
        # Search Noon.com
        print("\n🛒 Searching NOON.COM...")
        print("-" * 30)
        noon_scraper = SimpleNoonScraper(headless=headless)
        
        try:
            if noon_scraper.setup_driver():
                noon_item = NoonSearchItem(name=search_term, max_price=max_price)
                noon_results = noon_scraper.search_item(noon_item)
                all_results['noon'] = {
                    'site': 'Noon.com',
                    'products': noon_results,
                    'max_price': max_price
                }
                print(f"✅ Found {len(noon_results)} products on Noon")
            else:
                print("❌ Failed to setup Noon scraper")
                all_results['noon'] = {'site': 'Noon.com', 'products': [], 'max_price': max_price}
        except Exception as e:
            print(f"❌ Error searching Noon: {e}")
            all_results['noon'] = {'site': 'Noon.com', 'products': [], 'max_price': max_price}
        finally:
            noon_scraper.close()
        
        # Small delay between sites
        time.sleep(2)
        
        # Search Namshi.com
        print("\n👗 Searching NAMSHI.COM...")
        print("-" * 30)
        namshi_scraper = SimpleNamshiScraper(headless=headless)
        
        try:
            if namshi_scraper.setup_driver():
                namshi_item = NamshiSearchItem(name=search_term, max_price=max_price)
                namshi_results = namshi_scraper.search_item(namshi_item)
                all_results['namshi'] = {
                    'site': 'Namshi.com',
                    'products': namshi_results,
                    'max_price': max_price
                }
                print(f"✅ Found {len(namshi_results)} products on Namshi")
            else:
                print("❌ Failed to setup Namshi scraper")
                all_results['namshi'] = {'site': 'Namshi.com', 'products': [], 'max_price': max_price}
        except Exception as e:
            print(f"❌ Error searching Namshi: {e}")
            all_results['namshi'] = {'site': 'Namshi.com', 'products': [], 'max_price': max_price}
        finally:
            namshi_scraper.close()
        
        # Small delay between sites
        time.sleep(2)
        
        # Search Amazon.ae
        print("\n🛒 Searching AMAZON.AE...")
        print("-" * 30)
        amazon_scraper = SimpleAmazonScraper(headless=headless)
        
        try:
            if amazon_scraper.setup_driver():
                amazon_item = AmazonSearchItem(name=search_term, max_price=max_price)
                amazon_results = amazon_scraper.search_item(amazon_item)
                all_results['amazon'] = {
                    'site': 'Amazon.ae',
                    'products': amazon_results,
                    'max_price': max_price
                }
                print(f"✅ Found {len(amazon_results)} products on Amazon")
            else:
                print("❌ Failed to setup Amazon scraper")
                all_results['amazon'] = {'site': 'Amazon.ae', 'products': [], 'max_price': max_price}
        except Exception as e:
            print(f"❌ Error searching Amazon: {e}")
            all_results['amazon'] = {'site': 'Amazon.ae', 'products': [], 'max_price': max_price}
        finally:
            amazon_scraper.close()
        
        # Small delay after Amazon (they're stricter)
        time.sleep(3)
        
        return all_results
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to install requirements: pip install -r requirements.txt")
        return {}

def print_unified_results(results: Dict[str, Any], search_term: str):
    """Print results from all sites in a unified format"""
    print("\n" + "="*80)
    print("UNIFIED SEARCH RESULTS")
    print("="*80)
    
    total_products = 0
    
    for site_key, data in results.items():
        products = data.get('products', [])
        site_name = data.get('site', site_key.title())
        max_price = data.get('max_price')
        
        print(f"\n🏪 {site_name.upper()}")
        if max_price:
            print(f"💰 Price limit: AED {max_price}")
        print("-" * 60)
        
        if not products:
            if max_price:
                print("❌ No products found within price limit")
            else:
                print("❌ No products found")
            continue
        
        total_products += len(products)
        
        for i, product in enumerate(products, 1):
            print(f"\n{i}. {product.title}")
            print(f"   💰 Price: {product.price}")
            
            # Show brand if available (mainly for Namshi)
            if hasattr(product, 'brand') and product.brand:
                print(f"   🏷️  Brand: {product.brand}")
            
            # Show delivery info if available
            if hasattr(product, 'delivery_info') and product.delivery_info:
                print(f"   🚚 Delivery: {product.delivery_info}")
            
            # Show rating if available (mainly for Noon)
            if hasattr(product, 'rating') and product.rating:
                print(f"   ⭐ Rating: {product.rating}")
            
            # Price analysis
            if product.price_value and max_price:
                if product.price_value <= max_price:
                    savings = max_price - product.price_value
                    print(f"   💚 Within budget (AED {savings:.0f} under limit)")
                else:
                    print(f"   🔴 Over budget (AED {product.price_value - max_price:.0f} over limit)")
            
            print(f"   🔗 URL: {product.url}")
    
    # Summary
    print("\n" + "="*80)
    print("SEARCH SUMMARY")
    print("="*80)
    print(f"🔍 Search term: {search_term}")
    if any(data.get('max_price') for data in results.values()):
        print(f"💰 Price limit: AED {max(data.get('max_price', 0) for data in results.values())}")
    
    for site_key, data in results.items():
        site_name = data.get('site', site_key.title())
        product_count = len(data.get('products', []))
        print(f"🏪 {site_name}: {product_count} products")
    
    print(f"📊 Total products found: {total_products}")

def save_unified_results(results: Dict[str, Any], search_term: str, output_file: str = None):
    """Save unified results to JSON file"""
    import json
    
    if not output_file:
        safe_search_term = "".join(c for c in search_term if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_search_term = safe_search_term.replace(' ', '_')
        output_file = f"unified_search_{safe_search_term}.json"
    
    try:
        serializable_results = {
            'search_term': search_term,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sites': {}
        }
        
        for site_key, data in results.items():
            products = data.get('products', [])
            site_name = data.get('site', site_key.title())
            max_price = data.get('max_price')
            
            serializable_results['sites'][site_key] = {
                'site_name': site_name,
                'max_price_filter': max_price,
                'product_count': len(products),
                'products': [
                    {
                        'title': product.title,
                        'price': product.price,
                        'price_value': product.price_value,
                        'url': product.url,
                        'image_url': getattr(product, 'image_url', None),
                        'rating': getattr(product, 'rating', None),
                        'brand': getattr(product, 'brand', None),
                        'discount': getattr(product, 'discount', None),
                        'delivery_info': getattr(product, 'delivery_info', None),
                        'within_budget': (product.price_value <= max_price) if (max_price and product.price_value) else None
                    }
                    for product in products
                ]
            }
        
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(serializable_results, file, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error saving results: {e}")

def save_unified_results_csv(results: Dict[str, Any], search_term: str, output_file: str = None):
    """Save unified results to CSV file"""
    import csv
    
    if not output_file:
        safe_search_term = "".join(c for c in search_term if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_search_term = safe_search_term.replace(' ', '_')
        output_file = f"unified_search_{safe_search_term}.csv"
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'site', 'title', 'price', 'price_value', 'brand', 'rating', 
                'review_count', 'delivery_info', 'availability', 'discount_info',
                'within_budget', 'url', 'image_url'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data for each site
            for site_key, data in results.items():
                products = data.get('products', [])
                site_name = data.get('site', site_key.title())
                max_price = data.get('max_price')
                
                for product in products:
                    row = {
                        'site': site_name,
                        'title': product.title,
                        'price': product.price,
                        'price_value': product.price_value,
                        'brand': getattr(product, 'brand', ''),
                        'rating': getattr(product, 'rating', ''),
                        'review_count': getattr(product, 'review_count', ''),
                        'delivery_info': getattr(product, 'delivery_info', ''),
                        'availability': getattr(product, 'availability', ''),
                        'discount_info': getattr(product, 'discount_info', ''),
                        'within_budget': (product.price_value <= max_price) if (max_price and product.price_value) else '',
                        'url': product.url,
                        'image_url': getattr(product, 'image_url', '')
                    }
                    writer.writerow(row)
        
        print(f"\n📊 CSV results saved to {output_file}")
        
    except Exception as e:
        print(f"❌ Error saving CSV results: {e}")

def save_results_based_on_format(unified_results, search_term, args):
    """Save results in JSON or CSV format based on user preference"""
    if args.csv:
        output_file = args.output + ".csv" if args.output else None
        save_unified_results_csv(unified_results, search_term, output_file)
    else:
        output_file = args.output + ".json" if args.output else None
        save_unified_results(unified_results, search_term, output_file)

def main():
    parser = argparse.ArgumentParser(description="Unified scraper for Noon.com, Namshi.com, and Amazon.ae")
    parser.add_argument("search_term", help="Item to search for")
    parser.add_argument("--max-price", "-p", type=float, help="Maximum price in AED")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--output", "-o", help="Output file name (without extension)")
    parser.add_argument("--csv", action="store_true", help="Export results as CSV instead of JSON")
    parser.add_argument("--noon-only", action="store_true", help="Search only Noon.com")
    parser.add_argument("--namshi-only", action="store_true", help="Search only Namshi.com")
    parser.add_argument("--amazon-only", action="store_true", help="Search only Amazon.ae")
    
    args = parser.parse_args()
    
    print("🚀 Unified E-commerce Scraper")
    print("=" * 50)
    
    if args.noon_only:
        # Search only Noon
        try:
            from simple_noon_scraper import SimpleNoonScraper, SearchItem
            
            scraper = SimpleNoonScraper(headless=args.headless)
            if scraper.setup_driver():
                item = SearchItem(name=args.search_term, max_price=args.max_price)
                results = scraper.search_item(item)
                
                # Format for unified display
                unified_results = {
                    'noon': {
                        'site': 'Noon.com',
                        'products': results,
                        'max_price': args.max_price
                    }
                }
                
                print_unified_results(unified_results, args.search_term)
                save_results_based_on_format(unified_results, args.search_term, args)
            scraper.close()
            
        except ImportError as e:
            print(f"❌ Error importing Noon scraper: {e}")
    
    elif args.namshi_only:
        # Search only Namshi
        try:
            from simple_namshi_scraper import SimpleNamshiScraper, SearchItem
            
            scraper = SimpleNamshiScraper(headless=args.headless)
            if scraper.setup_driver():
                item = SearchItem(name=args.search_term, max_price=args.max_price)
                results = scraper.search_item(item)
                
                # Format for unified display
                unified_results = {
                    'namshi': {
                        'site': 'Namshi.com',
                        'products': results,
                        'max_price': args.max_price
                    }
                }
                
                print_unified_results(unified_results, args.search_term)
                save_results_based_on_format(unified_results, args.search_term, args)
            scraper.close()
            
        except ImportError as e:
            print(f"❌ Error importing Namshi scraper: {e}")
    
    elif args.amazon_only:
        # Search only Amazon
        try:
            from simple_amazon_scraper import SimpleAmazonScraper, SearchItem
            
            scraper = SimpleAmazonScraper(headless=args.headless)
            if scraper.setup_driver():
                item = SearchItem(name=args.search_term, max_price=args.max_price)
                results = scraper.search_item(item)
                
                # Format for unified display
                unified_results = {
                    'amazon': {
                        'site': 'Amazon.ae',
                        'products': results,
                        'max_price': args.max_price
                    }
                }
                
                print_unified_results(unified_results, args.search_term)
                save_results_based_on_format(unified_results, args.search_term, args)
            scraper.close()
            
        except ImportError as e:
            print(f"❌ Error importing Amazon scraper: {e}")
    
    else:
        # Search all sites
        results = search_all_sites(args.search_term, args.max_price, args.headless)
        
        if results:
            print_unified_results(results, args.search_term)
            save_results_based_on_format(results, args.search_term, args)
            print("\n✅ Search completed successfully!")
        else:
            print("\n❌ Search failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()
