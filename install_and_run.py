#!/usr/bin/env python3
"""
Complete installer and runner for the Noon Item Finder
This script will install dependencies and run the scraper
"""

import subprocess
import sys
import os
import venv
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def install_and_run():
    """Install dependencies and run the scraper"""
    
    print("🚀 Noon.com Item Finder - Complete Setup")
    print("=" * 50)
    
    # Get the script directory
    script_dir = Path(__file__).parent.absolute()
    venv_dir = script_dir / "venv"
    
    # Check if virtual environment exists
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        venv.create(venv_dir, with_pip=True)
        print("✅ Virtual environment created")
    else:
        print("📦 Virtual environment already exists")
    
    # Determine the correct pip and python paths
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip"
        python_path = venv_dir / "Scripts" / "python"
    else:
        pip_path = venv_dir / "bin" / "pip"
        python_path = venv_dir / "bin" / "python"
    
    # Install requirements
    requirements_file = script_dir / "requirements.txt"
    if requirements_file.exists():
        print("📥 Installing required packages...")
        success, output = run_command(f'"{pip_path}" install -r requirements.txt', cwd=script_dir)
        if success:
            print("✅ Packages installed successfully")
        else:
            print(f"❌ Failed to install packages: {output}")
            return False
    else:
        print("⚠️ requirements.txt not found, installing packages manually...")
        packages = [
            "selenium==4.15.2",
            "webdriver-manager==4.0.1", 
            "beautifulsoup4==4.12.2",
            "requests==2.31.0",
            "fake-useragent==1.4.0",
            "undetected-chromedriver==3.5.4",
            "python-dotenv==1.0.0"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            success, output = run_command(f'"{pip_path}" install {package}')
            if not success:
                print(f"❌ Failed to install {package}: {output}")
                return False
        print("✅ All packages installed")
    
    # Check if items.txt exists
    items_file = script_dir / "items.txt"
    if not items_file.exists():
        print("\n📝 Creating sample items.txt file...")
        sample_items = [
            "iPhone 15 Pro",
            "Samsung Galaxy S24", 
            "Apple MacBook Air M2",
            "Sony WH-1000XM5 headphones",
            "Nintendo Switch OLED"
        ]
        
        with open(items_file, 'w') as f:
            f.write('\n'.join(sample_items))
        print("✅ Sample items.txt created")
    
    # Ask user what they want to do
    print("\n🎯 What would you like to do?")
    print("1. Run a quick test (single item)")
    print("2. Search all items from items.txt") 
    print("3. Test price filtering with items_with_prices.txt")
    print("4. Search a custom item with price limit")
    print("5. Search a custom item without price limit")
    print("6. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            # Quick test
            test_item = "iPhone 15"
            print(f"\n🧪 Running quick test with: {test_item}")
            command = f'"{python_path}" simple_noon_scraper.py --single "{test_item}"'
            break
            
        elif choice == "2":
            # Search all items
            print(f"\n🔍 Searching all items from items.txt")
            command = f'"{python_path}" simple_noon_scraper.py --file items.txt'
            break
            
        elif choice == "3":
            # Test price filtering
            print(f"\n💰 Testing price filtering with items_with_prices.txt")
            print("This file contains items with maximum price limits.")
            command = f'"{python_path}" simple_noon_scraper.py --file items_with_prices.txt'
            break
            
        elif choice == "4":
            # Custom item with price
            item_name = input("Enter item name: ").strip()
            while True:
                try:
                    max_price = float(input("Enter maximum price (AED): ").strip())
                    break
                except ValueError:
                    print("Please enter a valid number for the price.")
            
            print(f"\n🔍 Searching for: {item_name} (max price: AED {max_price})")
            command = f'"{python_path}" simple_noon_scraper.py --single "{item_name},{max_price}"'
            break
            
        elif choice == "5":
            # Custom item without price
            item_name = input("Enter item name: ").strip()
            print(f"\n🔍 Searching for: {item_name} (no price limit)")
            command = f'"{python_path}" simple_noon_scraper.py --single "{item_name}"'
            break
            
        elif choice == "6":
            print(" Goodbye!")
            return True
            
        else:
            print("❌ Invalid choice. Please enter 1-6")
            continue
    
    # Ask about headless mode
    headless_choice = input("\nRun in headless mode (no browser window)? (y/N): ").strip().lower()
    if headless_choice in ['y', 'yes']:
        command += " --headless"
    
    print(f"\n🚀 Running command: {command}")
    print("Note: This will open a browser window and start scraping...")
    print("Press Ctrl+C to stop at any time\n")
    
    # Run the scraper
    try:
        result = subprocess.run(command, shell=True, cwd=script_dir)
        if result.returncode == 0:
            print("\n✅ Scraping completed successfully!")
            
            # Show output files
            output_files = []
            for file_pattern in ["search_results.json", "noon_scraper.log"]:
                file_path = script_dir / file_pattern
                if file_path.exists():
                    output_files.append(str(file_path))
            
            if output_files:
                print("\n📄 Output files created:")
                for file_path in output_files:
                    print(f"   - {file_path}")
        else:
            print(f"\n❌ Scraping failed with exit code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running scraper: {str(e)}")
    
    return True

def main():
    """Main function"""
    try:
        install_and_run()
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")

if __name__ == "__main__":
    main()
