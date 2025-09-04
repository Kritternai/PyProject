"""
Task routes following Clean Architecture principles.
Defines HTTP endpoints for task operations.
"""

from flask import Blueprint
from ..controllers.task_controller import TaskController
from ..middleware.auth_middleware import login_required

# Create blueprint
task_bp = Blueprint('task', __name__, url_prefix='/api/tasks')

# Initialize controller
task_controller = TaskController()


@task_bp.route('', methods=['POST'])
@login_required
def create_task():
    """Create a new task."""
    return task_controller.create_task()


@task_bp.route('/<task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Get task by ID."""
    return task_controller.get_task(task_id)


@task_bp.route('', methods=['GET'])
@login_required
def get_user_tasks():
    """Get tasks for current user."""
    return task_controller.get_user_tasks()


@task_bp.route('/<task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update task."""
    return task_controller.update_task(task_id)


@task_bp.route('/<task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete task."""
    return task_controller.delete_task(task_id)


@task_bp.route('/<task_id>/status', methods=['PUT'])
@login_required
def change_task_status(task_id):
    """Change task status."""
    return task_controller.change_task_status(task_id)


@task_bp.route('/<task_id>/progress', methods=['PUT'])
@login_required
def update_task_progress(task_id):
    """Update task progress."""
    return task_controller.update_task_progress(task_id)


@task_bp.route('/<task_id>/time', methods=['PUT'])
@login_required
def add_time_spent(task_id):
    """Add time spent on task."""
    return task_controller.add_time_spent(task_id)


@task_bp.route('/overdue', methods=['GET'])
@login_required
def get_overdue_tasks():
    """Get overdue tasks."""
    return task_controller.get_overdue_tasks()


@task_bp.route('/due-soon', methods=['GET'])
@login_required
def get_due_soon_tasks():
    """Get tasks due soon."""
    return task_controller.get_due_soon_tasks()


@task_bp.route('/high-priority', methods=['GET'])
@login_required
def get_high_priority_tasks():
    """Get high priority tasks."""
    return task_controller.get_high_priority_tasks()


@task_bp.route('/search', methods=['GET'])
@login_required
def search_tasks():
    """Search tasks."""
    return task_controller.search_tasks()


@task_bp.route('/statistics', methods=['GET'])
@login_required
def get_task_statistics():
    """Get task statistics."""
    return task_controller.get_task_statistics()
