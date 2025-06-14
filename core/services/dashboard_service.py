import logging
from django.db.models import Count, Q
from core.models import User, Document, PointsHistory, Program, DegreeLevel, UploadLog, Course, Semester, AcademicYear

# Import the specific serializers needed for nested data
from core.serializers.dashboard_serializers import (
    StudentPointsHistorySerializer,
    StudentUploadedDocumentSerializer,
)

logger = logging.getLogger(__name__)


class DashboardService:

    @staticmethod
    def get_admin_dashboard_data(user: User) -> dict:
        """
        Retrieves data for the admin dashboard.
        """
        try:
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()

            users_by_role = dict(
                User.objects.values('role').annotate(count=Count('id')).order_by('role').values_list('role', 'count'))

            total_documents = Document.objects.count()
            documents_pending_review = Document.objects.filter(status='pending').count()
            documents_approved = Document.objects.filter(status='approved').count()

            # Serialize recent document uploads directly here
            recent_document_uploads_queryset = Document.objects.select_related('course', 'semester').order_by(
                '-upload_timestamp')[:10]
            # --- FIX: Serialize the QuerySet using the nested serializer ---
            serialized_recent_uploads = StudentUploadedDocumentSerializer(recent_document_uploads_queryset,
                                                                          many=True).data

            recent_upload_reviews = []
            for log_entry in UploadLog.objects.select_related('document', 'reviewer').order_by('-review_timestamp')[
                             :10]:
                recent_upload_reviews.append({
                    "document_title": log_entry.document.title,
                    "reviewer_email": log_entry.reviewer.email,
                    "status": log_entry.status,
                    "review_timestamp": log_entry.review_timestamp.isoformat(),
                })

            return {
                "total_users": total_users,
                "active_users": active_users,
                "users_by_role": users_by_role,
                "total_documents": total_documents,
                "documents_pending_review": documents_pending_review,
                "documents_approved": documents_approved,
                "recent_document_uploads": serialized_recent_uploads,  # Pass the serialized data
                "recent_upload_reviews": recent_upload_reviews,
            }
        except Exception as e:
            logger.error(f"Error fetching admin dashboard data: {e}", exc_info=True)
            raise

    @staticmethod
    def get_student_dashboard_data(user: User) -> dict:
        """
        Retrieves data for the student dashboard.
        """
        try:
            current_points = user.points

            # --- FIX: Serialize the QuerySet for recent_points_history ---
            recent_points_history_queryset = PointsHistory.objects.filter(user=user).order_by('-timestamp')[:5]
            serialized_recent_points_history = StudentPointsHistorySerializer(recent_points_history_queryset,
                                                                              many=True).data

            student_documents = Document.objects.filter(uploader=user)
            uploaded_documents_summary = {
                "total": student_documents.count(),
                "pending": student_documents.filter(status='pending').count(),
                "approved": student_documents.filter(status='approved').count(),
                "rejected": student_documents.filter(status='rejected').count(),
            }

            # --- FIX: Serialize the QuerySet for my_recent_uploads ---
            my_recent_uploads_queryset = student_documents.select_related('course', 'semester').order_by(
                '-upload_timestamp')[:5]
            serialized_my_recent_uploads = StudentUploadedDocumentSerializer(my_recent_uploads_queryset, many=True).data

            my_program_info = {}
            if user.program:
                my_program_info = {
                    "program_name": user.program.name,
                    "degree_level_name": user.program.degree_level.name if user.program.degree_level else None,
                    "enrollment_year": user.enrollment_year,
                }

            my_academic_progress = {}
            if user.program and user.enrollment_year:
                # Adjust '2025' to dynamically get the current year or relevant academic year
                current_year_obj = AcademicYear.objects.filter(year_start__lte=2025, year_end__gte=2025).first()
                if current_year_obj:
                    semesters = Semester.objects.filter(
                        program=user.program,
                        academic_year=current_year_obj
                    ).order_by('number')

                    enrolled_courses_data = []
                    for semester in semesters:
                        # This logic needs refinement based on actual student-course enrollment
                        # For demonstration, assuming all courses in user's program
                        courses_in_semester = Course.objects.filter(program=user.program).values('id', 'name', 'code')
                        enrolled_courses_data.append({
                            "semester_name": semester.name,
                            "semester_number": semester.number,
                            "courses": list(courses_in_semester)
                        })
                    my_academic_progress['semesters'] = enrolled_courses_data

            return {
                "current_points": current_points,
                "recent_points_history": serialized_recent_points_history,  # Pass the serialized data
                "uploaded_documents_summary": uploaded_documents_summary,
                "my_recent_uploads": serialized_my_recent_uploads,  # Pass the serialized data
                "my_program_info": my_program_info,
                "my_academic_progress": my_academic_progress,
            }
        except Exception as e:
            logger.error(f"Error fetching student dashboard data for user {user.id}: {e}", exc_info=True)
            raise