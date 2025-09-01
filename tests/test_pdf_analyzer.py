#!/usr/bin/env python3
"""
Tests for PDF analysis functionality
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pdf_analyzer import PDFAnalyzer


class TestPDFAnalyzer:
    """Test cases for PDFAnalyzer class"""
    
    @pytest.fixture
    def analyzer(self):
        """Create PDFAnalyzer instance"""
        return PDFAnalyzer()
    
    @pytest.fixture
    def sample_target_dates(self):
        """Sample target dates for testing"""
        return ['2025-09-12', '2025-09-15', '2025-09-21']
    
    @pytest.fixture
    def temp_pdf_file(self):
        """Create temporary PDF file"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"Mock PDF content")
            temp_path = temp_file.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer.availability_colors is not None
        assert 'available' in analyzer.availability_colors
        assert 'booked' in analyzer.availability_colors
        assert 'day_use' in analyzer.availability_colors
        assert 'closed' in analyzer.availability_colors
    
    def test_analyze_availability_structure(self, analyzer, temp_pdf_file, sample_target_dates):
        """Test analyze_availability returns proper structure"""
        result = analyzer.analyze_availability(temp_pdf_file, sample_target_dates)
        
        # Check required fields
        assert 'timestamp' in result
        assert 'target_dates' in result
        assert 'method_used' in result
        assert 'availability' in result
        assert 'success' in result
        assert 'error' in result
        
        # Check target dates are preserved
        assert result['target_dates'] == sample_target_dates
    
    def test_color_distance(self, analyzer):
        """Test color distance calculation"""
        color1 = (255, 0, 0)  # Red
        color2 = (255, 0, 0)  # Same red
        color3 = (0, 255, 0)  # Green
        
        # Same colors should have distance 0
        assert analyzer._color_distance(color1, color2) == 0
        
        # Different colors should have positive distance
        distance = analyzer._color_distance(color1, color3)
        assert distance > 0
        
        # Distance should be symmetric
        assert analyzer._color_distance(color1, color3) == analyzer._color_distance(color3, color1)
    
    def test_classify_color_available(self, analyzer):
        """Test color classification for available status"""
        green_color = (0, 255, 0)  # Pure green
        result = analyzer._classify_color(green_color)
        assert result == 'available'
    
    def test_classify_color_booked(self, analyzer):
        """Test color classification for booked status"""
        red_color = (255, 0, 0)  # Pure red
        result = analyzer._classify_color(red_color)
        assert result == 'booked'
    
    def test_classify_color_day_use(self, analyzer):
        """Test color classification for day use status"""
        yellow_color = (255, 255, 0)  # Pure yellow
        result = analyzer._classify_color(yellow_color)
        assert result == 'day_use'
    
    def test_classify_color_closed(self, analyzer):
        """Test color classification for closed status"""
        white_color = (255, 255, 255)  # Pure white
        result = analyzer._classify_color(white_color)
        assert result == 'closed'
    
    def test_classify_color_unknown(self, analyzer):
        """Test color classification for unknown colors"""
        weird_color = (123, 45, 67)  # Random color
        result = analyzer._classify_color(weird_color)
        assert result == 'unknown'
    
    @patch('pdf_analyzer.pdfplumber')
    def test_try_text_extraction_no_library(self, mock_pdfplumber, analyzer, temp_pdf_file):
        """Test text extraction when library is not available"""
        mock_pdfplumber = None
        
        results = {}
        result = analyzer._try_text_extraction(temp_pdf_file, results)
        
        assert result is False
    
    @patch('pdf_analyzer.pdfplumber')
    def test_try_text_extraction_success(self, mock_pdfplumber, analyzer, temp_pdf_file, sample_target_dates):
        """Test successful text extraction"""
        # Mock pdfplumber
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "September calendar with 12 available, 15 booked"
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf
        
        # Mock parse method
        with patch.object(analyzer, '_parse_calendar_text') as mock_parse:
            mock_parse.return_value = {'2025-09-12': 'available'}
            
            results = {'target_dates': sample_target_dates}
            result = analyzer._try_text_extraction(temp_pdf_file, results)
            
            assert result is True
            assert results['availability'] == {'2025-09-12': 'available'}
    
    @patch('pdf_analyzer.convert_from_path')
    def test_try_image_analysis_no_library(self, mock_convert, analyzer, temp_pdf_file):
        """Test image analysis when libraries not available"""
        mock_convert = None
        
        results = {}
        result = analyzer._try_image_analysis(temp_pdf_file, results)
        
        assert result is False
    
    @patch('pdf_analyzer.pytesseract')
    @patch('pdf_analyzer.convert_from_path')
    def test_try_ocr_analysis_no_library(self, mock_convert, mock_tesseract, analyzer, temp_pdf_file):
        """Test OCR analysis when libraries not available"""
        mock_tesseract = None
        mock_convert = None
        
        results = {}
        result = analyzer._try_ocr_analysis(temp_pdf_file, results)
        
        assert result is False
    
    def test_parse_calendar_text_basic(self, analyzer):
        """Test basic calendar text parsing"""
        sample_text = """
        September 2025 Calendar
        12 - available for booking
        15 - fully booked
        21 - day use only
        """
        
        target_dates = ['2025-09-12', '2025-09-15', '2025-09-21']
        result = analyzer._parse_calendar_text(sample_text, target_dates)
        
        assert result is not None
        assert isinstance(result, dict)
        
        # Check that all dates have some status
        for date in target_dates:
            assert date in result
    
    def test_parse_calendar_text_empty(self, analyzer):
        """Test parsing empty text"""
        result = analyzer._parse_calendar_text("", ['2025-09-12'])
        
        # Should still return something for the date
        assert result is not None
        assert '2025-09-12' in result
    
    def test_detect_calendar_in_image(self, analyzer):
        """Test calendar detection in image (placeholder)"""
        # This is a placeholder test since the real implementation
        # would require actual image processing
        mock_image = Mock()
        result = analyzer._detect_calendar_in_image(mock_image)
        
        # Current implementation returns True as placeholder
        assert result is True
    
    def test_find_september_calendar(self, analyzer):
        """Test finding September calendar in OCR data"""
        ocr_data = {
            'text': ['January', 'February', 'September', 'October']
        }
        
        result = analyzer._find_september_calendar(ocr_data)
        assert result is True
        
        ocr_data_no_september = {
            'text': ['January', 'February', 'October']
        }
        
        result = analyzer._find_september_calendar(ocr_data_no_september)
        assert result is False


