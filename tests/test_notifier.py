#!/usr/bin/env python3
"""
Tests for email notification functionality
"""

import os
import sys
import pytest
import smtplib
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from email.mime.multipart import MIMEMultipart

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from notifier import EmailNotifier


class TestEmailNotifier:
    """Test cases for EmailNotifier class"""
    
    @pytest.fixture
    def notifier(self):
        """Create EmailNotifier instance"""
        return EmailNotifier(
            email_from="test@example.com",
            email_to="notify@example.com",
            password="test_password"
        )
    
    @pytest.fixture
    def sample_availability_data(self):
        """Sample availability data for testing"""
        return {
            'timestamp': '2025-01-01T12:00:00',
            'target_dates': ['2025-09-12', '2025-09-15'],
            'method_used': 'text_extraction',
            'availability': {
                '2025-09-12': 'available',
                '2025-09-15': 'booked'
            },
            'success': True,
            'error': None
        }
    
    def test_initialization(self, notifier):
        """Test notifier initialization"""
        assert notifier.email_from == "test@example.com"
        assert notifier.email_to == "notify@example.com"
        assert notifier.password == "test_password"
        assert notifier.smtp_server == "smtp.gmail.com"
        assert notifier.smtp_port == 587
    
    def test_create_availability_email_success(self, notifier, sample_availability_data):
        """Test HTML email creation for successful availability data"""
        html_content = notifier._create_availability_email(
            sample_availability_data, 
            "current_hash_123", 
            "previous_hash_456"
        )
        
        assert isinstance(html_content, str)
        assert '<html>' in html_content
        assert 'Rifugio Piandicengia' in html_content
        assert 'September 12, 2025' in html_content
        assert 'Available' in html_content
        assert 'Booked' in html_content
        assert 'text_extraction' in html_content
        assert 'current_hash_123' in html_content
    
    def test_create_availability_email_failure(self, notifier):
        """Test HTML email creation for failed availability data"""
        failed_data = {
            'timestamp': '2025-01-01T12:00:00',
            'target_dates': ['2025-09-12'],
            'method_used': 'text_extraction',
            'availability': {},
            'success': False,
            'error': 'PDF parsing failed'
        }
        
        html_content = notifier._create_availability_email(
            failed_data,
            "hash_123",
            None
        )
        
        assert 'Unable to determine availability' in html_content
        assert 'PDF parsing failed' in html_content
        assert 'text_extraction' in html_content
    
    def test_create_text_email(self, notifier, sample_availability_data):
        """Test plain text email creation"""
        text_content = notifier._create_text_email(
            sample_availability_data,
            "current_hash_123",
            "previous_hash_456"
        )
        
        assert isinstance(text_content, str)
        assert 'Rifugio Piandicengia' in text_content
        assert 'September 12, 2025: Available' in text_content
        assert 'September 15, 2025: Booked' in text_content
        assert 'text_extraction' in text_content
        assert 'current_hash_123' in text_content
    
    @patch('notifier.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp, notifier):
        """Test successful email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test sending email
        notifier._send_email(
            "Test Subject",
            "<html><body>Test HTML</body></html>",
            "Test plain text"
        )
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test_password")
        mock_server.send_message.assert_called_once()
    
    @patch('notifier.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp, notifier):
        """Test email sending failure"""
        # Mock SMTP to raise exception
        mock_smtp.side_effect = smtplib.SMTPException("SMTP Error")
        
        # Test that exception is raised
        with pytest.raises(smtplib.SMTPException):
            notifier._send_email("Subject", "HTML", "Text")
    
    def test_send_email_missing_config(self):
        """Test email sending with missing configuration"""
        notifier = EmailNotifier(None, "to@example.com", "password")
        
        with pytest.raises(ValueError, match="Missing email configuration"):
            notifier._send_email("Subject", "HTML", "Text")
    
    @patch.object(EmailNotifier, '_send_email')
    def test_send_change_notification(self, mock_send, notifier, sample_availability_data):
        """Test sending change notification"""
        notifier.send_change_notification(
            sample_availability_data,
            "current_hash",
            "previous_hash"
        )
        
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        
        # Check subject
        assert "Rifugio Calendar Updated" in call_args[0][0]
        
        # Check that HTML and text content are provided
        assert len(call_args[0]) == 3  # subject, html, text
    
    @patch.object(EmailNotifier, '_send_email')
    def test_send_error_notification(self, mock_send, notifier):
        """Test sending error notification"""
        error_message = "Test error occurred"
        
        notifier.send_error_notification(error_message)
        
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        
        # Check subject
        assert "Monitor Error" in call_args[0][0]
        
        # Check error message is in content
        html_content = call_args[0][1]
        text_content = call_args[0][2]
        
        assert error_message in html_content
        assert error_message in text_content
    
    @patch('notifier.smtplib.SMTP')
    def test_test_email_connection_success(self, mock_smtp, notifier):
        """Test successful email connection test"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = notifier.test_email_connection()
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test_password")
    
    @patch('notifier.smtplib.SMTP')
    def test_test_email_connection_failure(self, mock_smtp, notifier):
        """Test email connection test failure"""
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")
        
        result = notifier.test_email_connection()
        
        assert result is False
    
    def test_availability_status_formatting(self, notifier):
        """Test that availability statuses are properly formatted"""
        test_data = {
            'timestamp': '2025-01-01T12:00:00',
            'target_dates': ['2025-09-12', '2025-09-15', '2025-09-18', '2025-09-21'],
            'method_used': 'image_analysis',
            'availability': {
                '2025-09-12': 'available',
                '2025-09-15': 'booked',
                '2025-09-18': 'day_use',
                '2025-09-21': 'closed'
            },
            'success': True,
            'error': None
        }
        
        html_content = notifier._create_availability_email(test_data, "hash", None)
        
        # Check that all statuses are properly formatted
        assert '🟢' in html_content  # Available
        assert '🔴' in html_content  # Booked  
        assert '🟡' in html_content  # Day use
        assert '⚪' in html_content  # Closed
        assert 'Available' in html_content
        assert 'Booked' in html_content
        assert 'Day Use' in html_content
        assert 'Closed' in html_content


class TestEmailNotifierIntegration:
    """Integration tests for email notifier"""
    
    def test_email_content_completeness(self):
        """Test that email contains all necessary information"""
        notifier = EmailNotifier("from@test.com", "to@test.com", "password")
        
        availability_data = {
            'timestamp': '2025-09-01T15:30:00',
            'target_dates': ['2025-09-12', '2025-09-15'],
            'method_used': 'text_extraction',
            'availability': {
                '2025-09-12': 'available',
                '2025-09-15': 'unknown'
            },
            'success': True,
            'error': None
        }
        
        html_content = notifier._create_availability_email(
            availability_data, 
            "abcdef123456789",
            "fedcba987654321"
        )
        text_content = notifier._create_text_email(
            availability_data,
            "abcdef123456789", 
            "fedcba987654321"
        )
        
        # Check essential elements in both formats
        for content in [html_content, text_content]:
            assert 'Rifugio' in content
            assert '2025' in content
            assert 'September 12' in content
            assert 'September 15' in content
            assert 'text_extraction' in content
            assert 'abcdef123456' in content  # Hash prefix
        
        # Check HTML-specific elements
        assert '<html>' in html_content
        assert 'href=' in html_content  # Links
        assert 'style=' in html_content  # Styling
        
        # Check text format doesn't have HTML
        assert '<html>' not in text_content
        assert 'href=' not in text_content