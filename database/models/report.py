from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Integer, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class Report(BaseModel):
    """Report model for generating and storing reports"""
    
    # Report identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Report categorization
    report_type = Column(String(50), nullable=False, index=True)  # progress, activity, performance, custom, analytics
    category = Column(String(100))  # study, productivity, time_tracking, goals
    tags = Column(Text)  # JSON string of tags
    
    # Report parameters and configuration
    parameters = Column(Text)  # JSON string of report parameters (date range, filters, etc.)
    template_id = Column(String(100))  # report template identifier
    custom_query = Column(Text)  # custom SQL query for complex reports
    
    # Report data and output
    report_data = Column(Text)  # JSON string of processed report data
    file_path = Column(String(500))  # path to generated report file
    file_format = Column(String(20), default='pdf')  # pdf, excel, csv, html, json
    file_size = Column(Integer)  # file size in bytes
    
    # Report generation settings
    is_scheduled = Column(Boolean, default=False, index=True)
    schedule_pattern = Column(String(50))  # daily, weekly, monthly, quarterly, yearly
    schedule_time = Column(String(20))  # time of day to generate (e.g., "09:00")
    last_generated_at = Column(DateTime, index=True)
    next_generation_at = Column(DateTime, index=True)
    
    # Report status and processing
    generation_status = Column(String(20), default='pending', index=True)  # pending, generating, completed, failed
    processing_time = Column(Integer)  # time taken to generate in seconds
    error_message = Column(Text)  # error details if generation failed
    retry_count = Column(Integer, default=0)
    
    # Report delivery and sharing
    delivery_methods = Column(Text)  # JSON string: ['email', 'download', 'webhook', 'api']
    recipients = Column(Text)  # JSON string of recipient emails
    is_public = Column(Boolean, default=False, index=True)
    share_url = Column(String(500))  # public share URL
    
    # Report metadata
    version = Column(String(20), default='1.0')
    language = Column(String(10), default='en')
    timezone = Column(String(50))  # timezone for date/time data
    
    # Relationships
    user = relationship('User', back_populates='reports')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_report_user_type', 'user_id', 'report_type'),
        Index('idx_report_scheduled', 'is_scheduled', 'next_generation_at'),
        Index('idx_report_status_type', 'generation_status', 'report_type'),
        Index('idx_report_generation_time', 'last_generated_at', 'report_type'),
    )
    
    @property
    def is_overdue(self):
        """Check if scheduled report is overdue"""
        if self.is_scheduled and self.next_generation_at:
            from datetime import datetime
            return datetime.utcnow() > self.next_generation_at
        return False
    
    @property
    def needs_generation(self):
        """Check if report needs to be generated"""
        if not self.is_scheduled:
            return False
        
        if not self.next_generation_at:
            return True
        
        from datetime import datetime
        return datetime.utcnow() >= self.next_generation_at
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def processing_time_minutes(self):
        """Get processing time in minutes"""
        if self.processing_time:
            return round(self.processing_time / 60, 2)
        return 0
    
    @property
    def status_icon(self):
        """Get icon for generation status"""
        status_icons = {
            'pending': 'clock',
            'generating': 'spinner',
            'completed': 'check-circle',
            'failed': 'exclamation-triangle'
        }
        return status_icons.get(self.generation_status, 'question-circle')
    
    def __repr__(self):
        return f'<Report {self.title} ({self.report_type}) - {self.generation_status}>'
