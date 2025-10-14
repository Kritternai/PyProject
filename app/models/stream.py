"""
Stream System Models
Q&A + Announcements + Activity Timeline
"""

from app import db
from datetime import datetime


class StreamPost(db.Model):
    """
    Stream Post Model - Questions, Announcements, Activities
    
    Types:
    - 'question': Q&A posts (anyone can ask)
    - 'announcement': Announcements (owner only)
    - 'activity': Auto-generated activities (system)
    """
    __tablename__ = 'stream_post'
    
    id = db.Column(db.String, primary_key=True)
    lesson_id = db.Column(db.String, db.ForeignKey('lesson.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Content
    type = db.Column(db.String, nullable=False, default='question')  # question, announcement, activity
    title = db.Column(db.String)
    content = db.Column(db.Text, nullable=False)
    
    # Settings
    is_pinned = db.Column(db.Boolean, default=False)
    allow_comments = db.Column(db.Boolean, default=True)
    
    # Q&A specific
    has_accepted_answer = db.Column(db.Boolean, default=False)
    accepted_answer_id = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    
    # Relationships
    comments = db.relationship('StreamComment', back_populates='post', cascade='all, delete-orphan', lazy='dynamic')
    attachments = db.relationship('StreamAttachment', back_populates='post', cascade='all, delete-orphan', lazy='dynamic')
    
    def to_dict(self, include_author=True, include_comments=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'content': self.content,
            'is_pinned': self.is_pinned,
            'allow_comments': self.allow_comments,
            'has_accepted_answer': self.has_accepted_answer,
            'accepted_answer_id': self.accepted_answer_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'comments_count': self.comments.count() if hasattr(self, 'comments') else 0,
            'attachments_count': self.attachments.count() if hasattr(self, 'attachments') else 0
        }
        
        if include_author and hasattr(self, 'author'):
            data['author'] = {
                'id': self.author.id,
                'name': self.author.name,
                'email': self.author.email
            }
        
        if include_comments and hasattr(self, 'comments'):
            data['comments'] = [comment.to_dict() for comment in self.comments]
        
        if hasattr(self, 'attachments'):
            data['attachments'] = [att.to_dict() for att in self.attachments]
        
        return data


class StreamComment(db.Model):
    """
    Stream Comment Model - Answers/Comments on posts
    """
    __tablename__ = 'stream_comment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.String, db.ForeignKey('stream_post.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)  # For Q&A: is this the accepted answer?
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime)
    
    # Relationships
    post = db.relationship('StreamPost', back_populates='comments')
    
    def to_dict(self, include_author=True):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'is_accepted': self.is_accepted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_author and hasattr(self, 'author'):
            data['author'] = {
                'id': self.author.id,
                'name': self.author.name,
                'email': self.author.email
            }
        
        return data


class StreamAttachment(db.Model):
    """
    Stream Attachment Model - Files/Images attached to posts
    """
    __tablename__ = 'stream_attachment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.String, db.ForeignKey('stream_post.id', ondelete='CASCADE'), nullable=False)
    
    type = db.Column(db.String, nullable=False)  # 'file', 'image', 'link'
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer)  # bytes
    mime_type = db.Column(db.String)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    post = db.relationship('StreamPost', back_populates='attachments')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'type': self.type,
            'name': self.name,
            'url': self.url,
            'size': self.size,
            'mime_type': self.mime_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

