from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class ExternalIntegration(BaseModel):
    """External integration model for platform connections"""
    
    # Integration identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)  # google_classroom, ms_teams, canvas, moodle
    
    # Authentication tokens
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    
    # Platform user information
    platform_user_id = Column(String(100), index=True)
    platform_user_email = Column(String(120))
    platform_user_name = Column(String(200))
    
    # Integration settings
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    auto_sync = Column(Boolean, default=True)
    sync_frequency = Column(String(20), default='daily')  # hourly, daily, weekly, manual
    
    # Sync information
    last_sync_at = Column(DateTime)
    last_sync_status = Column(String(20), default='pending')  # pending, success, failed, partial
    sync_error_count = Column(String(20), default=0)
    last_sync_error = Column(Text)
    
    # Platform-specific settings
    platform_settings = Column(Text)  # JSON string for platform-specific settings
    webhook_url = Column(String(500))  # for webhook-based sync
    api_version = Column(String(20))  # API version being used
    
    # Relationships
    user = relationship('User', back_populates='integrations')
    external_data = relationship('ExternalData', back_populates='integration', cascade='all, delete-orphan')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_integration_user_platform', 'user_id', 'platform'),
        Index('idx_integration_platform_status', 'platform', 'is_active'),
        Index('idx_integration_sync_status', 'last_sync_status', 'is_active'),
    )
    
    @property
    def is_token_expired(self):
        """Check if access token is expired"""
        if self.token_expires_at:
            from datetime import datetime
            return datetime.utcnow() > self.token_expires_at
        return True
    
    @property
    def needs_refresh(self):
        """Check if token needs refresh"""
        if self.token_expires_at:
            from datetime import datetime, timedelta
            # Refresh if expires within 1 hour
            return datetime.utcnow() > (self.token_expires_at - timedelta(hours=1))
        return True
    
    @property
    def sync_status_icon(self):
        """Get icon for sync status"""
        status_icons = {
            'pending': 'clock',
            'success': 'check-circle',
            'failed': 'exclamation-triangle',
            'partial': 'exclamation-circle'
        }
        return status_icons.get(self.last_sync_status, 'question-circle')
    
    def __repr__(self):
        return f'<ExternalIntegration {self.platform} for {self.user_id}>'


class ExternalData(BaseModel):
    """External data model for storing platform data"""
    
    # Data identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    integration_id = Column(String(36), ForeignKey('externalintegration.id'), nullable=False, index=True)
    external_id = Column(String(100), nullable=False, index=True)  # Original ID from external platform
    
    # Data categorization
    data_type = Column(String(50), nullable=False, index=True)  # course, assignment, announcement, material, grade, student
    title = Column(String(200))
    description = Column(Text)
    
    # Data status and metadata
    status = Column(String(50), default='active', index=True)  # active, archived, deleted, draft
    due_date = Column(DateTime, index=True)
    points = Column(String(20))  # for assignments
    max_points = Column(String(20))  # for assignments
    
    # External platform information
    external_url = Column(String(500))
    external_created_at = Column(DateTime)
    external_updated_at = Column(DateTime)
    
    # Raw data and processing
    raw_data = Column(Text)  # JSON string of complete data from external platform
    processed_data = Column(Text)  # JSON string of processed/cleaned data
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    
    # Sync information
    last_synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sync_version = Column(String(20), default='1')  # version of synced data
    
    # Relationships
    user = relationship('User')
    integration = relationship('ExternalIntegration', back_populates='external_data')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_external_data_user_type', 'user_id', 'data_type'),
        Index('idx_external_data_integration_type', 'integration_id', 'data_type'),
        Index('idx_external_data_external_id', 'external_id', 'data_type'),
        Index('idx_external_data_status_due', 'status', 'due_date'),
        Index('idx_external_data_sync_version', 'integration_id', 'sync_version'),
    )
    
    @property
    def is_overdue(self):
        """Check if data is overdue"""
        if self.due_date and self.status == 'active':
            from datetime import datetime
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def is_assignment(self):
        """Check if data is an assignment"""
        return self.data_type == 'assignment'
    
    @property
    def is_course(self):
        """Check if data is a course"""
        return self.data_type == 'course'
    
    @property
    def is_material(self):
        """Check if data is a material"""
        return self.data_type == 'material'
    
    def __repr__(self):
        return f'<ExternalData {self.data_type}:{self.title} from {self.integration_id}>'
