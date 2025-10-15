#!/usr/bin/env python3
"""
Unit tests for NoteModel class.
Single Responsibility: Test NoteModel database operations only.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../base'))

from base.base_test import BaseNoteTest


class NoteModelTest(BaseNoteTest):
    """
    Unit tests for NoteModel.
    Follows SRP: Tests only NoteModel functionality.
    """
    
    def __init__(self):
        super().__init__()
        self.app = None
        self.db = None
        self.note_model = None
    
    def run_tests(self) -> bool:
        """Run all NoteModel tests."""
        print("=" * 60)
        print("NOTE MODEL UNIT TESTS")
        print("=" * 60)
        
        # Setup
        if not self.setup_app():
            return False
        
        # Run tests
        self.test_model_import()
        self.test_database_connection()
        self.test_model_structure()
        self.test_model_operations()
        
        return self.print_summary()
    
    def setup_app(self):
        """Setup Flask app and database."""
        try:
            from app import create_app, db
            self.app = create_app()
            self.db = db
            
            with self.app.app_context():
                from app.models.note import NoteModel
                self.note_model = NoteModel
            
            return True
        except Exception as e:
            self.log_test_result("App Setup", False, f"Error: {e}")
            return False
    
    def test_model_import(self):
        """Test if NoteModel can be imported."""
        try:
            with self.app.app_context():
                from app.models.note import NoteModel
                success = NoteModel is not None
                self.log_test_result("Model Import", success)
                return success
        except Exception as e:
            self.log_test_result("Model Import", False, f"Error: {e}")
            return False
    
    def test_database_connection(self):
        """Test database connection and table existence."""
        try:
            with self.app.app_context():
                # Test if we can query the note table
                note_count = self.note_model.query.count()
                success = isinstance(note_count, int)
                self.log_test_result("Database Connection", success, f"Found {note_count} notes")
                return success
        except Exception as e:
            self.log_test_result("Database Connection", False, f"Error: {e}")
            return False
    
    def test_model_structure(self):
        """Test NoteModel structure and attributes."""
        try:
            with self.app.app_context():
                # Check if model has required attributes
                required_attrs = ['id', 'title', 'content', 'user_id', 'created_at', 'updated_at']
                missing_attrs = []
                
                # Create a sample note to check attributes
                sample_note = self.note_model()
                for attr in required_attrs:
                    if not hasattr(sample_note, attr):
                        missing_attrs.append(attr)
                
                success = len(missing_attrs) == 0
                self.log_test_result("Model Structure", success)
                
                if missing_attrs:
                    self.log_test_result("Model Structure", False, f"Missing attributes: {missing_attrs}")
                
                return success
        except Exception as e:
            self.log_test_result("Model Structure", False, f"Error: {e}")
            return False
    
    def test_model_operations(self):
        """Test basic model operations."""
        try:
            with self.app.app_context():
                from app.models.user import UserModel
                
                # Get a test user
                test_user = UserModel.query.first()
                if not test_user:
                    self.log_skip("Model Operations", "No test user available")
                    return True
                
                # Test note creation
                test_note = self.note_model(
                    title="Model Test Note",
                    content="Testing model operations",
                    user_id=test_user.id
                )
                
                # Test note saving
                self.db.session.add(test_note)
                self.db.session.commit()
                
                note_id = test_note.id
                success = note_id is not None
                self.log_test_result("Model Create", success)
                
                if success:
                    # Test note retrieval
                    retrieved_note = self.note_model.query.get(note_id)
                    success = retrieved_note is not None and retrieved_note.title == "Model Test Note"
                    self.log_test_result("Model Retrieve", success)
                    
                    # Cleanup
                    self.db.session.delete(retrieved_note)
                    self.db.session.commit()
                    self.log_test_result("Model Delete", True)
                
                return success
                
        except Exception as e:
            self.log_test_result("Model Operations", False, f"Error: {e}")
            return False


if __name__ == '__main__':
    test = NoteModelTest()
    success = test.run_tests()
    sys.exit(0 if success else 1)