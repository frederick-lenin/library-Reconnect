from rest_framework import permissions


class IsAdminOrLibrarian(permissions.BasePermission):
    """
    Custom permission to allow only admins and librarians to manage books.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'librarian']
    

class IsMember(permissions.BasePermission):
    """
    Custom permission to allow only member to manage books.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['member']