#!/usr/bin/env python3
"""
Script to fix import paths in the refactored codebase.
"""

import os
import re

def fix_imports_in_file(file_path):
    """Fix import paths in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix relative imports to absolute imports
        patterns = [
            (r'from \.\.\.domain\.', 'from app.domain.'),
            (r'from \.\.\.shared\.', 'from app.shared.'),
            (r'from \.\.\.application\.', 'from app.application.'),
            (r'from \.\.\.infrastructure\.', 'from app.infrastructure.'),
            (r'from \.\.\.presentation\.', 'from app.presentation.'),
        ]
        
        original_content = content
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed imports in: {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed in: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix imports in all relevant files."""
    base_dir = "app"
    fixed_files = 0
    
    # Files to fix
    files_to_fix = [
        "application/services/lesson_service.py",
        "application/services/note_service.py", 
        "application/services/task_service.py",
        "infrastructure/database/models/lesson_model.py",
        "infrastructure/database/models/note_model.py",
        "infrastructure/database/models/task_model.py",
        "presentation/controllers/lesson_controller.py",
        "presentation/controllers/note_controller.py",
        "presentation/controllers/task_controller.py",
        "presentation/controllers/user_controller.py",
        "presentation/middleware/auth_middleware.py",
    ]
    
    for file_path in files_to_fix:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            if fix_imports_in_file(full_path):
                fixed_files += 1
        else:
            print(f"⚠️  File not found: {full_path}")
    
    print(f"\n🎉 Fixed imports in {fixed_files} files!")

if __name__ == "__main__":
    main()
