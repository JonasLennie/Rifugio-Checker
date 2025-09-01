"""
PDF Analyzer - Multi-method PDF availability analysis
Implements hybrid approach: text extraction, image analysis, and OCR
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    PyPDF2 = None
    pdfplumber = None

try:
    from pdf2image import convert_from_path
    from PIL import Image, ImageDraw
    import numpy as np
except ImportError:
    convert_from_path = None
    Image = None
    np = None

try:
    import pytesseract
except ImportError:
    pytesseract = None


class PDFAnalyzer:
    """Multi-method PDF analysis for availability detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.availability_colors = {
            'available': [(0, 255, 0), (50, 255, 50)],     # Green ranges
            'booked': [(255, 0, 0), (255, 50, 50)],        # Red ranges  
            'day_use': [(255, 255, 0), (255, 255, 100)],   # Yellow ranges
            'closed': [(255, 255, 255), (240, 240, 240)]   # White ranges
        }
    
    def analyze_availability(self, pdf_path: str, target_dates: List[str]) -> Dict[str, Any]:
        """Main analysis method - tries multiple approaches"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'target_dates': target_dates,
            'method_used': None,
            'availability': {},
            'success': False,
            'error': None
        }
        
        try:
            # Method 1: Text extraction
            if self._try_text_extraction(pdf_path, results):
                results['method_used'] = 'text_extraction'
                results['success'] = True
                return results
            
            # Method 2: Image analysis  
            if self._try_image_analysis(pdf_path, results):
                results['method_used'] = 'image_analysis'
                results['success'] = True
                return results
            
            # Method 3: OCR + coordinate mapping
            if self._try_ocr_analysis(pdf_path, results):
                results['method_used'] = 'ocr_analysis'
                results['success'] = True
                return results
            
            # All methods failed
            results['error'] = 'All analysis methods failed'
            
        except Exception as e:
            results['error'] = str(e)
            self.logger.error(f"Analysis failed: {e}")
        
        return results
    
    def _try_text_extraction(self, pdf_path: str, results: Dict) -> bool:
        """Method 1: Extract text and parse calendar structure"""
        if not pdfplumber:
            self.logger.info("pdfplumber not available, skipping text extraction")
            return False
        
        try:
            self.logger.info("Attempting text extraction method")
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if text and 'september' in text.lower():
                        self.logger.info(f"Found September calendar on page {page_num + 1}")
                        
                        # Parse calendar text structure
                        availability = self._parse_calendar_text(text, results['target_dates'])
                        if availability:
                            results['availability'] = availability
                            return True
            
            self.logger.info("No calendar structure found in text")
            return False
            
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return False
    
    def _try_image_analysis(self, pdf_path: str, results: Dict) -> bool:
        """Method 2: Convert to image and analyze colors"""
        if not convert_from_path or not np:
            self.logger.info("Image analysis libraries not available")
            return False
        
        try:
            self.logger.info("Attempting image analysis method")
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=200)
            
            for page_num, image in enumerate(images):
                # Look for calendar pattern
                if self._detect_calendar_in_image(image):
                    self.logger.info(f"Found calendar on page {page_num + 1}")
                    
                    # Analyze availability colors
                    availability = self._analyze_calendar_colors(image, results['target_dates'])
                    if availability:
                        results['availability'] = availability
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            return False
    
    def _try_ocr_analysis(self, pdf_path: str, results: Dict) -> bool:
        """Method 3: OCR + coordinate mapping"""
        if not pytesseract or not convert_from_path:
            self.logger.info("OCR libraries not available")
            return False
        
        try:
            self.logger.info("Attempting OCR analysis method")
            
            images = convert_from_path(pdf_path, dpi=300)
            
            for page_num, image in enumerate(images):
                # Extract text with coordinates
                ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                
                # Find September calendar
                if self._find_september_calendar(ocr_data):
                    availability = self._map_coordinates_to_dates(image, ocr_data, results['target_dates'])
                    if availability:
                        results['availability'] = availability
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"OCR analysis failed: {e}")
            return False
    
    def _parse_calendar_text(self, text: str, target_dates: List[str]) -> Optional[Dict]:
        """Parse calendar from extracted text"""
        availability = {}
        
        # Basic text parsing - would need customization based on actual PDF format
        lines = text.split('\n')
        
        for date_str in target_dates:
            try:
                # Extract day from date (e.g., "2025-09-12" -> "12")
                day = date_str.split('-')[-1].lstrip('0')
                
                # Look for patterns indicating availability
                for line in lines:
                    if day in line:
                        if any(word in line.lower() for word in ['available', 'free', 'verfügbar']):
                            availability[date_str] = 'available'
                        elif any(word in line.lower() for word in ['booked', 'full', 'ausgebucht']):
                            availability[date_str] = 'booked'
                        elif any(word in line.lower() for word in ['day', 'tag']):
                            availability[date_str] = 'day_use'
                        else:
                            availability[date_str] = 'unknown'
                        break
                else:
                    availability[date_str] = 'unknown'
                    
            except Exception as e:
                self.logger.error(f"Error parsing date {date_str}: {e}")
                availability[date_str] = 'error'
        
        return availability if availability else None
    
    def _detect_calendar_in_image(self, image) -> bool:
        """Detect if image contains a calendar"""
        # Simple heuristic - look for grid patterns
        # This would need refinement based on actual calendar layout
        return True  # Placeholder
    
    def _analyze_calendar_colors(self, image, target_dates: List[str]) -> Optional[Dict]:
        """Analyze colors in calendar grid"""
        availability = {}
        
        # This is a simplified implementation
        # Real implementation would need calendar grid detection
        for date_str in target_dates:
            # Placeholder logic - would need actual coordinate mapping
            availability[date_str] = 'unknown'
        
        return availability
    
    def _find_september_calendar(self, ocr_data: Dict) -> bool:
        """Find September calendar in OCR data"""
        texts = ocr_data.get('text', [])
        return any('september' in text.lower() for text in texts if text)
    
    def _map_coordinates_to_dates(self, image, ocr_data: Dict, target_dates: List[str]) -> Optional[Dict]:
        """Map date coordinates to availability colors"""
        availability = {}
        
        # Placeholder implementation
        for date_str in target_dates:
            availability[date_str] = 'unknown'
        
        return availability
    
    def _color_distance(self, color1, color2):
        """Calculate color distance"""
        return sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)) ** 0.5
    
    def _classify_color(self, rgb_color):
        """Classify RGB color to availability status"""
        min_distance = float('inf')
        best_status = 'unknown'
        
        for status, color_ranges in self.availability_colors.items():
            for color_range in color_ranges:
                distance = self._color_distance(rgb_color, color_range)
                if distance < min_distance:
                    min_distance = distance
                    best_status = status
        
        # Only classify if color is close enough (threshold)
        return best_status if min_distance < 50 else 'unknown'