# core/views/v1/documents/document_views.py

import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied # Import explicitly for clarity
from rest_framework import serializers
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Import your custom permission classes
from core.permissions.role_permissions import (
    IsAdminUserRole,
    IsStaffUserRole,
    IsAdminOrStaffUserRole,
    IsStudentUserRole
)
from core.mixins.response_mixins import APIResponseMixin

# Import the DocumentService
from core.services.document_service import DocumentService

# Import the Document serializers
from core.serializers.document_serializers import (
    DocumentUploadSerializer,
    DocumentRetrieveSerializer,
    DocumentUpdateSerializer,
    DocumentStatusChangeSerializer
)
from core.models import Document
# IMPORT SemesterNumber and DocumentStatus DIRECTLY from base.py
from core.models.base import SemesterNumber, DocumentStatus # <--- CORRECTED IMPORT LOCATION

logger = logging.getLogger(__name__)

# --- DocumentUploadView ---
class DocumentUploadView(APIView, APIResponseMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Upload a new academic document.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['file', 'title', 'doc_type', 'course', 'academic_year', 'semester_number'],
            properties={
                'file': openapi.Schema(type=openapi.TYPE_FILE, description='The document file (PDF, JPG, PNG, DOCX, TXT).'),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the document.'),
                'doc_type': openapi.Schema(type=openapi.TYPE_STRING, enum=[choice[0] for choice in Document.DocumentType.choices], description='Type of the document (e.g., insem, endsem, assignment).'),
                'course': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the associated Course.'),
                'academic_year': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the associated Academic Year.'),
                # CORRECTED LINE: Reference SemesterNumber directly, not via Document
                'semester_number': openapi.Schema(type=openapi.TYPE_STRING, enum=[choice[0] for choice in SemesterNumber.choices], description='Semester number (e.g., 1, 2, 3).'),
            },
            consumes=['multipart/form-data']
        ),
        responses={
            201: openapi.Response('Document uploaded successfully.', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING),
                            'document_id': openapi.Schema(type=openapi.TYPE_INTEGER)}
            )),
            400: 'Bad Request', 401: 'Unauthorized', 403: 'Permission Denied', 500: 'Internal Server Error',
        },
        tags=['Documents']
    )
    def post(self, request, *args, **kwargs):
        logger.info(f"User {request.user.email} (Role: {request.user.role}) attempting to upload a document.")

        serializer = DocumentUploadSerializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            document = DocumentService.create_document(serializer.validated_data, request.user)
            logger.info(f"Document (ID: {document.id}) uploaded successfully by {request.user.email}.")
            return self.success_response(
                message="Document uploaded successfully.",
                data={"document_id": document.id},
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.exception(f"Document upload failed for user {request.user.email}: {e}")
            # Differentiate serializer validation errors from unexpected errors
            status_code_response = status.HTTP_400_BAD_REQUEST
            if not isinstance(e, (serializers.ValidationError, ValueError, TypeError)): # Add other expected validation errors
                status_code_response = status.HTTP_500_INTERNAL_SERVER_ERROR
            return self.error_response(
                message=str(e),
                status_code=status_code_response
            )


# --- Document ListView ---
class DocumentListView(APIView, APIResponseMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all academic documents. Filters available: status, uploader_id.",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              # CORRECTED LINE: Reference DocumentStatus directly
                              enum=[choice[0] for choice in DocumentStatus.choices], description="Filter by document status (e.g., 'pending', 'approved', 'rejected')."),
            openapi.Parameter('uploader_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description="Filter by uploader ID (Admin/Staff only)."),
        ],
        responses={
            200: openapi.Response('List of documents', DocumentRetrieveSerializer(many=True)),
            401: 'Unauthorized', 403: 'Permission Denied', 500: 'Internal Server Error',
        },
        tags=['Documents']
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"User {request.user.email} (Role: {request.user.role}) requesting list of documents.")
        filter_kwargs = {}

        # Important: Implement role-based filtering logic *within* the view's get method
        if request.user.role == 'student':
            filter_kwargs['status'] = DocumentStatus.APPROVED.value # Corrected for consistency with imported enum
            if request.query_params.get('my_uploads', 'false').lower() == 'true':
                filter_kwargs['uploader'] = request.user
            if request.query_params.get('uploader_id') and str(request.user.id) != request.query_params.get('uploader_id'):
                logger.warning(f"Student {request.user.email} attempted to view documents of uploader ID {request.query_params.get('uploader_id')}.")
                return self.error_response(
                    message="Students can only view their own uploads or general approved documents.",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            elif request.query_params.get('uploader_id') and str(request.user.id) == request.query_params.get('uploader_id'):
                 filter_kwargs['uploader_id'] = request.user.id
        elif IsAdminOrStaffUserRole().has_permission(request, self):
            status_param = request.query_params.get('status')
            if status_param:
                filter_kwargs['status'] = status_param
            uploader_id = request.query_params.get('uploader_id')
            if uploader_id:
                filter_kwargs['uploader_id'] = uploader_id
        else:
            filter_kwargs['status'] = DocumentStatus.APPROVED.value


        try:
            documents = DocumentService.get_all_documents(filter_kwargs=filter_kwargs)
            serializer = DocumentRetrieveSerializer(documents, many=True)
            logger.info(f"Retrieved {len(serializer.data)} documents for user {request.user.email}.")
            return self.success_response(
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(f"Error listing documents for user {request.user.email}: {e}")
            return self.error_response(
                message="Failed to retrieve documents.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# --- Document Detail/Update/Delete View ---
class DocumentDetailView(APIView, APIResponseMixin):
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        """Helper method to get document instance or raise 404."""
        from django.http import Http404 # Ensure Http404 is imported if used directly
        from rest_framework.exceptions import PermissionDenied # Ensure PermissionDenied is imported

        try:
            document = DocumentService.get_document(id)
            # Internal object-level permission check based on role
            if not (IsAdminOrStaffUserRole().has_permission(self.request, self) or
                    (self.request.user.role == 'student' and
                     (document.uploader == self.request.user or document.status == DocumentStatus.APPROVED.value))): # Corrected to use .value
                logger.warning(f"User {self.request.user.email} (Role: {self.request.user.role}) attempted unauthorized access to document ID {id}.")
                raise PermissionDenied("You do not have permission to access this document.")
            return document
        except Http404:
            raise Http404("Document not found.") # Re-raise Http404 to get proper DRF 404 behavior
        except PermissionDenied:
            raise # Re-raise PermissionDenied
        except Exception as e:
            logger.exception(f"Document with ID {id} not found or access denied for {self.request.user.email}: {e}")
            raise # Re-raise to let the outer try/except in the view handle it for consistent APIResponseMixin usage


    @swagger_auto_schema(
        operation_description="Retrieve an academic document by ID.",
        responses={
            200: openapi.Response('Document details', DocumentRetrieveSerializer),
            401: 'Unauthorized', 403: 'Permission Denied', 404: 'Not Found', 500: 'Internal Server Error',
        },
        tags=['Documents']
    )
    def get(self, request, id, *args, **kwargs):
        logger.info(f"User {request.user.email} (Role: {request.user.role}) requesting details for document ID: {id}.")
        try:
            document = self.get_object(id)
            serializer = DocumentRetrieveSerializer(document)
            return self.success_response(
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Http404 as e:
            return self.error_response(
                message=str(e),
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e: # Catch other exceptions including PermissionDenied
            status_code_response = status.HTTP_403_FORBIDDEN if isinstance(e, PermissionDenied) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return self.error_response(
                message=str(e),
                status_code=status_code_response
            )

    @swagger_auto_schema(
        operation_description="Update an academic document by ID (full update).",
        request_body=DocumentUpdateSerializer,
        responses={
            200: openapi.Response('Document updated successfully.', DocumentRetrieveSerializer),
            400: 'Bad Request', 401: 'Unauthorized', 403: 'Permission Denied', 404: 'Not Found', 500: 'Internal Server Error',
        },
        tags=['Documents']
    )
    def put(self, request, id, *args, **kwargs):
        logger.info(f"User {request.user.email} (Role: {request.user.role}) attempting full update for document ID: {id}.")
        # Internal check: Only Admin/Staff can update
        if not IsAdminOrStaffUserRole().has_permission(request, self):
            logger.warning(f"User {request.user.email} (Role: {request.user.role}) attempted unauthorized document update (ID: {id}).")
            return self.error_response(
                message="Only administrators and staff can update documents.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        try:
            document = self.get_object(id)
            serializer = DocumentUpdateSerializer(data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            updated_document = DocumentService.update_document_metadata(document.id, serializer.validated_data)
            return self.success_response(
                data=DocumentRetrieveSerializer(updated_document).data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(f"Document update failed for ID {id} by {request.user.email}: {e}")
            status_code_response = status.HTTP_400_BAD_REQUEST if isinstance(e, serializers.ValidationError) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return self.error_response(
                message=str(e),
                status_code=status_code_response
            )

    @swagger_auto_schema(
        operation_description="Partially update an academic document by ID.",
        request_body=DocumentUpdateSerializer,
        responses={
            200: openapi.Response('Document partially updated successfully.', DocumentRetrieveSerializer),
            400: 'Bad Request', 401: 'Unauthorized', 403: 'Permission Denied', 404: 'Not Found', 500: 'Internal Server Error',
        },
        tags=['Documents']
    )
    def patch(self, request, id, *args, **kwargs):
        logger.info(f"User {request.user.email} (Role: {request.user.role}) attempting partial update for document ID: {id}.")
        # Internal check: Only Admin/Staff can update
        if not IsAdminOrStaffUserRole().has_permission(request, self):
            logger.warning(f"User {request.user.email} (Role: {request.user.role}) attempted unauthorized document partial update (ID: {id}).")
            return self.error_response(
                message="Only administrators and staff can update documents.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        try:
            document = self.get_object(id)
            serializer = DocumentUpdateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_document = DocumentService.update_document_metadata(document.id, serializer.validated_data)
            return self.success_response(
                data=DocumentRetrieveSerializer(updated_document).data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(f"Document partial update failed for ID {id} by {request.user.email}: {e}")
            status_code_response = status.HTTP_400_BAD_REQUEST if isinstance(e, serializers.ValidationError) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return self.error_response(
                message=str(e),
                status_code=status_code_response
            )

    @swagger_auto_schema(
        operation_description="Delete an academic document by ID.",
        responses={
            204: 'No Content (Delete success)',
            401: 'Unauthorized', 403: 'Permission Denied', 404: 'Not Found', 500: 'Internal Server Error',
        },
        tags=['Documents']
    )
    def delete(self, request, id, *args, **kwargs):
        logger.info(f"User {request.user.email} (Role: {request.user.role}) attempting to delete document ID: {id}.")
        # Internal check: Only Admin/Staff can delete
        if not IsAdminOrStaffUserRole().has_permission(request, self):
            logger.warning(f"User {request.user.email} (Role: {request.user.role}) attempted unauthorized document deletion (ID: {id}).")
            return self.error_response(
                message="Only administrators and staff can delete documents.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        try:
            document = self.get_object(id)
            DocumentService.delete_document(document.id)
            logger.info(f"Document ID {id} deleted successfully by {request.user.email}.")
            return self.success_response(
                message="Document deleted successfully.",
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            logger.exception(f"Document deletion failed for ID {id} by {request.user.email}: {e}")
            status_code_response = status.HTTP_400_BAD_REQUEST if isinstance(e, serializers.ValidationError) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return self.error_response(
                message=str(e),
                status_code=status_code_response
            )


# --- Document Status Change View ---
class DocumentStatusChangeView(APIView, APIResponseMixin):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change the status of an academic document (e.g., 'approved', 'rejected').",
        request_body=DocumentStatusChangeSerializer,
        responses={
            200: openapi.Response('Document status updated successfully.', DocumentRetrieveSerializer),
            400: 'Bad Request', 401: 'Unauthorized', 403: 'Permission Denied', 404: 'Not Found', 500: 'Internal Server Error',
        },
        tags=['Documents']
    )
    def patch(self, request, id, *args, **kwargs):
        logger.info(f"User {request.user.email} (Role: {request.user.role}) attempting to change status for document ID: {id}.")
        # Internal check: Only Admin/Staff can change status
        if not IsAdminOrStaffUserRole().has_permission(request, self):
            logger.warning(f"User {request.user.email} (Role: {request.user.role}) attempted unauthorized status change for document ID {id}.")
            return self.error_response(
                message="Only administrators and staff can change document status.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        from django.shortcuts import get_object_or_404
        try:
            document = get_object_or_404(Document, id=id)
            serializer = DocumentStatusChangeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_status = serializer.validated_data['new_status']
            updated_document = DocumentService.change_document_status(document.id, new_status, request.user)
            logger.info(f"Document ID {id} status changed to '{new_status}' by {request.user.email}.")
            return self.success_response(
                message="Document status updated successfully.",
                data=DocumentRetrieveSerializer(updated_document).data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception(f"Document status change failed for ID {id} by {request.user.email}: {e}")
            status_code_response = status.HTTP_400_BAD_REQUEST if isinstance(e, serializers.ValidationError) else status.HTTP_500_INTERNAL_SERVER_ERROR
            return self.error_response(
                message=str(e),
                status_code=status_code_response
            )

    # Helper method for status view as it's not a generic view
    def get_object_or_404(self, queryset, *args, **kwargs):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(queryset, *args, **kwargs)