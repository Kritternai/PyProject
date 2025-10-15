#!/usr/bin/env python3
"""
Unit tests for tag parsing functionality.
Single Responsibility: Test tag parsing logic only.
"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../base'))

from base.base_test import BaseNoteTest


class TagParsingTest(BaseNoteTest):
    """
    Unit tests for tag parsing.
    Follows SRP: Tests only tag parsing functionality.
    """
    
    def run_tests(self) -> bool:
        """Run all tag parsing tests."""
        print("=" * 60)
        print("TAG PARSING UNIT TESTS")
        print("=" * 60)
        
        # Run tests
        self.test_json_array_parsing()
        self.test_comma_separated_parsing()
        self.test_single_tag_parsing()
        self.test_empty_input_parsing()
        self.test_none_input_parsing()
        self.test_list_input_parsing()
        self.test_invalid_input_parsing()
        
        return self.print_summary()
    
    def parse_tags(self, tags_input):
        """Parse tags using the same logic as backend."""
        if not tags_input:
            return []
        
        try:
            if isinstance(tags_input, str):
                # Try to parse as JSON first
                try:
                    parsed_tags = json.loads(tags_input)
                    if isinstance(parsed_tags, list):
                        return parsed_tags
                    else:
                        return []
                except (json.JSONDecodeError, TypeError):
                    # Fallback: split by comma
                    return [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            else:
                return tags_input if isinstance(tags_input, list) else []
        except Exception:
            return []
    
    def test_json_array_parsing(self):
        """Test parsing JSON array strings."""
        test_cases = [
            ('["study", "math", "science"]', ['study', 'math', 'science']),
            ('["study"]', ['study']),
            ('[]', []),
            ('["tag1", "tag2", "tag3"]', ['tag1', 'tag2', 'tag3'])
        ]
        
        all_passed = True
        for input_val, expected in test_cases:
            result = self.parse_tags(input_val)
            passed = result == expected
            self.log_test_result(f"JSON Array: {input_val}", passed)
            if not passed:
                self.log_test_result(f"JSON Array: {input_val}", False, f"Expected: {expected}, Got: {result}")
                all_passed = False
        
        return all_passed
    
    def test_comma_separated_parsing(self):
        """Test parsing comma-separated strings."""
        test_cases = [
            ('study, math, science', ['study', 'math', 'science']),
            ('study', ['study']),
            ('', []),
            ('tag1, tag2, tag3', ['tag1', 'tag2', 'tag3']),
            ('tag1,tag2,tag3', ['tag1', 'tag2', 'tag3']),  # No spaces
            ('tag1, , tag3', ['tag1', 'tag3'])  # Empty tags
        ]
        
        all_passed = True
        for input_val, expected in test_cases:
            result = self.parse_tags(input_val)
            passed = result == expected
            self.log_test_result(f"Comma Separated: {input_val}", passed)
            if not passed:
                self.log_test_result(f"Comma Separated: {input_val}", False, f"Expected: {expected}, Got: {result}")
                all_passed = False
        
        return all_passed
    
    def test_single_tag_parsing(self):
        """Test parsing single tags."""
        test_cases = [
            ('study', ['study']),
            ('"study"', ['study']),
            ('  study  ', ['study'])  # With whitespace
        ]
        
        all_passed = True
        for input_val, expected in test_cases:
            result = self.parse_tags(input_val)
            passed = result == expected
            self.log_test_result(f"Single Tag: {input_val}", passed)
            if not passed:
                self.log_test_result(f"Single Tag: {input_val}", False, f"Expected: {expected}, Got: {result}")
                all_passed = False
        
        return all_passed
    
    def test_empty_input_parsing(self):
        """Test parsing empty inputs."""
        test_cases = [
            ('', []),
            (None, []),
            ('   ', []),
            ('[]', [])
        ]
        
        all_passed = True
        for input_val, expected in test_cases:
            result = self.parse_tags(input_val)
            passed = result == expected
            self.log_test_result(f"Empty Input: {repr(input_val)}", passed)
            if not passed:
                self.log_test_result(f"Empty Input: {repr(input_val)}", False, f"Expected: {expected}, Got: {result}")
                all_passed = False
        
        return all_passed
    
    def test_none_input_parsing(self):
        """Test parsing None input."""
        result = self.parse_tags(None)
        passed = result == []
        self.log_test_result("None Input", passed)
        return passed
    
    def test_list_input_parsing(self):
        """Test parsing list inputs."""
        test_cases = [
            (['study', 'math'], ['study', 'math']),
            (['study'], ['study']),
            ([], []),
            (['tag1', 'tag2', 'tag3'], ['tag1', 'tag2', 'tag3'])
        ]
        
        all_passed = True
        for input_val, expected in test_cases:
            result = self.parse_tags(input_val)
            passed = result == expected
            self.log_test_result(f"List Input: {input_val}", passed)
            if not passed:
                self.log_test_result(f"List Input: {input_val}", False, f"Expected: {expected}, Got: {result}")
                all_passed = False
        
        return all_passed
    
    def test_invalid_input_parsing(self):
        """Test parsing invalid inputs."""
        test_cases = [
            ('{"invalid": "json"}', []),  # Invalid JSON for tags
            ('{"tags": ["study"]}', []),  # Wrong JSON structure
            (123, []),  # Number input
            (True, []),  # Boolean input
        ]
        
        all_passed = True
        for input_val, expected in test_cases:
            result = self.parse_tags(input_val)
            passed = result == expected
            self.log_test_result(f"Invalid Input: {repr(input_val)}", passed)
            if not passed:
                self.log_test_result(f"Invalid Input: {repr(input_val)}", False, f"Expected: {expected}, Got: {result}")
                all_passed = False
        
        return all_passed


if __name__ == '__main__':
    test = TagParsingTest()
    success = test.run_tests()
    sys.exit(0 if success else 1)