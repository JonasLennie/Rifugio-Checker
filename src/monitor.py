#!/usr/bin/env python3
"""
PDF Availability Monitor - Main monitoring script
Monitors refuge PDF availability calendar for changes and availability status
"""

import os
import sys
import hashlib
import logging
from datetime import datetime
from pathlib import Path

import requests
from pdf_analyzer import PDFAnalyzer
from notifier import EmailNotifier


class PDFMonitor:
    def __init__(self, config_path="config/settings.yml"):
        self.setup_logging()
        self.pdf_url = "https://www.rifugiopiandicengia.it/CustomerData/764/Files/Documents/verfuegbarkeiten.pdf"
        self.hash_file = Path("data/last_hash.txt")
        self.availability_file = Path("data/availability.json")
        
        self.target_dates = os.getenv("TARGET_DATES", "2025-09-12,2025-09-21").split(",")
        self.email_from = os.getenv("EMAIL_FROM")
        self.email_to = os.getenv("EMAIL_TO") 
        self.email_password = os.getenv("EMAIL_PASSWORD")
        
        self.analyzer = PDFAnalyzer()
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
    
    def check_for_changes(self):
        """Main monitoring logic"""
        try:
            # Download current PDF
            pdf_content = self.download_pdf()
            current_hash = self.calculate_hash(pdf_content)
            stored_hash = self.get_stored_hash()
            
            self.logger.info(f"Current hash: {current_hash}")
            self.logger.info(f"Stored hash: {stored_hash}")
            
            # Check if PDF has changed
            if current_hash == stored_hash:
                self.logger.info("No changes detected in PDF")
                return False
            
            self.logger.info("PDF change detected!")
            
            # Save PDF temporarily for analysis
            temp_pdf_path = "temp_calendar.pdf"
            with open(temp_pdf_path, 'wb') as f:
                f.write(pdf_content)
            
            # Analyze availability for target dates
            availability_data = self.analyzer.analyze_availability(temp_pdf_path, self.target_dates)
            
            # Send notification
            self.notifier.send_change_notification(availability_data, current_hash, stored_hash)
            
            # Update stored hash
            self.store_hash(current_hash)
            
            # Clean up temp file
            os.remove(temp_pdf_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during monitoring: {e}")
            # Send error notification
            self.notifier.send_error_notification(str(e))
            return False


def main():
    """Main entry point"""
    monitor = PDFMonitor()
    
    print("Starting PDF Availability Monitor...")
    print(f"Target dates: {monitor.target_dates}")
    print(f"PDF URL: {monitor.pdf_url}")
    
    try:
        changed = monitor.check_for_changes()
        if changed:
            print("✅ PDF changes detected and processed")
        else:
            print("ℹ️  No changes detected")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()