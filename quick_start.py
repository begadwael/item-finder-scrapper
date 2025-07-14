#!/usr/bin/env python3
"""
Quick Start Guide for the Unified Scraper
Interactive helper to run the unified scraper easily
"""

import sys
import os
import subprocess

def main():
    print("🚀 E-commerce Unified Scraper - Quick Start")
    print("=" * 50)
    
    # Get search term
    search_term = input("🔍 What product would you like to search for? ")
    if not search_term.strip():
        print("❌ Please enter a product name")
        return
    
    # Get price limit (optional)
    price_input = input("💰 Maximum price in AED (press Enter to skip): ")
    max_price = None
    if price_input.strip():
        try:
            max_price = float(price_input)
        except ValueError:
            print("⚠️  Invalid price, searching without price limit")
    
    # Ask about site preference
    print("\n🏪 Which sites would you like to search?")
    print("1. All sites (Noon + Namshi + Amazon) - Recommended")
    print("2. Noon.com only (Electronics, general items)")
    print("3. Namshi.com only (Fashion, clothing)")
    print("4. Amazon.ae only (Books, electronics)")
    
    site_choice = input("\nEnter your choice (1-4, default 1): ").strip() or "1"
    
    # Ask about headless mode
    headless_input = input("\n👁️  Run in background (faster, no browser window)? (y/N): ").strip().lower()
    headless = headless_input in ['y', 'yes']
    
    # Ask about output format
    format_input = input("\n📊 Output format (csv/json, default json): ").strip().lower()
    use_csv = format_input in ['csv', 'c']
    
    # Build command
    cmd = ["python3", "unified_scraper.py", search_term]
    
    if max_price:
        cmd.extend(["--max-price", str(max_price)])
    
    if site_choice == "2":
        cmd.append("--noon-only")
    elif site_choice == "3":
        cmd.append("--namshi-only")
    elif site_choice == "4":
        cmd.append("--amazon-only")
    
    if headless:
        cmd.append("--headless")
    
    if use_csv:
        cmd.append("--csv")
    
    # Show command that will be run
    print("\n🔧 Running command:")
    print(" ".join(cmd))
    print("\n" + "="*50)
    
    # Run the scraper
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Search completed successfully!")
        
        # Suggest next steps
        print("\n💡 Next steps:")
        print("1. Check the results above")
        print("2. Look for the saved JSON file with detailed results")
        print("3. Run again with different search terms or price limits")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running scraper: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you've installed requirements: pip install -r requirements.txt")
        print("2. Check that Chrome browser is installed")
        print("3. Try running individual scrapers first")
        
    except KeyboardInterrupt:
        print("\n⚠️ Search interrupted by user")
    except FileNotFoundError:
        print("\n❌ unified_scraper.py not found")
        print("💡 Make sure you're in the correct directory")

if __name__ == "__main__":
    print("Welcome to the E-commerce Scraper!")
    print("This tool searches Noon.com, Namshi.com, and Amazon.ae for products.\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check your setup and try again")
