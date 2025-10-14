"""
Add Grade Items to Current Lesson
Quick script to add sample grade items and scores to any lesson
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.controllers.grade_views import GradeController
from app.models.grade import GradeCategory
from datetime import datetime, timedelta


def add_grade_items_to_lesson(lesson_id, user_id):
    """Add grade items to a specific lesson"""
    
    print(f"📝 Adding grade items to lesson: {lesson_id}")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Get categories for this lesson
            categories = GradeCategory.query.filter_by(lesson_id=lesson_id).all()
            
            if not categories:
                print("❌ No categories found. Please setup grading first.")
                return
            
            print(f"✅ Found {len(categories)} categories")
            
            # Add items for each category
            items_created = []
            
            for category in categories:
                print(f"\n📊 Category: {category.name} ({category.weight}%)")
                
                # Determine number of items based on category name
                if 'assignment' in category.name.lower() or 'work' in category.name.lower():
                    num_items = 5
                    base_points = 20
                elif 'quiz' in category.name.lower():
                    num_items = 3
                    base_points = 10
                elif 'mid' in category.name.lower() or 'final' in category.name.lower():
                    num_items = 1
                    base_points = 100
                else:
                    num_items = 2
                    base_points = 50
                
                # Create items
                for i in range(1, num_items + 1):
                    try:
                        item = GradeController.create_grade_item(
                            lesson_id=lesson_id,
                            category_id=category.id,
                            name=f"{category.name} {i}",
                            points_possible=base_points,
                            is_published=True,
                            due_date=datetime.now() - timedelta(days=(num_items - i) * 5)
                        )
                        items_created.append(item)
                        print(f"  ✅ Created: {item.name} ({base_points} pts)")
                    except Exception as e:
                        print(f"  ⚠️ Error: {e}")
            
            print(f"\n✅ Total items created: {len(items_created)}")
            
            # Submit some sample grades (70-95% range)
            import random
            scores_submitted = 0
            
            print(f"\n📊 Submitting sample grades...")
            
            for i, item in enumerate(items_created):
                # Skip last 2 items (keep as pending)
                if i >= len(items_created) - 2:
                    continue
                
                try:
                    # Random score between 70-95%
                    percentage = random.randint(70, 95)
                    score = (percentage / 100) * float(item.points_possible)
                    
                    GradeController.submit_grade(
                        grade_item_id=item.id,
                        user_id=user_id,
                        score=score,
                        comments="Good work!"
                    )
                    scores_submitted += 1
                    print(f"  ✅ Graded: {item.name} - {score:.1f}/{item.points_possible} ({percentage}%)")
                    
                except Exception as e:
                    print(f"  ❌ Error grading {item.name}: {e}")
            
            print(f"\n✅ Submitted {scores_submitted} grades")
            
            # Calculate summary
            print(f"\n🎯 Calculating grade summary...")
            try:
                summary = GradeController.calculate_grade_summary(lesson_id, user_id)
                
                if 'error' not in summary:
                    print(f"\n" + "="*60)
                    print(f"📊 GRADE SUMMARY")
                    print(f"="*60)
                    print(f"Current Grade: {summary['letter_grade']} ({summary['percentage']:.2f}%)")
                    print(f"GPA: {summary['gpa']}")
                    print(f"Status: {'✅ Passing' if summary['is_passing'] else '❌ Failing'}")
                    print(f"="*60)
                else:
                    print(f"❌ Error: {summary['error']}")
                    
            except Exception as e:
                print(f"❌ Error calculating summary: {e}")
                import traceback
                traceback.print_exc()
            
            print(f"\n🎉 Done! Refresh the Grades tab to see the data.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # Get lesson and user from command line or use defaults
    if len(sys.argv) >= 3:
        lesson_id = sys.argv[1]
        user_id = sys.argv[2]
    else:
        # Default: current lesson "กฟห" and user "1"
        lesson_id = "37e5c2e4-d83b-4b4d-af7d-814bc6b60f0a"
        user_id = "f7462f3a-658d-484b-9f84-4f5b3f4d9efb"
        
        print(f"Using defaults:")
        print(f"  Lesson: กฟห")
        print(f"  User: 1 (email: 1)")
        print(f"\nTo use different lesson/user:")
        print(f"  python {sys.argv[0]} <lesson_id> <user_id>")
        print(f"\n" + "="*60 + "\n")
    
    add_grade_items_to_lesson(lesson_id, user_id)

