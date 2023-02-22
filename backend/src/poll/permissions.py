from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from poll.utils import REDACTOR, AUTHOR


class IsPollOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsPollOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.owner == request.user


class IsPollOwnerDiskSpaceFree(permissions.BasePermission):
    message = 'Disk space is full'

    def has_object_permission(self, request, view, obj):
        return obj.owner.secretguestprofile.current_disk_space <= obj.owner.secretguestprofile.max_disk_space


class IsPollRedactor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user:
            return False

        access = user.poll_access.filter(poll=obj).first()
        if access and request.method != 'DELETE' and access.role == REDACTOR:
            return True
        return False


class IsQuestionOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.poll.owner == request.user


class IsQuestionRedactor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user:
            return False

        access = user.poll_access.filter(poll=obj.poll).first()
        if access and access.role == REDACTOR:
            return True
        return False


class IsSubQuestionQuestionRedactor():
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user:
            return False

        access = user.poll_access.filter(poll=obj.poll).first()
        if access and access.role == REDACTOR:
            return True
        return False


# TODO rewrite it
def check_question_permission(poll, request):
    user = request.user
    access = user.poll_access.filter(poll=poll)
    if poll.owner == user or request.user.is_staff:
        return True
    if access.exists():
        access = access.first()
        if access.role in [AUTHOR, REDACTOR]:
            return True
    raise PermissionDenied()


def check_item_permission(item, request):
    question = item.get_question()
    user = request.user
    poll = question.poll
    access = user.poll_access.filter(poll=poll)
    if poll.owner == user or request.user.is_staff:
        return True
    if access.exists():
        access = access.first()
        if access.role in [AUTHOR, REDACTOR]:
            return True
    raise PermissionDenied()