class TestPDFAnalyzerIntegration:
    """Integration tests for PDF analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return PDFAnalyzer()
    
    def test_full_analysis_flow(self, analyzer, sample_target_dates):
        """Test the complete analysis flow with mocked methods"""
        with patch.object(analyzer, '_try_text_extraction') as mock_text, \
             patch.object(analyzer, '_try_image_analysis') as mock_image, \
             patch.object(analyzer, '_try_ocr_analysis') as mock_ocr:
            
            # Test when text extraction succeeds
            mock_text.return_value = True
            mock_image.return_value = False
            mock_ocr.return_value = False
            
            # Mock a successful text extraction that modifies results
            def mock_text_success(pdf_path, results):
                results['availability'] = {'2025-09-12': 'available'}
                return True
            
            mock_text.side_effect = mock_text_success
            
            result = analyzer.analyze_availability("fake_path.pdf", sample_target_dates)
            
            assert result['success'] is True
            assert result['method_used'] == 'text_extraction'
            assert result['availability'] == {'2025-09-12': 'available'}
    
    def test_analysis_all_methods_fail(self, analyzer, sample_target_dates):
        """Test when all analysis methods fail"""
        with patch.object(analyzer, '_try_text_extraction', return_value=False), \
             patch.object(analyzer, '_try_image_analysis', return_value=False), \
             patch.object(analyzer, '_try_ocr_analysis', return_value=False):
            
            result = analyzer.analyze_availability("fake_path.pdf", sample_target_dates)
            
            assert result['success'] is False
            assert result['method_used'] is None
            assert result['error'] == 'All analysis methods failed'