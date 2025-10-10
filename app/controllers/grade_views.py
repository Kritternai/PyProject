"""
Grade Controller (Views) - Business logic for grade management
Handles grade calculations, goal calculator, and what-if scenarios
Following MVC pattern: Controller handles business logic
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
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
            grading_scale: Dictionary of grade scale (e.g., {"A": {"min": 80, "max": 100, "gpa": 4.0}})
            **kwargs: Additional config options
        """
        from database.models.grade import GradeConfig
        from app import db
        import uuid
        
        # Check if config already exists
        existing = db.session.query(GradeConfig).filter_by(lesson_id=lesson_id).first()
        if existing:
            raise BusinessLogicException("Grade configuration already exists for this lesson")
        
        # Create config
        config = GradeConfig(
            id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            grading_scale=json.dumps(grading_scale),
            grading_type=kwargs.get('grading_type', 'percentage'),
            total_points=kwargs.get('total_points', 100),
            passing_grade=kwargs.get('passing_grade', 'D'),
            passing_percentage=kwargs.get('passing_percentage', 50.0),
            show_total_grade=kwargs.get('show_total_grade', True),
            allow_what_if=kwargs.get('allow_what_if', True),
            show_class_average=kwargs.get('show_class_average', False),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(config)
        db.session.commit()
        
        return config
    
    @staticmethod
    def get_grade_config(lesson_id: str):
        """Get grade configuration for a lesson"""
        from database.models.grade import GradeConfig
        from app import db
        
        config = db.session.query(GradeConfig).filter_by(lesson_id=lesson_id).first()
        if not config:
            raise NotFoundException("Grade configuration not found")
        
        # Parse JSON grading scale
        config_dict = {
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
        
        return config_dict
    
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
        from database.models.grade import GradeCategory
        from app import db
        import uuid
        
        # Validate weight
        if weight < 0 or weight > 100:
            raise ValidationException("Weight must be between 0 and 100")
        
        # Check total weight
        existing_categories = db.session.query(GradeCategory).filter_by(lesson_id=lesson_id).all()
        total_weight = sum(float(cat.weight) for cat in existing_categories) + weight
        
        if total_weight > 100:
            raise ValidationException(f"Total weight would exceed 100% (current: {total_weight}%)")
        
        # Create category
        category = GradeCategory(
            id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            name=name,
            description=kwargs.get('description', ''),
            weight=weight,
            total_points=kwargs.get('total_points'),
            drop_lowest=kwargs.get('drop_lowest', 0),
            drop_highest=kwargs.get('drop_highest', 0),
            color=kwargs.get('color', '#3B82F6'),
            icon=kwargs.get('icon', 'bi-clipboard'),
            order_index=kwargs.get('order_index', 0),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(category)
        db.session.commit()
        
        return category
    
    @staticmethod
    def get_categories(lesson_id: str):
        """Get all categories for a lesson"""
        from database.models.grade import GradeCategory
        from app import db
        
        categories = db.session.query(GradeCategory).filter_by(
            lesson_id=lesson_id
        ).order_by(GradeCategory.order_index).all()
        
        return categories
    
    # ==========================================
    # GRADE ITEMS
    # ==========================================
    
    @staticmethod
    def create_grade_item(lesson_id: str, category_id: str, name: str, points_possible: float, **kwargs):
        """Create a grade item (assignment, quiz, etc.)"""
        from database.models.grade import GradeItem, GradeCategory
        from app import db
        import uuid
        
        # Validate category exists
        category = db.session.query(GradeCategory).get(category_id)
        if not category:
            raise NotFoundException("Category not found")
        
        # Create grade item
        item = GradeItem(
            id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            category_id=category_id,
            name=name,
            description=kwargs.get('description', ''),
            points_possible=points_possible,
            due_date=kwargs.get('due_date'),
            published_date=kwargs.get('published_date'),
            is_published=kwargs.get('is_published', False),
            is_extra_credit=kwargs.get('is_extra_credit', False),
            is_muted=kwargs.get('is_muted', False),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(item)
        db.session.commit()
        
        return item
    
    @staticmethod
    def get_grade_items(lesson_id: str, include_unpublished=False):
        """Get all grade items for a lesson"""
        from database.models.grade import GradeItem
        from app import db
        
        query = db.session.query(GradeItem).filter_by(lesson_id=lesson_id)
        
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
        from database.models.grade import GradeEntry, GradeItem
        from app import db
        import uuid
        
        # Get grade item
        item = db.session.query(GradeItem).get(grade_item_id)
        if not item:
            raise NotFoundException("Grade item not found")
        
        # Check if entry exists
        entry = db.session.query(GradeEntry).filter_by(
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
            entry.updated_at = datetime.utcnow()
        else:
            # Create new
            entry = GradeEntry(
                id=str(uuid.uuid4()),
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
                late_penalty=kwargs.get('late_penalty', 0),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(entry)
        
        db.session.commit()
        
        # Recalculate summary
        GradeController.calculate_grade_summary(item.lesson_id, user_id)
        
        return entry
    
    @staticmethod
    def get_student_grades(lesson_id: str, user_id: str):
        """Get all grade entries for a student in a lesson"""
        from database.models.grade import GradeEntry, GradeItem, GradeCategory
        from app import db
        
        entries = db.session.query(
            GradeEntry, GradeItem, GradeCategory
        ).join(
            GradeItem, GradeEntry.grade_item_id == GradeItem.id
        ).join(
            GradeCategory, GradeItem.category_id == GradeCategory.id
        ).filter(
            GradeEntry.lesson_id == lesson_id,
            GradeEntry.user_id == user_id
        ).order_by(GradeItem.due_date).all()
        
        result = []
        for entry, item, category in entries:
            result.append({
                'entry_id': entry.id,
                'item_id': item.id,
                'item_name': item.name,
                'category_name': category.name,
                'category_color': category.color,
                'score': float(entry.score) if entry.score else None,
                'points_possible': float(entry.points_possible) if entry.points_possible else float(item.points_possible),
                'percentage': entry.percentage,
                'status': entry.status,
                'is_late': entry.is_late,
                'comments': entry.comments,
                'graded_at': entry.graded_at.isoformat() if entry.graded_at else None,
                'due_date': item.due_date.isoformat() if item.due_date else None
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
        from database.models.grade import GradeConfig, GradeCategory, GradeItem, GradeEntry, GradeSummary
        from app import db
        import uuid
        
        # Get config
        config = db.session.query(GradeConfig).filter_by(lesson_id=lesson_id).first()
        if not config:
            return {'error': 'Grade configuration not set'}
        
        grading_scale = json.loads(config.grading_scale)
        
        # Get categories
        categories = db.session.query(GradeCategory).filter_by(lesson_id=lesson_id).all()
        
        total_weighted_score = 0
        category_breakdown = {}
        
        for category in categories:
            # Get all items in this category
            items = db.session.query(GradeItem).filter_by(
                category_id=category.id,
                is_published=True
            ).all()
            
            if not items:
                continue
            
            # Get grades for these items
            total_earned = 0
            total_possible = 0
            
            for item in items:
                entry = db.session.query(GradeEntry).filter_by(
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
            else:
                category_percentage = 0
            
            # Calculate weighted score
            weighted_score = category_percentage * (float(category.weight) / 100)
            total_weighted_score += weighted_score
            
            category_breakdown[category.id] = {
                'name': category.name,
                'weight': float(category.weight),
                'earned': total_earned,
                'possible': total_possible,
                'percentage': round(category_percentage, 2),
                'weighted_score': round(weighted_score, 2),
                'color': category.color
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
        summary = db.session.query(GradeSummary).filter_by(
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
            summary.updated_at = datetime.utcnow()
        else:
            summary = GradeSummary(
                id=str(uuid.uuid4()),
                user_id=user_id,
                lesson_id=lesson_id,
                current_score=total_weighted_score,
                percentage=total_weighted_score,
                letter_grade=letter_grade,
                gpa=gpa,
                is_passing=total_weighted_score >= float(config.passing_percentage),
                points_to_next_grade=json.dumps(goals.get('points_to_grades', {})),
                last_calculated=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
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
        from database.models.grade import GradeItem, GradeEntry
        from app import db
        
        # Get remaining items (not yet graded)
        all_items = db.session.query(GradeItem).filter_by(
            lesson_id=lesson_id,
            is_published=True
        ).all()
        
        graded_items = db.session.query(GradeEntry).filter_by(
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
        from database.models.grade import GradeConfig, GradeCategory, GradeItem, GradeEntry
        from app import db
        
        # Get current summary first
        current_summary = GradeController.calculate_grade_summary(lesson_id, user_id)
        
        if 'error' in current_summary:
            return current_summary
        
        # Get config
        config = db.session.query(GradeConfig).filter_by(lesson_id=lesson_id).first()
        grading_scale = json.loads(config.grading_scale)
        
        # Get categories
        categories = db.session.query(GradeCategory).filter_by(lesson_id=lesson_id).all()
        
        total_weighted_score = 0
        
        for category in categories:
            items = db.session.query(GradeItem).filter_by(
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
                    entry = db.session.query(GradeEntry).filter_by(
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

