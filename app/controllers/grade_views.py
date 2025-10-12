"""
Grade Controller (Views) - Business logic for grade management
Handles grade calculations, goal calculator, and what-if scenarios
Following MVC pattern: Controller handles business logic
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from app import db
from app.utils.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException
)


class GradeController:
    """Controller for grade management - handles business logic"""
    
    # ==========================================
    # CONFIGURATION
    # ==========================================
    
    @staticmethod
    def create_grade_config(lesson_id: str, grading_scale: Dict, **kwargs):
        """
        Create grade configuration for a lesson
        
        Args:
            lesson_id: Lesson ID
            grading_scale: Dictionary of grade scale
            **kwargs: Additional config options
        """
        from app.models.grade import GradeConfig
        
        # Check if config already exists
        existing = GradeConfig.query.filter_by(lesson_id=lesson_id).first()
        if existing:
            raise BusinessLogicException("Grade configuration already exists for this lesson")
        
        # Create config
        config = GradeConfig(
            lesson_id=lesson_id,
            grading_scale=json.dumps(grading_scale),
            grading_type=kwargs.get('grading_type', 'percentage'),
            total_points=kwargs.get('total_points', 100),
            passing_grade=kwargs.get('passing_grade', 'D'),
            passing_percentage=kwargs.get('passing_percentage', 50.0),
            show_total_grade=kwargs.get('show_total_grade', True),
            allow_what_if=kwargs.get('allow_what_if', True),
            show_class_average=kwargs.get('show_class_average', False)
        )
        
        db.session.add(config)
        db.session.commit()
        
        return config
    
    @staticmethod
    def get_grade_config(lesson_id: str):
        """Get grade configuration for a lesson"""
        from app.models.grade import GradeConfig
        
        config = GradeConfig.query.filter_by(lesson_id=lesson_id).first()
        if not config:
            raise NotFoundException("Grade configuration", lesson_id)
        
        # Parse JSON and return dict
        return {
            'id': config.id,
            'lesson_id': config.lesson_id,
            'grading_scale': json.loads(config.grading_scale),
            'grading_type': config.grading_type,
            'total_points': float(config.total_points),
            'passing_grade': config.passing_grade,
            'passing_percentage': float(config.passing_percentage),
            'show_total_grade': config.show_total_grade,
            'allow_what_if': config.allow_what_if,
            'show_class_average': config.show_class_average
        }
    
    @staticmethod
    def update_grade_config(lesson_id: str, grading_scale: Dict, **kwargs):
        """Update existing grade configuration"""
        from app.models.grade import GradeConfig
        
        config = GradeConfig.query.filter_by(lesson_id=lesson_id).first()
        if not config:
            raise NotFoundException("Grade configuration", lesson_id)
        
        # Update fields
        config.grading_scale = json.dumps(grading_scale)
        
        if kwargs.get('grading_type'):
            config.grading_type = kwargs.get('grading_type')
        if kwargs.get('total_points'):
            config.total_points = kwargs.get('total_points')
        if kwargs.get('passing_grade'):
            config.passing_grade = kwargs.get('passing_grade')
        if kwargs.get('passing_percentage'):
            config.passing_percentage = kwargs.get('passing_percentage')
        
        config.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return config
    
    @staticmethod
    def delete_grade_config(lesson_id: str):
        """Delete grade configuration and all related data"""
        from app.models.grade import GradeConfig, GradeCategory, GradeItem, GradeEntry, GradeSummary
        
        # Delete config (will cascade delete categories, items, entries due to FK constraints)
        config = GradeConfig.query.filter_by(lesson_id=lesson_id).first()
        if not config:
            raise NotFoundException("Grade configuration", lesson_id)
        
        # Manually delete related data
        GradeSummary.query.filter_by(lesson_id=lesson_id).delete()
        GradeEntry.query.filter_by(lesson_id=lesson_id).delete()
        GradeItem.query.filter_by(lesson_id=lesson_id).delete()
        GradeCategory.query.filter_by(lesson_id=lesson_id).delete()
        
        db.session.delete(config)
        db.session.commit()
        
        return True
    
    # ==========================================
    # CATEGORIES
    # ==========================================
    
    @staticmethod
    def create_category(lesson_id: str, name: str, weight: float, **kwargs):
        """
        Create a grade category
        
        Args:
            lesson_id: Lesson ID
            name: Category name (e.g., "Assignments")
            weight: Percentage weight (0-100)
            **kwargs: Additional options
        """
        from app.models.grade import GradeCategory
        
        # Validate weight
        if weight < 0 or weight > 100:
            raise ValidationException("Weight must be between 0 and 100")
        
        # Check total weight
        existing_categories = GradeCategory.query.filter_by(lesson_id=lesson_id).all()
        total_weight = sum(float(cat.weight) for cat in existing_categories) + weight
        
        if total_weight > 100:
            raise ValidationException(f"Total weight would exceed 100% (current: {total_weight}%)")
        
        # Create category
        category = GradeCategory(
            lesson_id=lesson_id,
            name=name,
            description=kwargs.get('description', ''),
            weight=weight,
            total_points=kwargs.get('total_points'),
            drop_lowest=kwargs.get('drop_lowest', 0),
            drop_highest=kwargs.get('drop_highest', 0),
            color=kwargs.get('color', '#3B82F6'),
            icon=kwargs.get('icon', 'bi-clipboard'),
            order_index=kwargs.get('order_index', 0)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return category
    
    @staticmethod
    def get_categories(lesson_id: str):
        """Get all categories for a lesson"""
        from app.models.grade import GradeCategory
        
        categories = GradeCategory.query.filter_by(
            lesson_id=lesson_id
        ).order_by(GradeCategory.order_index).all()
        
        return categories
    
    @staticmethod
    def delete_category(category_id: str):
        """Delete a grade category"""
        from app.models.grade import GradeCategory
        
        category = GradeCategory.query.get(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        
        db.session.delete(category)
        db.session.commit()
        
        return True
    
    # ==========================================
    # GRADE ITEMS
    # ==========================================
    
    @staticmethod
    def create_grade_item(lesson_id: str, category_id: str, name: str, points_possible: float, **kwargs):
        """Create a grade item (assignment, quiz, etc.)"""
        from app.models.grade import GradeItem, GradeCategory
        
        # Validate category exists
        category = GradeCategory.query.get(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        
        # Parse due_date if provided
        due_date = None
        if kwargs.get('due_date'):
            try:
                if isinstance(kwargs['due_date'], str):
                    due_date = datetime.fromisoformat(kwargs['due_date'])
                else:
                    due_date = kwargs['due_date']
            except ValueError:
                raise ValidationException("Invalid due_date format. Use YYYY-MM-DD")
        
        # Create grade item
        item = GradeItem(
            lesson_id=lesson_id,
            category_id=category_id,
            name=name,
            description=kwargs.get('description', ''),
            points_possible=points_possible,
            due_date=due_date,
            published_date=kwargs.get('published_date'),
            is_published=kwargs.get('is_published', False),
            is_extra_credit=kwargs.get('is_extra_credit', False),
            is_muted=kwargs.get('is_muted', False),
            classwork_task_id=kwargs.get('classwork_task_id')  # Link to task
        )
        
        db.session.add(item)
        db.session.commit()
        
        return item
    
    @staticmethod
    def update_grade_item(item_id: str, **kwargs):
        """Update an existing grade item"""
        from app.models.grade import GradeItem, GradeCategory
        
        # Get grade item
        item = GradeItem.query.get(item_id)
        if not item:
            raise NotFoundException("Grade item", item_id)
        
        # Update fields if provided
        if 'name' in kwargs:
            item.name = kwargs['name']
        
        if 'category_id' in kwargs:
            # Validate new category exists
            category = GradeCategory.query.get(kwargs['category_id'])
            if not category:
                raise NotFoundException("Category", kwargs['category_id'])
            item.category_id = kwargs['category_id']
        
        if 'points_possible' in kwargs:
            item.points_possible = kwargs['points_possible']
        
        if 'description' in kwargs:
            item.description = kwargs['description']
        
        if 'due_date' in kwargs:
            due_date = kwargs['due_date']
            if due_date:
                try:
                    if isinstance(due_date, str):
                        item.due_date = datetime.fromisoformat(due_date)
                    else:
                        item.due_date = due_date
                except ValueError:
                    raise ValidationException("Invalid due_date format. Use YYYY-MM-DD")
            else:
                item.due_date = None
        
        if 'is_published' in kwargs:
            item.is_published = kwargs['is_published']
        
        # Update timestamp
        item.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # If score is provided, also update/create grade entry
        if 'score' in kwargs:
            user_id = kwargs.get('user_id')
            if user_id:
                GradeController.submit_grade(
                    grade_item_id=item_id,
                    user_id=user_id,
                    score=kwargs['score'],
                    comments=kwargs.get('comments')
                )
        
        return item
    
    @staticmethod
    def get_available_tasks(lesson_id: str):
        """Get classwork tasks that haven't been linked to grade items yet"""
        from app import db
        from sqlalchemy import text
        
        # Get all tasks for this lesson
        tasks = db.session.execute(
            text("""
                SELECT id, title, description, status, priority, due_date
                FROM classwork_task
                WHERE lesson_id = :lesson_id
                AND id NOT IN (
                    SELECT classwork_task_id 
                    FROM grade_item 
                    WHERE classwork_task_id IS NOT NULL 
                    AND lesson_id = :lesson_id
                )
                ORDER BY created_at DESC
            """),
            {'lesson_id': lesson_id}
        ).fetchall()
        
        result = []
        for task in tasks:
            result.append({
                'id': task[0],
                'title': task[1],
                'description': task[2],
                'status': task[3],
                'priority': task[4],
                'due_date': task[5]
            })
        
        return result
    
    @staticmethod
    def get_grade_items(lesson_id: str, include_unpublished=False):
        """Get all grade items for a lesson"""
        from app.models.grade import GradeItem
        
        query = GradeItem.query.filter_by(lesson_id=lesson_id)
        
        if not include_unpublished:
            query = query.filter_by(is_published=True)
        
        items = query.order_by(GradeItem.due_date).all()
        
        return items
    
    # ==========================================
    # GRADE ENTRIES
    # ==========================================
    
    @staticmethod
    def submit_grade(grade_item_id: str, user_id: str, score: float, **kwargs):
        """Submit/update a grade entry"""
        from app.models.grade import GradeEntry, GradeItem
        
        # Get grade item
        item = GradeItem.query.get(grade_item_id)
        if not item:
            raise NotFoundException("Grade item", grade_item_id)
        
        # Check if entry exists
        entry = GradeEntry.query.filter_by(
            grade_item_id=grade_item_id,
            user_id=user_id
        ).first()
        
        if entry:
            # Update existing
            entry.score = score
            entry.points_possible = item.points_possible
            entry.status = 'graded'
            entry.graded_at = datetime.utcnow()
            entry.comments = kwargs.get('comments')
            entry.graded_by = kwargs.get('graded_by')
            entry.is_late = kwargs.get('is_late', False)
            entry.late_penalty = kwargs.get('late_penalty', 0)
        else:
            # Create new
            entry = GradeEntry(
                user_id=user_id,
                lesson_id=item.lesson_id,
                grade_item_id=grade_item_id,
                score=score,
                points_possible=item.points_possible,
                status='graded',
                graded_at=datetime.utcnow(),
                comments=kwargs.get('comments'),
                graded_by=kwargs.get('graded_by'),
                is_late=kwargs.get('is_late', False),
                late_penalty=kwargs.get('late_penalty', 0)
            )
            db.session.add(entry)
        
        db.session.commit()
        
        # Recalculate summary
        GradeController.calculate_grade_summary(item.lesson_id, user_id)
        
        return entry
    
    @staticmethod
    def get_student_grades(lesson_id: str, user_id: str):
        """
        Get all grade items for a student in a lesson
        Returns ALL grade items (both with and without grades)
        """
        from app.models.grade import GradeEntry, GradeItem, GradeCategory
        from sqlalchemy import text
        
        # Get ALL grade items with LEFT JOIN to grade entries
        # This ensures we show all assignments, even those without grades yet
        items = db.session.execute(
            text("""
                SELECT 
                    gi.id as item_id,
                    gi.name as item_name,
                    gi.points_possible as item_points,
                    gi.due_date,
                    gi.is_published,
                    gi.classwork_task_id,
                    gc.id as category_id,
                    gc.name as category_name,
                    gc.color as category_color,
                    ge.id as entry_id,
                    ge.score,
                    ge.status,
                    ge.is_late,
                    ge.comments,
                    ge.graded_at,
                    ct.title as task_title,
                    ct.status as task_status
                FROM grade_item gi
                JOIN grade_category gc ON gi.category_id = gc.id
                LEFT JOIN grade_entry ge ON ge.grade_item_id = gi.id AND ge.user_id = :user_id
                LEFT JOIN classwork_task ct ON gi.classwork_task_id = ct.id
                WHERE gi.lesson_id = :lesson_id
                AND gi.is_published = 1
                ORDER BY gi.due_date, gi.name
            """),
            {'lesson_id': lesson_id, 'user_id': user_id}
        ).fetchall()
        
        result = []
        for row in items:
            # Calculate percentage
            percentage = None
            score = row[10]
            item_points = row[2]
            
            if score is not None and item_points is not None and item_points > 0:
                percentage = round((float(score) / float(item_points)) * 100, 2)
            
            # Determine status
            status = row[11] if row[11] else 'pending'  # If no entry, status is pending
            
            result.append({
                'item_id': row[0],
                'item_name': row[1],
                'points_possible': float(item_points) if item_points else 0,
                'due_date': row[3],
                'category_id': row[6],
                'category_name': row[7],
                'category_color': row[8],
                'entry_id': row[9],
                'score': float(score) if score else None,
                'percentage': percentage,
                'status': status,
                'is_late': row[12] if row[12] else False,
                'comments': row[13],
                'graded_at': row[14],
                'linked_task_title': row[15],  # Task title
                'linked_task_status': row[16]  # Task status
            })
        
        return result
    
    # ==========================================
    # GRADE CALCULATIONS
    # ==========================================
    
    @staticmethod
    def calculate_grade_summary(lesson_id: str, user_id: str):
        """
        Calculate complete grade summary for a student
        Returns summary with current grade, goals, and what-if data
        """
        from app.models.grade import GradeConfig, GradeCategory, GradeItem, GradeEntry, GradeSummary
        
        # Get config
        config = GradeConfig.query.filter_by(lesson_id=lesson_id).first()
        if not config:
            return {'error': 'Grade configuration not set'}
        
        grading_scale = json.loads(config.grading_scale)
        
        # Get categories
        categories = GradeCategory.query.filter_by(lesson_id=lesson_id).all()
        
        total_weighted_score = 0
        category_breakdown = {}
        
        for category in categories:
            # Get all items in this category
            items = GradeItem.query.filter_by(
                category_id=category.id,
                is_published=True
            ).all()
            
            # Get grades for these items
            total_earned = 0
            total_possible = 0
            graded_count = 0
            
            for item in items:
                entry = GradeEntry.query.filter_by(
                    grade_item_id=item.id,
                    user_id=user_id,
                    status='graded'
                ).first()
                
                if entry and entry.score is not None:
                    total_earned += float(entry.score)
                    total_possible += float(entry.points_possible)
                    graded_count += 1
            
            # Calculate category percentage
            if total_possible > 0:
                category_percentage = (total_earned / total_possible) * 100
            else:
                category_percentage = 0
            
            # Calculate weighted score
            weighted_score = category_percentage * (float(category.weight) / 100)
            total_weighted_score += weighted_score
            
            # Always include category in breakdown (even if no items)
            category_breakdown[category.id] = {
                'name': category.name,
                'weight': float(category.weight),
                'earned': total_earned,
                'possible': total_possible,
                'percentage': round(category_percentage, 2),
                'weighted_score': round(weighted_score, 2),
                'color': category.color,
                'total_items': len(items),
                'graded_items': graded_count,
                'pending_items': len(items) - graded_count
            }
        
        # Get letter grade
        letter_grade = GradeController._get_letter_grade(total_weighted_score, grading_scale)
        gpa = grading_scale[letter_grade]['gpa']
        
        # Calculate goals
        goals = GradeController._calculate_goals(
            lesson_id=lesson_id,
            user_id=user_id,
            current_percentage=total_weighted_score,
            grading_scale=grading_scale
        )
        
        # Save/update summary
        summary = GradeSummary.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()
        
        if summary:
            summary.current_score = total_weighted_score
            summary.percentage = total_weighted_score
            summary.letter_grade = letter_grade
            summary.gpa = gpa
            summary.is_passing = total_weighted_score >= float(config.passing_percentage)
            summary.points_to_next_grade = json.dumps(goals.get('points_to_grades', {}))
            summary.last_calculated = datetime.utcnow()
        else:
            summary = GradeSummary(
                user_id=user_id,
                lesson_id=lesson_id,
                current_score=total_weighted_score,
                percentage=total_weighted_score,
                letter_grade=letter_grade,
                gpa=gpa,
                is_passing=total_weighted_score >= float(config.passing_percentage),
                points_to_next_grade=json.dumps(goals.get('points_to_grades', {})),
                last_calculated=datetime.utcnow()
            )
            db.session.add(summary)
        
        db.session.commit()
        
        return {
            'percentage': round(total_weighted_score, 2),
            'letter_grade': letter_grade,
            'gpa': gpa,
            'is_passing': total_weighted_score >= float(config.passing_percentage),
            'category_breakdown': category_breakdown,
            'goals': goals
        }
    
    @staticmethod
    def _get_letter_grade(percentage: float, grading_scale: Dict) -> str:
        """Convert percentage to letter grade"""
        for grade, scale in grading_scale.items():
            if scale['min'] <= percentage <= scale['max']:
                return grade
        return 'F'
    
    @staticmethod
    def _calculate_goals(lesson_id: str, user_id: str, current_percentage: float, grading_scale: Dict) -> Dict:
        """Calculate points needed for each grade"""
        from app.models.grade import GradeItem, GradeEntry
        
        # Get remaining items (not yet graded)
        all_items = GradeItem.query.filter_by(
            lesson_id=lesson_id,
            is_published=True
        ).all()
        
        graded_items = GradeEntry.query.filter_by(
            lesson_id=lesson_id,
            user_id=user_id,
            status='graded'
        ).all()
        
        graded_item_ids = {entry.grade_item_id for entry in graded_items}
        remaining_items = [item for item in all_items if item.id not in graded_item_ids]
        
        total_remaining_points = sum(float(item.points_possible) for item in remaining_items)
        
        goals = {}
        points_to_grades = {}
        
        for grade_letter, scale in sorted(grading_scale.items(), key=lambda x: x[1]['min'], reverse=True):
            target_percentage = scale['min']
            
            if current_percentage >= target_percentage:
                goals[grade_letter] = {
                    'achievable': True,
                    'already_achieved': True,
                    'message': f"You already have a {grade_letter}!"
                }
                points_to_grades[grade_letter] = 0
            else:
                points_needed = target_percentage - current_percentage
                
                if total_remaining_points == 0:
                    goals[grade_letter] = {
                        'achievable': False,
                        'message': f"No remaining work to improve grade to {grade_letter}"
                    }
                    points_to_grades[grade_letter] = None
                elif points_needed > total_remaining_points:
                    goals[grade_letter] = {
                        'achievable': False,
                        'message': f"Not enough remaining points to achieve {grade_letter}"
                    }
                    points_to_grades[grade_letter] = None
                else:
                    percentage_needed = (points_needed / total_remaining_points) * 100 if total_remaining_points > 0 else 0
                    goals[grade_letter] = {
                        'achievable': True,
                        'already_achieved': False,
                        'points_needed': round(points_needed, 2),
                        'percentage_needed': round(percentage_needed, 2),
                        'message': f"Need {round(points_needed, 2)} more points to get {grade_letter} ({round(percentage_needed, 2)}% on remaining work)"
                    }
                    points_to_grades[grade_letter] = round(points_needed, 2)
        
        return {
            'goals': goals,
            'points_to_grades': points_to_grades,
            'remaining_points': total_remaining_points,
            'remaining_items': len(remaining_items)
        }
    
    # ==========================================
    # GOAL CALCULATOR
    # ==========================================
    
    @staticmethod
    def calculate_goal(lesson_id: str, user_id: str, target_grade: str):
        """Calculate what score is needed to achieve target grade"""
        summary = GradeController.calculate_grade_summary(lesson_id, user_id)
        
        if 'error' in summary:
            return summary
        
        goals = summary['goals']['goals']
        
        if target_grade not in goals:
            raise ValidationException(f"Invalid target grade: {target_grade}")
        
        return {
            'target_grade': target_grade,
            'current_grade': summary['letter_grade'],
            'current_percentage': summary['percentage'],
            'goal_info': goals[target_grade]
        }
    
    # ==========================================
    # WHAT-IF CALCULATOR
    # ==========================================
    
    @staticmethod
    def calculate_what_if(lesson_id: str, user_id: str, hypothetical_scores: Dict):
        """
        Calculate what-if scenario
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID
            hypothetical_scores: Dict of {grade_item_id: hypothetical_score}
        """
        from app.models.grade import GradeConfig, GradeCategory, GradeItem, GradeEntry
        
        # Get current summary first
        current_summary = GradeController.calculate_grade_summary(lesson_id, user_id)
        
        if 'error' in current_summary:
            return current_summary
        
        # Get config
        config = GradeConfig.query.filter_by(lesson_id=lesson_id).first()
        grading_scale = json.loads(config.grading_scale)
        
        # Get categories
        categories = GradeCategory.query.filter_by(lesson_id=lesson_id).all()
        
        total_weighted_score = 0
        
        for category in categories:
            items = GradeItem.query.filter_by(
                category_id=category.id,
                is_published=True
            ).all()
            
            if not items:
                continue
            
            total_earned = 0
            total_possible = 0
            
            for item in items:
                # Use hypothetical score if provided
                if item.id in hypothetical_scores:
                    score = hypothetical_scores[item.id]
                    total_earned += score
                    total_possible += float(item.points_possible)
                else:
                    # Use actual grade
                    entry = GradeEntry.query.filter_by(
                        grade_item_id=item.id,
                        user_id=user_id,
                        status='graded'
                    ).first()
                    
                    if entry and entry.score is not None:
                        total_earned += float(entry.score)
                        total_possible += float(entry.points_possible)
            
            # Calculate category percentage
            if total_possible > 0:
                category_percentage = (total_earned / total_possible) * 100
                weighted_score = category_percentage * (float(category.weight) / 100)
                total_weighted_score += weighted_score
        
        # Get hypothetical letter grade
        hypothetical_grade = GradeController._get_letter_grade(total_weighted_score, grading_scale)
        hypothetical_gpa = grading_scale[hypothetical_grade]['gpa']
        
        return {
            'current_percentage': current_summary['percentage'],
            'current_grade': current_summary['letter_grade'],
            'current_gpa': current_summary['gpa'],
            'hypothetical_percentage': round(total_weighted_score, 2),
            'hypothetical_grade': hypothetical_grade,
            'hypothetical_gpa': hypothetical_gpa,
            'difference': round(total_weighted_score - current_summary['percentage'], 2)
        }

