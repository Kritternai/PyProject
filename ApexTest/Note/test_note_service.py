#!/usr/bin/env python3
"""
Unit tests for NoteService class.
Single Responsibility: Test NoteService CRUD operations only.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../base'))

from base.base_test import BaseNoteServiceTest


class NoteServiceTest(BaseNoteServiceTest):
    """
    Unit tests for NoteService.
    Follows SRP: Tests only NoteService functionality.
    """
    
    def run_tests(self) -> bool:
        """Run all NoteService tests."""
        print("=" * 60)
        print("NOTE SERVICE UNIT TESTS")
        print("=" * 60)
        
        # Setup
        if not self.setup_service():
            return False
        
        if not self.setup_test_user():
            return False
        
        # Run tests
        self.test_service_initialization()
        self.test_crud_methods_exist()
        self.test_create_note()
        self.test_read_operations()
        self.test_update_operations()
        self.test_delete_operations()
        
        return self.print_summary()
    
    def test_service_initialization(self):
        """Test NoteService initialization."""
        self.log_test_result("Service Initialization", self.note_service is not None)
    
    def test_crud_methods_exist(self):
        """Test if all required CRUD methods exist."""
        required_methods = [
            'create_note',
            'get_note_by_id',
            'get_notes_by_user',
            'get_notes_by_lesson',
            'update_note',
            'delete_note',
            'get_user_notes'
        ]
        
        all_exist = True
        for method in required_methods:
            exists = hasattr(self.note_service, method)
            self.log_test_result(f"Method {method}", exists)
            if not exists:
                all_exist = False
        
        return all_exist
    
    def test_create_note(self):
        """Test note creation functionality."""
        try:
            test_note = self.note_service.create_note(
                user_id=self.test_user.id,
                lesson_id=None,
                title="Unit Test Note",
                content="This is a unit test note."
            )
            
            success = test_note is not None and hasattr(test_note, 'id')
            self.log_test_result("Create Note", success)
            
            if success:
                # Store note ID for cleanup
                self.test_note_id = test_note.id
                return True
            return False
            
        except Exception as e:
            self.log_test_result("Create Note", False, f"Error: {e}")
            return False
    
    def test_read_operations(self):
        """Test note reading operations."""
        if not hasattr(self, 'test_note_id'):
            self.log_skip("Read Operations", "No test note created")
            return True
        
        # Test get_note_by_id
        try:
            note = self.note_service.get_note_by_id(self.test_note_id)
            success = note is not None and note.id == self.test_note_id
            self.log_test_result("Get Note By ID", success)
        except Exception as e:
            self.log_test_result("Get Note By ID", False, f"Error: {e}")
        
        # Test get_user_notes
        try:
            user_notes = self.note_service.get_user_notes(self.test_user.id)
            success = isinstance(user_notes, list)
            self.log_test_result("Get User Notes", success)
        except Exception as e:
            self.log_test_result("Get User Notes", False, f"Error: {e}")
    
    def test_update_operations(self):
        """Test note update operations."""
        if not hasattr(self, 'test_note_id'):
            self.log_skip("Update Operations", "No test note created")
            return True
        
        try:
            updated_note = self.note_service.update_note(
                note_id=self.test_note_id,
                title="Updated Unit Test Note",
                content="This note has been updated."
            )
            
            success = updated_note is not None and updated_note.title == "Updated Unit Test Note"
            self.log_test_result("Update Note", success)
            return success
            
        except Exception as e:
            self.log_test_result("Update Note", False, f"Error: {e}")
            return False
    
    def test_delete_operations(self):
        """Test note deletion operations."""
        if not hasattr(self, 'test_note_id'):
            self.log_skip("Delete Operations", "No test note created")
            return True
        
        try:
            success = self.note_service.delete_note(self.test_note_id)
            self.log_test_result("Delete Note", success)
            return success
            
        except Exception as e:
            self.log_test_result("Delete Note", False, f"Error: {e}")
            return False


if __name__ == '__main__':
    test = NoteServiceTest()
    success = test.run_tests()
    sys.exit(0 if success else 1)
