from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist

from accounts.models import User
from .models import UserPermission, ModelPermissions, UserPermissionRelation


class AlreadyRegistered(Exception):
    """
    An attempt was made to register a model for objectpermissions more than once.
    """
    pass


#: Contains all the models that we've registered. A ``list`` of ``Model``\ s
registry = []


def register(model, permissions):
    """
    Register a model and permission set. It adds several functions to the model:
    """
    if model in registry:
        # raise AlreadyRegistered('The model %s has already been registered.' % model.__name__)
        return
    registry.append(model)

    opts = model._meta
    try:
        opts.get_field('user_perms_set')
    except FieldDoesNotExist:
        UserPermissionRelation().contribute_to_class(model, 'user_perms_set')

    setattr(model, 'perms', ModelPermissions(permissions))


# The following functions are added to the User objects

def grant_object_perm(self, instance, perm):
    """
    Grants permission ``perm`` to object ``instance`` for the :class:`User`
    
    This function is added to the :class:`User` models and
    is called as::
    
        a_user.grant_object_perm(an_object_instance, 'read')
    
    :param instance: A Django :class:`Model` instance
    :type instance: :class:`Model`
    :param perm: The permission(s) to grant
    :type perm: ``integer``, ``string``, ``list of string``
    """
    addl_perm = instance.perms.as_int(perm)
    query_args = {}
    if isinstance(self, User):
        try:
            the_permission = instance.user_perms_set.get(user=self)
        except UserPermission.DoesNotExist:
            the_permission = instance.user_perms_set.create(user=self)
    else:
        raise Exception("This method should only be attached to a User object.")
    the_permission.permission |= addl_perm
    the_permission.save()


def revoke_object_perm(self, instance, perm):
    """
    Remove the permission ``perm`` to object ``instance`` for the :class:`User` ``self`` .
    
    :param instance: A Django :class:`Model` instance
    :type instance: :class:`Model`
    :param perm: The name of the permission to revoke
    :type perm: ``integer``, ``string``, ``list of string``
    """
    remove_perm = instance.perms.as_int(perm)

    try:
        if isinstance(self, User):
            the_permission = instance.user_perms_set.get(user=self)
    except UserPermission.DoesNotExist:
        # Can't revoke what they don't have
        return
    the_permission.permission ^= remove_perm
    if the_permission.permission == 0:
        the_permission.delete()
    else:
        the_permission.save()


def revoke_all_object_perm(self, instance):
    """
    Remove all the permissions for this :class:`User`.
    
    :param instance: A Django :class:`Model` instance
    :type instance: :class:`Model`
    """
    try:
        if isinstance(self, User):
            instance.user_perms_set.get(user=self).delete()
    except UserPermission.DoesNotExist:
        # Can't revoke what they don't have
        return


def set_object_perm(self, instance, perm):
    """
    Sets the permission to the ``perm`` value. Same as revoking all privileges
    and granting ``perm``
    
    :param instance: The object on which to set the permissions
    :type instance:  ``Model``
    :param perm:  The permission(s) that should be set.
    :type perm:   ``int``, ``string`` or ``list of string``
    """
    perms = instance.perms.as_int(perm)
    if isinstance(self, User):
        try:
            the_permission = instance.user_perms_set.get(user=self)
        except UserPermission.DoesNotExist:
            the_permission = instance.user_perms_set.create(user=self)
    the_permission.permission = perms
    the_permission.save()


