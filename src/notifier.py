#!/usr/bin/env python3
"""
Email Notification System
Handles email notifications for PDF changes and availability updates
"""

import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional


class EmailNotifier:
    """Email notification handler using Gmail SMTP"""
    
    def __init__(self, email_from: str, email_to: str, password: str):
        self.email_from = email_from
        self.email_to = email_to
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.logger = logging.getLogger(__name__)
    
    def send_change_notification(self, availability_data: Dict[str, Any], 
                               current_hash: str, previous_hash: Optional[str] = None):
        """Send notification when PDF changes are detected"""
        try:
            subject = "🏔️ Rifugio Calendar Updated!"
            
            # Create HTML email content
            html_content = self._create_availability_email(availability_data, current_hash, previous_hash)
            
            # Create plain text version
            text_content = self._create_text_email(availability_data, current_hash, previous_hash)
            
            self._send_email(subject, html_content, text_content)
            self.logger.info("Change notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send change notification: {e}")
            raise
    
    def send_error_notification(self, error_message: str):
        """Send notification when monitoring encounters errors"""
        try:
            subject = "⚠️ Rifugio Monitor Error"
            
            html_content = f"""
            <html>
            <body>
                <h2>Monitoring Error</h2>
                <p>The refuge availability monitor encountered an error:</p>
                <div style="background-color: #ffebee; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <code>{error_message}</code>
                </div>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Please check the system logs for more details.</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Monitoring Error
            
            The refuge availability monitor encountered an error:
            {error_message}
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Please check the system logs for more details.
            """
            
            self._send_email(subject, html_content, text_content)
            self.logger.info("Error notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send error notification: {e}")
    
    def _create_availability_email(self, availability_data: Dict[str, Any], 
                                 current_hash: str, previous_hash: Optional[str]) -> str:
        """Create HTML email content for availability updates"""
        
        timestamp = availability_data.get('timestamp', datetime.now().isoformat())
        method_used = availability_data.get('method_used', 'unknown')
        success = availability_data.get('success', False)
        availability = availability_data.get('availability', {})
        error = availability_data.get('error')
        
        # Status emojis
        status_emojis = {
            'available': '🟢',
            'booked': '🔴', 
            'day_use': '🟡',
            'closed': '⚪',
            'unknown': '❓',
            'error': '❌'
        }
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2e7d32;">🏔️ Rifugio Piandicengia - Calendar Update</h2>
            
            <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3>📅 Availability Status</h3>
        """
        
        if success and availability:
            # Show availability for each target date
            for date, status in availability.items():
                emoji = status_emojis.get(status, '❓')
                date_formatted = datetime.fromisoformat(date).strftime('%B %d, %Y')
                status_text = status.replace('_', ' ').title()
                
                color = {
                    'available': '#4caf50',
                    'booked': '#f44336',
                    'day_use': '#ff9800',
                    'closed': '#9e9e9e',
                    'unknown': '#607d8b',
                    'error': '#f44336'
                }.get(status, '#607d8b')
                
                html_content += f"""
                <div style="margin: 10px 0; padding: 10px; background-color: white; border-left: 4px solid {color}; border-radius: 4px;">
                    <strong>{emoji} {date_formatted}</strong><br>
                    <span style="color: {color}; font-weight: bold;">{status_text}</span>
                </div>
                """
        else:
            html_content += f"""
            <div style="background-color: #fff3cd; padding: 10px; border-radius: 4px; border-left: 4px solid #ffc107;">
                <strong>⚠️ Analysis Status:</strong> Unable to determine availability<br>
                <strong>Method Used:</strong> {method_used}<br>
                {f'<strong>Error:</strong> {error}' if error else ''}
            </div>
            """
        
        html_content += f"""
            </div>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3>🔍 Technical Details</h3>
                <p><strong>Detection Time:</strong> {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Analysis Method:</strong> {method_used}</p>
                <p><strong>PDF Hash:</strong> <code style="font-size: 0.8em;">{current_hash[:16]}...</code></p>
                {f'<p><strong>Previous Hash:</strong> <code style="font-size: 0.8em;">{previous_hash[:16] if previous_hash else "None"}...</code></p>' if previous_hash else ''}
            </div>
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3>🔗 Quick Actions</h3>
                <p>
                    <a href="https://www.rifugiopiandicengia.it/CustomerData/764/Files/Documents/verfuegbarkeiten.pdf" 
                       style="background-color: #1976d2; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        📄 View PDF Calendar
                    </a>
                </p>
                <p>
                    <a href="https://www.rifugiopiandicengia.it/" 
                       style="background-color: #388e3c; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        🏠 Visit Refuge Website
                    </a>
                </p>
            </div>
            
            <p style="color: #666; font-size: 0.9em; margin-top: 20px;">
                This is an automated notification from the Rifugio Availability Monitor.<br>
                Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
            </p>
        </body>
        </html>
        """
        
        return html_content
    
    def _create_text_email(self, availability_data: Dict[str, Any], 
                          current_hash: str, previous_hash: Optional[str]) -> str:
        """Create plain text email content"""
        
        timestamp = availability_data.get('timestamp', datetime.now().isoformat())
        method_used = availability_data.get('method_used', 'unknown')
        success = availability_data.get('success', False)
        availability = availability_data.get('availability', {})
        error = availability_data.get('error')
        
        text_content = f"""
Rifugio Piandicengia - Calendar Update

AVAILABILITY STATUS:
{'=' * 50}
"""
        
        if success and availability:
            for date, status in availability.items():
                date_formatted = datetime.fromisoformat(date).strftime('%B %d, %Y')
                status_text = status.replace('_', ' ').title()
                text_content += f"{date_formatted}: {status_text}\n"
        else:
            text_content += f"Unable to determine availability\nMethod: {method_used}\n"
            if error:
                text_content += f"Error: {error}\n"
        
        text_content += f"""

TECHNICAL DETAILS:
{'=' * 50}
Detection Time: {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')}
Analysis Method: {method_used}
PDF Hash: {current_hash[:16]}...
{f'Previous Hash: {previous_hash[:16] if previous_hash else "None"}...' if previous_hash else ''}

QUICK LINKS:
{'=' * 50}
PDF Calendar: https://www.rifugiopiandicengia.it/CustomerData/764/Files/Documents/verfuegbarkeiten.pdf
Refuge Website: https://www.rifugiopiandicengia.it/

---
This is an automated notification from the Rifugio Availability Monitor.
Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
"""
        
        return text_content
    
    def _send_email(self, subject: str, html_content: str, text_content: str):
        """Send email with both HTML and plain text versions"""
        
        if not all([self.email_from, self.email_to, self.password]):
            raise ValueError("Missing email configuration")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Subject'] = subject
        
        # Attach both versions
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_from, self.password)
            server.send_message(msg)
        
        self.logger.info(f"Email sent to {self.email_to}")
    
    def test_email_connection(self) -> bool:
        """Test email configuration and connection"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.password)
            
            self.logger.info("Email connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Email connection test failed: {e}")
            return False