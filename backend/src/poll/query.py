from rest_framework.exceptions import NotFound


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def get_or_404(classmodel, error_msg='Not found', **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        raise NotFound(error_msg)
