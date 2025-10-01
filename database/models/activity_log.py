from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Integer, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class ActivityLog(BaseModel):
    """Activity log model for tracking user actions and system events"""
    
    # Activity identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)  # login, create_lesson, update_note, etc.
    
    # Activity categorization
    activity_type = Column(String(50), index=True)  # user_action, system_event, error, security
    category = Column(String(100))  # authentication, content, settings, integration
    severity = Column(String(20), default='info', index=True)  # info, warning, error, critical
    
    # Activity context
    entity_type = Column(String(50), index=True)  # lesson, note, task, user, system
    entity_id = Column(String(36), index=True)  # ID of the affected entity
    entity_name = Column(String(200))  # human-readable name of the entity
    
    # Activity details
    description = Column(Text)  # human-readable description
    details = Column(Text)  # JSON string of additional details
    old_values = Column(Text)  # JSON string of previous values (for updates)
    new_values = Column(Text)  # JSON string of new values (for updates)
    
    # Activity metadata
    ip_address = Column(String(45))  # IPv4 or IPv6 address
    user_agent = Column(Text)  # browser/client information
    session_id = Column(String(100))  # user session identifier
    request_id = Column(String(100))  # unique request identifier
    
    # Activity location and context
    location = Column(String(100))  # geographic location if available
    timezone = Column(String(50))  # user timezone
    device_type = Column(String(50))  # desktop, mobile, tablet
    browser = Column(String(100))  # browser name and version
    
    # Activity performance
    response_time = Column(Integer)  # response time in milliseconds
    memory_usage = Column(Integer)  # memory usage in bytes
    cpu_usage = Column(String(20))  # CPU usage percentage
    
    # Activity relationships
    user = relationship('User', back_populates='activity_logs')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_activity_user_action', 'user_id', 'action'),
        Index('idx_activity_type_severity', 'activity_type', 'severity'),
        Index('idx_activity_entity', 'entity_type', 'entity_id'),
        Index('idx_activity_created', 'created_at', 'action'),
        Index('idx_activity_session', 'session_id', 'created_at'),
    )
    
    @property
    def is_error(self):
        """Check if activity is an error"""
        return self.severity in ['error', 'critical']
    
    @property
    def is_warning(self):
        """Check if activity is a warning"""
        return self.severity == 'warning'
    
    @property
    def is_info(self):
        """Check if activity is informational"""
        return self.severity == 'info'
    
    @property
    def is_security_event(self):
        """Check if activity is a security event"""
        return self.activity_type == 'security'
    
    @property
    def is_user_action(self):
        """Check if activity is a user action"""
        return self.activity_type == 'user_action'
    
    @property
    def is_system_event(self):
        """Check if activity is a system event"""
        return self.activity_type == 'system_event'
    
    @property
    def response_time_seconds(self):
        """Get response time in seconds"""
        if self.response_time:
            return round(self.response_time / 1000, 3)
        return 0
    
    @property
    def memory_usage_mb(self):
        """Get memory usage in MB"""
        if self.memory_usage:
            return round(self.memory_usage / (1024 * 1024), 2)
        return 0
    
    def __repr__(self):
        return f'<ActivityLog {self.action} by {self.user_id} ({self.severity})>'
