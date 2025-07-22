from app import db
from app.core.course_linkage import CourseLinkage

class CourseLinkageManager:
    def add_linkage(self, user_id, kmitl_course_identifier, google_classroom_id):
        # Check if a linkage already exists for the KMITL course identifier
        existing_linkage = CourseLinkage.query.filter_by(
            user_id=user_id,
            kmitl_course_identifier=kmitl_course_identifier
        ).first()

        if existing_linkage:
            # Update existing linkage
            existing_linkage.google_classroom_id = google_classroom_id
            db.session.commit()
            return existing_linkage
        else:
            # Create new linkage
            linkage = CourseLinkage(user_id=user_id, kmitl_course_identifier=kmitl_course_identifier, google_classroom_id=google_classroom_id)
            db.session.add(linkage)
            db.session.commit()
            return linkage

    def get_linkage_by_kmitl_identifier(self, user_id, kmitl_course_identifier):
        return CourseLinkage.query.filter_by(
            user_id=user_id,
            kmitl_course_identifier=kmitl_course_identifier
        ).first()

    def get_all_linkages_by_user(self, user_id):
        return CourseLinkage.query.filter_by(user_id=user_id).all()

    def delete_linkage(self, linkage_id):
        linkage = CourseLinkage.query.get(linkage_id)
        if linkage:
            db.session.delete(linkage)
            db.session.commit()
            return True
        return False

    def delete_linkage_by_kmitl_identifier(self, user_id, kmitl_course_identifier):
        linkage = self.get_linkage_by_kmitl_identifier(user_id, kmitl_course_identifier)
        if linkage:
            db.session.delete(linkage)
            db.session.commit()
            return True
        return False
