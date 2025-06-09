# core/permissions/role_permissions.py

from rest_framework.permissions import BasePermission

class IsAdminUserRole(BasePermission):
    """
    Allows access only to users with role='admin'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == "admin"
        )


class IsStaffUserRole(BasePermission):
    """
    Allows access only to users with role='staff'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == "staff"
        )


class IsStudentUserRole(BasePermission):
    """
    Allows access only to users with role='student'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == "student"
        )


class IsAdminOrStaffUserRole(BasePermission):
    """
    Allows access to users with role='admin' or role='staff'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ["admin", "staff"]
        )
