"""
PDF Availability Monitor - Main monitoring script
Monitors refuge PDF availability calendar for changes and availability status
"""

import os
import sys
import hashlib
import logging
import json
from datetime import datetime
from pathlib import Path

import requests
sys.path.append('..')
from bettter_pdf_parser import get_available_nights
from notifier import EmailNotifier


class PDFMonitor:
    def __init__(self):
        self.setup_logging()
        self.pdf_url = "https://www.rifugiopiandicengia.it/CustomerData/764/Files/Documents/verfuegbarkeiten.pdf"
        self.hash_file = Path("data/last_hash.txt")
        self.availability_file = Path("data/availability_count.json")
        
        self.email_from = os.getenv("EMAIL_FROM")
        self.email_to = os.getenv("EMAIL_TO") 
        self.email_password = os.getenv("EMAIL_PASSWORD")
        
        self.notifier = EmailNotifier(self.email_from, self.email_to, self.email_password)
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('monitor.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def download_pdf(self):
        """Download PDF and return content bytes"""
        try:
            self.logger.info(f"Downloading PDF from {self.pdf_url}")
            response = requests.get(self.pdf_url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            self.logger.error(f"Failed to download PDF: {e}")
            raise
    
    def calculate_hash(self, content):
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content).hexdigest()
    
    def get_stored_hash(self):
        """Get previously stored hash if exists"""
        if self.hash_file.exists():
            return self.hash_file.read_text().strip()
        return None
    
    def store_hash(self, hash_value):
        """Store hash to file"""
        self.hash_file.parent.mkdir(parents=True, exist_ok=True)
        self.hash_file.write_text(hash_value)
    
    def get_stored_count(self):
        """Get previously stored available nights count"""
        if self.availability_file.exists():
            try:
                with open(self.availability_file, 'r') as f:
                    data = json.load(f)
                    return data.get('count', 0)
            except:
                return 0
        return 0
    
    def store_count(self, count, nights):
        """Store available nights count and list"""
        self.availability_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'count': count,
            'nights': nights,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.availability_file, 'w') as f:
            json.dump(data, f, indent=2)

    def check_for_changes(self):
        """Main monitoring logic"""
        try:
            # Download current PDF
            pdf_content = self.download_pdf()
            current_hash = self.calculate_hash(pdf_content)
            stored_hash = self.get_stored_hash()
            
            self.logger.info(f"Current hash: {current_hash}")
            self.logger.info(f"Stored hash: {stored_hash}")
            
            # Save PDF temporarily for analysis
            temp_pdf_path = "temp_calendar.pdf"
            with open(temp_pdf_path, 'wb') as f:
                f.write(pdf_content)
            
            # Get available nights using new parser
            available_nights = get_available_nights(temp_pdf_path)
            current_count = len(available_nights)
            stored_count = self.get_stored_count()
            
            self.logger.info(f"Available nights found: {current_count}")
            self.logger.info(f"Previously stored count: {stored_count}")
            
            # Check if PDF has changed OR if we have more available nights
            pdf_changed = current_hash != stored_hash
            more_nights_available = current_count > stored_count
            
            if not pdf_changed and not more_nights_available:
                self.logger.info("No changes detected and no increase in available nights")
                os.remove(temp_pdf_path)
                return False
            
            if pdf_changed:
                self.logger.info("PDF change detected!")
            if more_nights_available:
                self.logger.info(f"More available nights detected! ({stored_count} -> {current_count})")
            
            # Send notification
            self.notifier.send_availability_notification(
                available_nights, current_count, stored_count, pdf_changed
            )
            
            # Update stored data
            self.store_hash(current_hash)
            self.store_count(current_count, available_nights)
            
            # Clean up temp file
            os.remove(temp_pdf_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during monitoring: {e}")
            self.notifier.send_error_notification(str(e))
            return False


def main():
    """Main entry point"""
    monitor = PDFMonitor()
    
    print("Starting PDF Availability Monitor...")
    print(f"PDF URL: {monitor.pdf_url}")
    
    try:
        changed = monitor.check_for_changes()
        if changed:
            print("✅ Changes detected and processed")
        else:
            print("ℹ️  No changes detected")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()