def user_has_object_perm(self, instance, perm, require_all=False):
    """
    Basic testing of user permissions. Permissions can be passed as an int, using the 
    object's ``perms`` attribute::
    
        obj.perms.perm1 + obj.perms.perm2
    
    Permissions can be referenced by name::
    
        'perm1'
    
    Permissions can be referenced by a list of names or ``int``s::
    
        ['perm1', 'perm2']
        [obj.perms.perm1, objs.perms.perm2]
    
    When passing in multiple permissions, you can force the checking that the 
    user has *all* the permissions by passing ``True`` as the third parameter. By
    default it returns ``True`` if the user has *any* of the permissions.
    
    Superusers *always* return ``True``
    
    Inactive users *always* return ``False``
    
    :param instance: The object for which the user may or may not have permissions.
    :type instance:  A Django model subclass that has been registered with :ref:`objectpermissions.register`
    :param perm:     Permission(s) to check for in either an integer, a string or a list of strings
    :type perm:      ``int``, ``string`` or ``list of string``
    :param require_all: Does the user need to have all the permissions? ``True``
                        if they do. **Default:** ``False``
    :type require_all:  ``bool``
    """
    if self.is_superuser:
        return True
    if not self.is_active:
        return False

    perms = instance.perms.as_int(perm)

    try:
        user_perm = instance.user_perms_set.get(user=self)
        if require_all:
            if user_perm.permission & perms == perms:
                return True
        else:
            if user_perm.permission & perms > 0:
                return True
    except UserPermission.DoesNotExist:
        pass


def user_has_all_object_perm(self, instance, perm):
    return self.has_object_perm(instance, perm, True)


def user_get_object_permissions(self, instance, format='int'):
    """
    Get the user's permissions for this object, formatted in a specific way.
    Format options:
    int: One integer with all permissions
    string_list: A list of the permission names
    int_list: A list of the permission values
    choices: A list of integer, string tuples for choice lists
    
    :param instance: A django :class:`Model` instance
    :type instance: :class:`Model`
    :param format: 'int', 'string_list', 'int_list', 'choices'. **Default:** 'int'
    :type format: ``string``
    """
    try:
        user_perm = instance.user_perms_set.get(user=self)
        formatter = getattr(instance.perms, "as_%s" % format, False)
        if formatter:
            return formatter(user_perm.permission)
        else:
            return user_perm.permission

    except UserPermission.DoesNotExist:
        if format == 'int':
            return 0
        else:
            return []


def user_get_object_permissions_as_string_list(self, instance):
    """
    Get a list of strings representing the user's permissions for this object
    """
    return self.get_object_perm(instance, 'string_list')


def user_get_object_permissions_as_int_list(self, instance):
    """
    Get a list of strings representing the user's permissions for this object
    """
    return self.get_object_perm(instance, 'int_list')


def user_get_object_permissions_as_choices(self, instance):
    """
    Get a list of strings representing the user's permissions for this object
    """
    return self.get_object_perm(instance, 'choices')


def user_get_objects_with_permission(self, model, permission):
    """
    Return all objects of type model where the user has the passed permissions
    """
    ctype = ContentType.objects.get_for_model(model)
    perms = model.perms.as_int(permission)
    return model.objects.filter(
        Q(pk__in=self.userpermission_set.filter(content_type=ctype).extra(
            where=['permission & %s > 0'], params=[perms]
        ).values_list('object_id', flat=True)))


if User not in registry:
    registry.append(User)
    setattr(User, 'grant_object_perm', grant_object_perm)
    setattr(User, 'set_object_perm', set_object_perm)
    setattr(User, 'revoke_object_perm', revoke_object_perm)
    setattr(User, 'revoke_all_object_perm', revoke_all_object_perm)
    setattr(User, 'has_object_perm', user_has_object_perm)
    setattr(User, 'has_any_object_perm', user_has_object_perm)
    setattr(User, 'has_all_object_perm', user_has_all_object_perm)
    setattr(User, 'get_object_perm', user_get_object_permissions)
    setattr(User, 'get_object_perm_as_str_list',
            user_get_object_permissions_as_string_list)
    setattr(User, 'get_object_perm_as_int_list',
            user_get_object_permissions_as_int_list)
    setattr(User, 'get_object_perm_as_choices',
            user_get_object_permissions_as_choices)
    setattr(User, 'get_objects_with_perms', user_get_objects_with_permission)
