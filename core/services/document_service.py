# core/services/document_service.py

import logging
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet # <--- ADD THIS IMPORT

from core.models import Document, User # Import Document and User models
from rest_framework import serializers # Make sure this is imported if you're raising serializers.ValidationError

logger = logging.getLogger(__name__)

class DocumentService:
    """
    A service layer for all document-related business logic.
    This class handles operations like creation, updates, status changes, and deletion
    of documents, interacting directly with the Document model.
    """

    @staticmethod
    def create_document(validated_data, uploader: User) -> Document:
        """
        Creates a new document instance.
        Args:
            validated_data (dict): Validated data from the serializer.
            uploader (User): The user uploading the document.
        Returns:
            Document: The newly created document instance.
        Raises:
            ValidationError: If any issues during creation (e.g., integrity errors).
        """
        try:
            with transaction.atomic():
                validated_data['uploader'] = uploader
                validated_data['status'] = Document.DocumentStatus.PENDING # Default to pending

                # Extract file object to get content_type for file_format
                uploaded_file = validated_data.get('file')
                if uploaded_file:
                    validated_data['file_format'] = uploaded_file.content_type
                else:
                    validated_data['file_format'] = None # Or handle as required

                document = Document.objects.create(**validated_data)
                logger.info(f"Document '{document.title}' (ID: {document.id}) created by {uploader.email}.")
                return document
        except IntegrityError as e:
            logger.error(f"Integrity error creating document: {e}", exc_info=True)
            raise serializers.ValidationError({"detail": "A document with these details might already exist or related data is invalid."})
        except Exception as e:
            logger.error(f"Unexpected error creating document: {e}", exc_info=True)
            raise serializers.ValidationError({"detail": f"Failed to create document: {str(e)}"})

    @staticmethod
    def update_document_metadata(document_id: int, validated_data) -> Document:
        """
        Updates metadata for an existing document.
        Args:
            document_id (int): The ID of the document to update.
            validated_data (dict): Validated data for updating.
        Returns:
            Document: The updated document instance.
        Raises:
            Http404: If the document is not found.
            ValidationError: If any issues during update.
        """
        document = get_object_or_404(Document, id=document_id)
        try:
            with transaction.atomic():
                # Note: File itself is typically not updated via metadata update.
                # If file update is needed, it's often a separate upload or logic.
                for attr, value in validated_data.items():
                    setattr(document, attr, value)
                document.save()
                logger.info(f"Document '{document.title}' (ID: {document.id}) metadata updated.")
                return document
        except Exception as e:
            logger.error(f"Error updating document metadata (ID: {document_id}): {e}", exc_info=True)
            raise serializers.ValidationError({"detail": f"Failed to update document: {str(e)}"})

    @staticmethod
    def change_document_status(document_id: int, new_status: str, reviewer: User) -> Document:
        """
        Changes the status of a document (e.g., pending, approved, rejected).
        Args:
            document_id (int): The ID of the document.
            new_status (str): The new status to set.
            reviewer (User): The user performing the status change.
        Returns:
            Document: The updated document instance.
        Raises:
            Http404: If the document is not found.
            ValidationError: If the status is invalid or update fails.
        """
        document = get_object_or_404(Document, id=document_id)

        # Basic validation for status choices
        if new_status not in [choice[0] for choice in Document.DocumentStatus.choices]:
            raise serializers.ValidationError({"new_status": "Invalid document status."})

        try:
            with transaction.atomic():
                document.status = new_status
                document.save()
                logger.info(f"Document '{document.title}' (ID: {document.id}) status changed to '{new_status}' by {reviewer.email}.")
                return document
        except Exception as e:
            logger.error(f"Error changing document status (ID: {document_id}) to {new_status}: {e}", exc_info=True)
            raise serializers.ValidationError({"detail": f"Failed to change document status: {str(e)}"})

    @staticmethod
    def delete_document(document_id: int):
        """
        Deletes a document from the database and its associated file from storage.
        Args:
            document_id (int): The ID of the document to delete.
        Raises:
            Http404: If the document is not found.
            ValidationError: If deletion fails.
        """
        document = get_object_or_404(Document, id=document_id)
        document_title = document.title
        try:
            with transaction.atomic():
                # Deleting the model instance that has a FileField will
                # automatically delete the associated file from S3-compatible storage
                # if DEFAULT_FILE_STORAGE is set to S3Boto3Storage.
                document.delete()
                logger.info(f"Document '{document_title}' (ID: {document.id}) deleted successfully.")
        except Exception as e:
            logger.error(f"Error deleting document (ID: {document_id}): {e}", exc_info=True)
            raise serializers.ValidationError({"detail": f"Failed to delete document: {str(e)}"})

    @staticmethod
    def get_document(document_id: int) -> Document:
        """Retrieves a single document by ID."""
        return get_object_or_404(Document.objects.select_related('course', 'academic_year', 'uploader'), id=document_id)

    @staticmethod
    def get_all_documents(filter_kwargs=None) -> QuerySet: # <--- QuerySet type hint now recognized
        """Retrieves all documents, with optional filtering."""
        if filter_kwargs is None:
            filter_kwargs = {}
        return Document.objects.select_related('course', 'academic_year', 'uploader').filter(**filter_kwargs)