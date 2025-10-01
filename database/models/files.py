from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, Integer, Index
from sqlalchemy.orm import relationship
from .base import BaseModel

class Files(BaseModel):
    """Files model for managing file attachments"""
    
    # File identification
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # File metadata
    file_type = Column(String(50), index=True)  # image, document, video, audio, archive, other
    mime_type = Column(String(100))
    file_size = Column(Integer)  # bytes
    file_extension = Column(String(20))
    
    # File categorization
    category = Column(String(100))  # lesson, note, task, profile, general
    tags = Column(Text)  # JSON string of tags
    description = Column(Text)
    
    # File relationships
    lesson_id = Column(String(36), ForeignKey('lesson.id'), index=True)
    section_id = Column(String(36), ForeignKey('lessonsection.id'), index=True)
    note_id = Column(String(36), ForeignKey('note.id'), index=True)
    task_id = Column(String(36), ForeignKey('task.id'), index=True)
    
    # File settings
    is_public = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False, index=True)
    download_count = Column(Integer, default=0)
    
    # External integration
    external_url = Column(String(500))  # Google Drive, OneDrive, etc.
    external_id = Column(String(100))
    source_platform = Column(String(50))  # local, google_drive, onedrive, dropbox
    
    # File processing
    is_processed = Column(Boolean, default=False)  # for image processing, OCR, etc.
    processing_status = Column(String(50), default='pending')  # pending, processing, completed, failed
    processing_metadata = Column(Text)  # JSON string for processing results
    
    # Security and access
    access_level = Column(String(20), default='private')  # private, shared, public
    password_protected = Column(Boolean, default=False)
    encryption_key = Column(String(255))  # for encrypted files
    
    # Relationships
    user = relationship('User', back_populates='files')
    lesson = relationship('Lesson', back_populates='files')
    section = relationship('LessonSection', back_populates='files')
    note = relationship('Note', back_populates='files')
    task = relationship('Task', back_populates='files')
    
    # Composite indexes
    __table_args__ = (
        Index('idx_files_user_category', 'user_id', 'category'),
        Index('idx_files_type_size', 'file_type', 'file_size'),
        Index('idx_files_lesson_section', 'lesson_id', 'section_id'),
        Index('idx_files_public_archived', 'is_public', 'is_archived'),
        Index('idx_files_platform_external', 'source_platform', 'external_id'),
    )
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def file_size_kb(self):
        """Get file size in KB"""
        if self.file_size:
            return round(self.file_size / 1024, 2)
        return 0
    
    @property
    def is_image(self):
        """Check if file is an image"""
        return self.file_type in ['image', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    
    @property
    def is_document(self):
        """Check if file is a document"""
        return self.file_type in ['document', 'pdf', 'doc', 'docx', 'txt', 'rtf']
    
    @property
    def is_video(self):
        """Check if file is a video"""
        return self.file_type in ['video', 'mp4', 'avi', 'mov', 'wmv', 'flv']
    
    @property
    def is_audio(self):
        """Check if file is an audio file"""
        return self.file_type in ['audio', 'mp3', 'wav', 'flac', 'aac', 'ogg']
    
    @property
    def is_archive(self):
        """Check if file is an archive"""
        return self.file_type in ['archive', 'zip', 'rar', '7z', 'tar', 'gz']
    
    def __repr__(self):
        return f"<Files '{self.file_name}' ({self.file_type})>"
