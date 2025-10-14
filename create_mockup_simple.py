#!/usr/bin/env python3
"""
Simple script to create mockup data using direct SQL
"""

import sqlite3
import uuid
from datetime import datetime, timedelta

def create_mockup_data():
    """Create mockup data using direct SQL"""
    lesson_id = "442db405-e3da-4b2e-857d-602d696bb784"
    user_id = "1"
    
    print(f"🎯 Creating mockup data for lesson {lesson_id}")
    
    # Connect to database
    conn = sqlite3.connect('instance/site.db')
    cursor = conn.cursor()
    
    try:
        # 1. Create Stream mockup data (Notes)
        print("📢 Creating Stream mockup...")
        
        stream_notes = [
            (str(uuid.uuid4()), user_id, lesson_id, "Welcome to Computer Science 101!", 
             """<div class="announcement-card">
                <h4>🎉 Welcome to Computer Science 101!</h4>
                <p>This class has been imported from Microsoft Teams with 45 members and 4 channels.</p>
                <div class="announcement-meta">
                    <span><i class="bi bi-people"></i> 45 members</span>
                    <span><i class="bi bi-chat-dots"></i> 4 channels</span>
                    <span><i class="bi bi-calendar"></i> Created 2024-01-15</span>
                </div>
            </div>""", 'announcement', datetime.now().isoformat()),
            
            (str(uuid.uuid4()), user_id, lesson_id, "Channel Update: General",
             """<div class="channel-update">
                <h5>📢 General Channel</h5>
                <p>This channel has 156 messages and is actively used for class discussions.</p>
                <div class="channel-stats">
                    <span class="badge bg-primary">156 messages</span>
                    <span class="badge bg-info">Standard</span>
                </div>
            </div>""", 'channel_update', datetime.now().isoformat()),
            
            (str(uuid.uuid4()), user_id, lesson_id, "Channel Update: Assignments",
             """<div class="channel-update">
                <h5>📢 Assignments Channel</h5>
                <p>This channel has 89 messages and contains assignment discussions.</p>
                <div class="channel-stats">
                    <span class="badge bg-primary">89 messages</span>
                    <span class="badge bg-info">Standard</span>
                </div>
            </div>""", 'channel_update', datetime.now().isoformat())
        ]
        
        for note in stream_notes:
            cursor.execute("""
                INSERT INTO note (id, user_id, lesson_id, title, content, note_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, note + (datetime.now().isoformat(),))
        
        print(f"✅ Created {len(stream_notes)} stream notes")
        
        # 2. Create Classwork mockup data (Tasks)
        print("📚 Creating Classwork mockup...")
        
        tasks = [
            (str(uuid.uuid4()), user_id, "Programming Assignment 1: Basic Algorithms",
             "Implement basic sorting algorithms and analyze their time complexity.",
             'pending', 'high', (datetime.now() + timedelta(days=7)).isoformat()),
            
            (str(uuid.uuid4()), user_id, "Data Structures Project",
             "Create and implement a custom data structure with documentation.",
             'pending', 'high', (datetime.now() + timedelta(days=14)).isoformat()),
            
            (str(uuid.uuid4()), user_id, "Algorithm Analysis Quiz",
             "Complete the online quiz covering algorithm analysis concepts.",
             'pending', 'medium', (datetime.now() + timedelta(days=3)).isoformat())
        ]
        
        for task in tasks:
            cursor.execute("""
                INSERT INTO task (id, user_id, title, description, status, priority, due_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, task + (datetime.now().isoformat(), datetime.now().isoformat()))
        
        print(f"✅ Created {len(tasks)} classwork tasks")
        
        # 3. Create Grades mockup data
        print("📊 Creating Grades mockup...")
        
        # Create grade categories
        categories = [
            (str(uuid.uuid4()), lesson_id, 'Assignments', 'Programming assignments and homework',
             40.0, 300.0, '#1976D2', 'bi-clipboard', 0),
            (str(uuid.uuid4()), lesson_id, 'Projects', 'Major programming projects',
             30.0, 200.0, '#48BB78', 'bi-code-slash', 1),
            (str(uuid.uuid4()), lesson_id, 'Exams', 'Midterm and final exams',
             20.0, 150.0, '#F6AD55', 'bi-pencil-square', 2),
            (str(uuid.uuid4()), lesson_id, 'Participation', 'Class participation and attendance',
             10.0, 50.0, '#9F7AEA', 'bi-people', 3)
        ]
        
        for category in categories:
            cursor.execute("""
                INSERT INTO grade_category (id, lesson_id, name, description, weight, total_points, color, icon, order_index, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, category + (datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Get category IDs for grade items
        cursor.execute("SELECT id FROM grade_category WHERE lesson_id = ? ORDER BY order_index", (lesson_id,))
        category_ids = [row[0] for row in cursor.fetchall()]
        
        # Create grade items
        grade_items = [
            (str(uuid.uuid4()), lesson_id, category_ids[0], 'Programming Assignment 1: Basic Algorithms',
             'Implement basic sorting algorithms and analyze their time complexity.',
             100.0, (datetime.now() + timedelta(days=7)).isoformat(), datetime.now().isoformat(), 1),
            
            (str(uuid.uuid4()), lesson_id, category_ids[0], 'Programming Assignment 2: Data Structures',
             'Implement linked lists and binary trees.',
             100.0, (datetime.now() + timedelta(days=14)).isoformat(), datetime.now().isoformat(), 1),
            
            (str(uuid.uuid4()), lesson_id, category_ids[1], 'Data Structures Project',
             'Create and implement a custom data structure with documentation.',
             150.0, (datetime.now() + timedelta(days=21)).isoformat(), datetime.now().isoformat(), 1),
            
            (str(uuid.uuid4()), lesson_id, category_ids[2], 'Algorithm Analysis Quiz',
             'Complete the online quiz covering algorithm analysis concepts.',
             50.0, (datetime.now() + timedelta(days=3)).isoformat(), datetime.now().isoformat(), 1)
        ]
        
        for item in grade_items:
            cursor.execute("""
                INSERT INTO grade_item (id, lesson_id, category_id, name, description, points_possible, due_date, published_date, is_published, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, item + (datetime.now().isoformat(), datetime.now().isoformat()))
        
        print(f"✅ Created {len(categories)} grade categories and {len(grade_items)} grade items")
        
        # 4. Create People mockup data (Notes for member management)
        print("👥 Creating People mockup...")
        
        people_note = (str(uuid.uuid4()), user_id, lesson_id, "Class Members (45 total)",
                      """<div class="members-overview">
                        <h5>👥 Class Members</h5>
                        <p>This class has 45 members imported from Microsoft Teams.</p>
                        <div class="member-stats">
                            <div class="stat-card">
                                <span class="stat-number">45</span>
                                <span class="stat-label">Total Members</span>
                            </div>
                            <div class="stat-card">
                                <span class="stat-number">1</span>
                                <span class="stat-label">Instructors</span>
                            </div>
                            <div class="stat-card">
                                <span class="stat-number">44</span>
                                <span class="stat-label">Students</span>
                            </div>
                        </div>
                        <div class="member-actions">
                            <button class="btn btn-primary btn-sm">View All Members</button>
                            <button class="btn btn-outline-primary btn-sm">Add Members</button>
                        </div>
                    </div>""", 'member_management', datetime.now().isoformat())
        
        cursor.execute("""
            INSERT INTO note (id, user_id, lesson_id, title, content, note_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, people_note + (datetime.now().isoformat(),))
        
        print("✅ Created 1 people management note")
        
        # Commit all changes
        conn.commit()
        
        print("🎉 Mockup data created successfully!")
        print(f"📊 Summary:")
        print(f"   📢 Stream notes: {len(stream_notes)}")
        print(f"   📚 Classwork tasks: {len(tasks)}")
        print(f"   👥 People notes: 1")
        print(f"   📊 Grade categories: {len(categories)}")
        print(f"   📊 Grade items: {len(grade_items)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating mockup data: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    create_mockup_data()
