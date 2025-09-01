#!/usr/bin/env python3
"""
Tests for the main monitoring functionality
"""

import os
import sys
import pytest
import tempfile
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monitor import PDFMonitor


class TestPDFMonitor:
    """Test cases for PDFMonitor class"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_env(self):
        """Mock environment variables"""
        env_vars = {
            'EMAIL_FROM': 'test@example.com',
            'EMAIL_TO': 'notify@example.com',
            'EMAIL_PASSWORD': 'test_password',
            'TARGET_DATES': '2025-09-12,2025-09-21'
        }
        
        with patch.dict(os.environ, env_vars):
            yield env_vars
    
    @pytest.fixture
    def monitor(self, mock_env, temp_dir):
        """Create PDFMonitor instance with test configuration"""
        with patch('monitor.Path') as mock_path:
            # Mock file paths to use temp directory
            mock_path.return_value = temp_dir
            
            monitor = PDFMonitor()
            monitor.hash_file = temp_dir / "last_hash.txt"
            monitor.availability_file = temp_dir / "availability.json"
            
            return monitor
    
    def test_initialization(self, mock_env):
        """Test monitor initialization with environment variables"""
        monitor = PDFMonitor()
        
        assert monitor.email_from == 'test@example.com'
        assert monitor.email_to == 'notify@example.com'
        assert monitor.email_password == 'test_password'
        assert monitor.target_dates == ['2025-09-12', '2025-09-21']
        assert 'rifugiopiandicengia.it' in monitor.pdf_url
    
    def test_calculate_hash(self, monitor):
        """Test hash calculation"""
        test_content = b"test content"
        expected_hash = hashlib.sha256(test_content).hexdigest()
        
        result = monitor.calculate_hash(test_content)
        assert result == expected_hash
    
    def test_store_and_get_hash(self, monitor, temp_dir):
        """Test hash storage and retrieval"""
        test_hash = "abcdef123456"
        
        # Test storing hash
        monitor.store_hash(test_hash)
        assert monitor.hash_file.exists()
        
        # Test retrieving hash
        stored_hash = monitor.get_stored_hash()
        assert stored_hash == test_hash
    
    def test_get_stored_hash_no_file(self, monitor):
        """Test getting hash when file doesn't exist"""
        result = monitor.get_stored_hash()
        assert result is None
    
    @patch('monitor.requests.get')
    def test_download_pdf_success(self, mock_get, monitor):
        """Test successful PDF download"""
        mock_response = Mock()
        mock_response.content = b"PDF content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = monitor.download_pdf()
        
        assert result == b"PDF content"
        mock_get.assert_called_once_with(monitor.pdf_url, timeout=30)
    
    @patch('monitor.requests.get')
    def test_download_pdf_failure(self, mock_get, monitor):
        """Test PDF download failure"""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(Exception):
            monitor.download_pdf()
    
    @patch('monitor.PDFMonitor.download_pdf')
    @patch('monitor.PDFAnalyzer')
    @patch('monitor.EmailNotifier')
    def test_check_for_changes_no_change(self, mock_notifier, mock_analyzer, mock_download, monitor):
        """Test check when no changes detected"""
        # Setup
        test_content = b"PDF content"
        test_hash = monitor.calculate_hash(test_content)
        
        mock_download.return_value = test_content
        monitor.store_hash(test_hash)  # Store same hash
        
        # Test
        result = monitor.check_for_changes()
        
        # Verify
        assert result is False
        mock_download.assert_called_once()
        mock_notifier.return_value.send_change_notification.assert_not_called()
    
    @patch('monitor.PDFMonitor.download_pdf')
    @patch('monitor.PDFAnalyzer')
    @patch('monitor.EmailNotifier')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.remove')
    def test_check_for_changes_with_change(self, mock_remove, mock_open, mock_notifier, 
                                          mock_analyzer, mock_download, monitor):
        """Test check when changes are detected"""
        # Setup
        old_content = b"Old PDF content"
        new_content = b"New PDF content"
        old_hash = monitor.calculate_hash(old_content)
        new_hash = monitor.calculate_hash(new_content)
        
        mock_download.return_value = new_content
        monitor.store_hash(old_hash)  # Store old hash
        
        # Mock analyzer
        mock_analyzer_instance = mock_analyzer.return_value
        mock_analyzer_instance.analyze_availability.return_value = {
            'success': True,
            'availability': {'2025-09-12': 'available'}
        }
        
        # Mock notifier
        mock_notifier_instance = mock_notifier.return_value
        
        # Test
        result = monitor.check_for_changes()
        
        # Verify
        assert result is True
        mock_download.assert_called_once()
        mock_analyzer_instance.analyze_availability.assert_called_once()
        mock_notifier_instance.send_change_notification.assert_called_once()
        mock_remove.assert_called_once_with("temp_calendar.pdf")
        
        # Check hash was updated
        stored_hash = monitor.get_stored_hash()
        assert stored_hash == new_hash
    
    @patch('monitor.PDFMonitor.download_pdf')
    @patch('monitor.EmailNotifier')
    def test_check_for_changes_with_error(self, mock_notifier, mock_download, monitor):
        """Test error handling during check"""
        # Setup
        mock_download.side_effect = Exception("Download failed")
        mock_notifier_instance = mock_notifier.return_value
        
        # Test
        result = monitor.check_for_changes()
        
        # Verify
        assert result is False
        mock_notifier_instance.send_error_notification.assert_called_once_with("Download failed")


class TestPDFMonitorIntegration:
    """Integration tests for PDFMonitor"""
    
    @pytest.fixture
    def real_temp_dir(self):
        """Create actual temporary directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_hash_file_operations(self, real_temp_dir):
        """Test actual file operations for hash storage"""
        hash_file = real_temp_dir / "test_hash.txt"
        
        # Create monitor with real file path
        monitor = PDFMonitor()
        monitor.hash_file = hash_file
        
        test_hash = "test_hash_123"
        
        # Store hash
        monitor.store_hash(test_hash)
        assert hash_file.exists()
        
        # Read hash
        stored_hash = monitor.get_stored_hash()
        assert stored_hash == test_hash
        
        # Test with no file
        hash_file.unlink()
        assert monitor.get_stored_hash() is None