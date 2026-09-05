from rest_framework import permissions


class IsModer(permissions.BasePermission):
    """
    Проверяет, является ли пользователь модератором.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moders").exists()


class IsOwner(permissions.BasePermission):
    """
    Проверяет, является ли пользователь владельцем.
    """
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Просмотр — всем авторизованным.
    Редактирование — только владельцу профиля.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user

