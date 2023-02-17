from rest_framework.response import Response


def get_data_response(serializer, items, many=True, check_valid=False, status=200):
    if not items:
        return Response([])

    if check_valid:
        items_serializer = serializer(data=items, many=many)
        items_serializer.is_valid(raise_exception=True)

    else:
        items_serializer = serializer(items, many=many)

    return Response(data=items_serializer.data, status=status)


def get_upload_path(instance, filename):
    return f"{str(instance.owner.pk)}/{filename}/"


def get_host_id_model(obj):
    """
    Получает id родительского документа и имя модели
    """
    if str(obj.__class__.__name__) == "Shot":
        frame = obj.host_frame
        return [frame.host_storyboard.id, "storyboard"]
    elif str(obj.__class__.__name__) == "CallsheetLogo":
        return [obj.host_callsheet.id, "callsheet"]
    elif str(obj.__class__.__name__) in "LocationMap":
        location = obj.host_location
        return [location.host_callsheet.id, "callsheet"]
    elif str(obj.__class__.__name__) in ['Callsheet',
                                         'Storyboard',
                                         'Shootingplan',
                                         'File',
                                         'Text',
                                         'Link',
                                         'Timing',
                                         'Document']:
        return [obj.id, obj.__class__.__name__.lower()]


def get_doc_upload_path(instance, filename):
    if str(instance.__class__.__name__) == "File":
        return f"{str(instance.owner.pk)}/file/{filename}/"
    pkid, model = get_host_id_model(instance)
    return f"{str(instance.owner.pk)}/{model}/{pkid}/{filename}"


def get_icon_upload_path(instance, filename):
    """creating a path for standard icon files."""
    return f'docicons/{filename}'
