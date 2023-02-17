import os
import shutil
import uuid
from pprint import pprint

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import utils
from rest_framework.exceptions import ValidationError

import settings
from accounts.models import User
from callsheets.models import Callsheetmember, Location, LocationMap, CallsheetLogo, Callsheet
from common.models import UserCell
from projects import models
from projects.models import Project
from shootingplans.models import Unit, Shootingplan
from shootingplans.serializers import UnitframeSerializer
from storyboards.models import Frame
from storyboards.serializers import ChronoframeSerializer
from timing.models import TimingGroup, Timing


def get_model(model_name):
    model_app_name = ContentType.objects.get(model=model_name).app_label
    return apps.get_model(model_app_name, model_name.capitalize())


def unpack_nested_kwargs(kwargs, self_base):
    print('vvvvvvvvvvvvvvvvv')
    print(23, 'unpack_nested_kwargs')
    print(kwargs)

    _, root_name, super_name, parent_name, host_name = [None] * 5
    _pk, root_pk, super_pk, parent_pk, host_pk, base_pk = [None] * 6

    is_pk = None
    if 'pk' in kwargs:
        print(31)
        is_pk = True
        base_pk = kwargs.pop('pk')

    kw_len = len(kwargs)
    kw_keys = [None] * (5 - kw_len) + list(kwargs.keys())
    kw_vals = [None] * (5 - kw_len) + list(kwargs.values())
    _, root_name, super_name, parent_name, host_name = kw_keys
    _pk, root_pk, super_pk, parent_pk, host_pk = kw_vals

    if is_pk:
        print(42)
        kwargs['pk'] = base_pk
    ret = {
        'su': _[:-3] if _ else None,
        'su_pk': _pk,
        'root': root_name[:-3] if root_name else None,
        'root_pk': root_pk,
        'super': super_name[:-3] if super_name else None,
        'super_pk': super_pk,
        'parent': parent_name[:-3] if parent_name else None,
        'parent_pk': parent_pk,
        'host': host_name[:-3] if host_name else None,
        'host_pk': host_pk,
        'base': self_base,
        'base_pk': base_pk
    }
    pprint(ret)
    print('^^^^^^^^^^^^^^^^^^^^')
    return ret


def get_object_or_404(model, pk):
    try:
        return get_model(model).objects.get(pk=pk)
    except (ObjectDoesNotExist, utils.IntegrityError):
        raise ValidationError(
            {"error": {"msg": f"{model.capitalize()}[{pk}] not found"}})


def organize_data_row_sort_arrays(instance):
    instance_has_userfields = False
    instance_data_row_attribute = None
    for attr in dir(instance):
        if attr.endswith('frames') or attr == 'locations':
            instance_data_row_attribute = getattr(instance, attr)
        if attr == 'userfields':
            instance_has_userfields = True
    instance_data_row = list(instance_data_row_attribute.values('id'))
    instance_data_row_ids = [data_row['id'] for data_row in instance_data_row]
    if set(instance_data_row_ids) != set(instance.data_row_order):
        diff = list(set(instance_data_row_ids)
                    .difference(set(instance.data_row_order)))
        instance.data_row_order += diff

    if instance.data_row_order:
        for idx in reversed(instance.data_row_order):
            if idx not in instance_data_row_ids:
                instance.data_row_order.remove(idx)
    else:
        for ident in instance_data_row_ids:
            instance.data_row_order.append(ident)

    if instance_has_userfields and instance._meta.object_name != 'Callsheet':
        if Frame.objects.first():
            frame = instance_data_row_attribute.first()
            column_ids = list(frame.userfields.values('field_id'))
            for idx in reversed(instance.col_order):
                if {'field_id': idx} not in column_ids:
                    instance.col_order.remove(idx)
        else:
            instance.col_order = []

    # отключаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = False

    instance.save()

    # включаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = True


def contact_to_callsheetmember(cnt, callsheet):
    member_data = {
        'host_callsheet_id': callsheet.id,
        'name': cnt.name,
        'phone': cnt.phone,
        'email': cnt.email,
        'department': cnt.department,
        'position': cnt.position,
        'owner': cnt.owner
    }
    return Callsheetmember.objects.create(**member_data)


def add_userfields(user, host_obj, new_obj):
    """
    Получение существующих юзер.колонок для модели и их добавление
    ко всем участникам или добавление к строкам этого-же документа
    """
    print(139, 'common.add_userfields')
    new_obj_name = new_obj.__class__.__name__
    columns = []
    if new_obj_name == 'Callsheetmember':
        columns = host_obj.member_columns.all()
    elif new_obj_name in ['Frame', 'Unitframe']:
        columns = host_obj.frame_columns.all()
    for usercolumn in columns:
        usercell = UserCell.objects.create(
            host_usercolumn=usercolumn, owner=user)
        if (new_obj_name == 'Unitframe' and new_obj.sbdframe) or \
            new_obj_name == 'Frame' or new_obj_name == 'Callsheetmember':
            new_obj.userfields.add(usercell)


def insert_frames(user, base, instance, frames_ids: list):
    print(165, 'utils insert_frames')
    for frame_id in frames_ids:
        frame = get_object_or_404('frame', frame_id)
        frame_data = {f'host_{base}': instance.id,
                      'sbdframe_id': frame.id}
        serializer = None
        if base == 'chrono':
            serializer = ChronoframeSerializer
        elif base == 'unit':
            serializer = UnitframeSerializer
        print(150, 'pass context')
        serializer = serializer(data=frame_data, context={'user': user})
        print(152, serializer.__class__.__name__)
        serializer.is_valid(raise_exception=True)
        new_frame = serializer.create(serializer.validated_data)
        instance.data_row_order.append(new_frame.id)
        instance.save()
        add_userfields(user, instance, new_frame)


def check_file_size(request, user):
    """
    Проверяет превышает ли размер загружаемого файла в совокупности с
    размером уже загруженных пользователем файлов установленный лимит.
    Если лимит не превышен, считает общий размер файлов на диске.
    """
    user = User.objects.filter(pkid=user.pkid).first()
    disk_space = user.disk_space if user.disk_space else 0
    for filename, file in request.FILES.items():
        file_size = file.size
        if file_size + disk_space < settings.DISK_SIZE:
            disk_space += file_size
        else:
            return False
    return disk_space


def change_disk_space(user, disk_space):
    """
    При загрузке файла обновляет занятое место на диске у пользователя.
    """
    user = User.objects.filter(pkid=user.pkid).first()
    user.disk_space = disk_space
    user.save()


def recount_disk_space(user):
    """
    Пересчитывает при обновлении файла общий вес файлов на диске
    у пользователя.
    """
    folder = os.path.join(os.getcwd(), settings.MEDIA_ROOT, str(user.pkid))
    size = 0
    for path, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    user = User.objects.filter(pkid=user.pkid).first()
    user.disk_space = size
    user.save()
    return size


def find_host_project(kw):
    """
    Ищет PKID проекта по id документа.
    """
    for key, value in kw.items():
        if value == 'project':
            pk = int(kw.get(f'{key}_pk'))
            return Project.objects.filter(pk=pk).first()


def update_host_modified_date(kw, user_email):
    """
    Обновляет время и юзера последнего изменения сториборда, вызывного или шутингплана
    """
    for key, value in kw.items():
        if value in ["storyboard", "callsheet", "shootingplan"]:
            pk = int(kw.get(f'{key}_pk'))
            instance = get_model(value).objects.filter(
                id=pk).first()
            instance.last_modified_user = user_email
            instance.save()


def count_space_per_object(user, obj, doc_type):
    """
    Получает папку, в которой лежат файлы конкретного документа и
    считает вес каждого файла.
    """
    if isinstance(obj, File):
        folder = os.path.join(os.getcwd(),
                              settings.MEDIA_ROOT,
                              str(user.pkid),
                              doc_type)
    else:
        folder = os.path.join(os.getcwd(),
                              settings.MEDIA_ROOT,
                              str(user.pkid),
                              doc_type,
                              str(obj.id))
    exist_folder = os.path.exists(folder)
    size = 0
    if not exist_folder:
        return size
    for path, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return size


def like_or_dislike_object(user, object_type):
    """
    Ставит или убирает лайк. Затем сохраняет информацию
    о наличии или отсутствии лайка в БД.
    """
    user = get_model('user').objects.filter(pk=user.pk).first()
    if object_type == 'bordomatic':
        user.like = False if user.like else True
        user.save()
        return user.like
    elif object_type == 'document':
        user.document_like = False if user.document_like else True
        user.save()
        return user.document_like


def copy_file(parent_object, related_object=None):
    """
    Функция, отвечающая за копирование объекта с файлом.
    """
    if related_object:
        file_field_instance = getattr(related_object, 'file')
        owner_pk = str(related_object.owner.pk)
    else:
        file_field_instance = getattr(parent_object, 'file')
        owner_pk = str(parent_object.owner.pk)
    if file_field_instance:
        file_path = os.path.join(os.getcwd(),
                                 settings.MEDIA_ROOT,
                                 file_field_instance.name)
        if isinstance(parent_object, Callsheet):
            pk = str(parent_object.pk)
            model = 'callsheet'
        elif isinstance(parent_object, models.File):
            pk = str(parent_object.pk)
            model = 'file'
        else:
            pk = str(parent_object.host_callsheet.pk)
            model = 'callsheet'
        new_path = os.path.join(os.getcwd(),
                                settings.MEDIA_ROOT,
                                owner_pk,
                                model,
                                pk)
        if not os.path.isdir(new_path):
            os.mkdir(new_path)
        new_path = shutil.copy(file_path, new_path)
        return new_path


def construct_new_instance_with_file(object, new_path, project_id=None):
    """
    Создает объект класса с файлом.
    """
    instance = get_model(str(object.__class__.__name__).lower())(
            name=object.name,
            owner=object.owner,
            col_order=object.col_order,
            created_at=object.created_at,
            data_row_order=object.data_row_order,
            description=object.description,
            last_modified_date=object.last_modified_date,
            last_modified_user=object.last_modified_user,
            tag_color=object.tag_color,
            file=File(open(new_path, 'rb'), name=os.path.split(object.file.name)[-1])
        )
    if isinstance(object, models.File):
        instance.host_project = models.Project.objects.filter(pk=project_id).first()
        instance.document_logo = None
    return instance


def duplicate_object(parent_object, project_id, host=None):
    """
    Копирует инстанс класса со всеми child объектами, в том числе, связанными
    foreign keys:
        1.  Собирает объекты, связанные с родительским объектов с помощью foreign keys и m2m relations.
        2.  Копирует родительский объект
        3a. Копирует child объекты вместе с их child объектами.
        3b. Создает новые m2m relations.
    """
    related_objects_to_copy = []
    relations_to_set = {}
    # Iterate through all the fields in the parent object looking for related fields
    for field in parent_object._meta.get_fields():
        if field.one_to_many:
            # One to many fields are backward relationships where many child
            # objects are related to the parent. Enumerate them and save a list
            # so we can copy them after duplicating our parent object.
            print(f'Found a one-to-many field: {field.name}')

            # 'field' is a ManyToOneRel which is not iterable, we need to get
            # the object attribute itself.
            related_object_manager = getattr(parent_object, field.name)
            related_objects = list(related_object_manager.all())
            if related_objects:
                print(f' - {len(related_objects)} related objects to copy')
                related_objects_to_copy += related_objects

        elif field.many_to_one:
            # In testing, these relationships are preserved when the parent
            # object is copied, so they don't need to be copied separately.
            print(f'Found a many-to-one field: {field.name}')

        elif field.many_to_many:
            # Many to many fields are relationships where many parent objects
            # can be related to many child objects. Because of this the child
            # objects don't need to be copied when we copy the parent, we just
            # need to re-create the relationship to them on the copied parent.
            print(f'Found a many-to-many field: {field.name}')
            related_object_manager = getattr(parent_object, field.name)
            relations = list(related_object_manager.all())
            if relations:
                print(f' - {len(relations)} relations to set')
                relations_to_set[field.name] = relations
    # Duplicate the parent object
    if isinstance(parent_object, Callsheet) or isinstance(parent_object, Shootingplan) or isinstance(parent_object, Timing):

        # Keep the original pk of the copied object
        old_parent_obj_pk = parent_object.pk

        parent_object.pk = None
        parent_object.name += " копия"
        parent_object.host_project = models.Project.objects.filter(pk=project_id).first()
        parent_object.order_id = uuid.uuid4()
        parent_object.doc_uuid = None

        # Copying the document logo
        copy_document_logo(parent_object, old_parent_obj_pk)

        parent_object.save()

    elif isinstance(parent_object, TimingGroup):
        parent_object.pk = None
        parent_object.host_timing = host
        parent_object.save()
    elif isinstance(parent_object, Location) or isinstance(parent_object, Callsheetmember):
        parent_object.pk = None
        parent_object.host_callsheet = host
        parent_object.save()
    elif isinstance(parent_object, Unit):
        parent_object.pk = None
        parent_object.host_storyboard = host
        parent_object.save()
    elif isinstance(parent_object, models.File):
        new_path = copy_file(parent_object)
        instance = construct_new_instance_with_file(parent_object, new_path, project_id)
        instance.name += " копия"
        instance.save()
    else:
        parent_object.pk = None
        parent_object.name += " копия"
        parent_object.order_id = uuid.uuid4()
        parent_object.document_logo = None
        parent_object.save()
    print(f'Copied parent object ({str(parent_object)})')
    # Copy the one-to-many child objects and relate them to the copied parent
    for related_object in related_objects_to_copy:
        # Iterate through the fields in the related object to find the one that
        # relates to the parent model.
        for related_object_field in related_object._meta.fields:
            if related_object_field.related_model == parent_object.__class__:
                # If the related_model on this field matches the parent
                # object's class, perform the copy of the child object and set
                # this field to the parent object, creating the new
                # child -> parent relationship. if object is Location or Callsheetmember
                # duplicates it as parent obj.
                if isinstance(related_object, Location) or isinstance(related_object, Callsheetmember) \
                    or isinstance(related_object, Unit) or isinstance(related_object, TimingGroup):
                    duplicate_object(related_object, project_id, host=parent_object)
                elif not isinstance(related_object, LocationMap) and \
                    not isinstance(related_object, CallsheetLogo):
                    related_object.pk = None
                    setattr(related_object, related_object_field.name, parent_object)
                    related_object.save()

                    text = str(related_object)
                    text = (text[:40] + '..') if len(text) > 40 else text
                    print(f'|- Copied child object ({text})')
                else:
                    new_path = copy_file(parent_object, related_object)
                    instance = construct_new_instance_with_file(related_object, new_path)
                    setattr(instance, related_object_field.name, parent_object)
                    instance.save()
                    text = str(instance)
                    text = (text[:40] + '..') if len(text) > 40 else text
                    print(f'|- Copied child object ({text})')

    # Set the many-to-many relations on the copied parent
    for field_name, relations in relations_to_set.items():
        # Get the field by name and set the relations, creating the new
        # relationships.
        field = getattr(parent_object, field_name)
        field.set(relations)
        text_relations = []
        for relation in relations:
            text_relations.append(str(relation))
        print(f'|- Set {len(relations)} many-to-many relations on {field_name} {text_relations}')

    if isinstance(parent_object, models.File):
        return instance
    else:
        return parent_object


def copy_document_logo(copied_instance, original_instance_pk):
    """
    The function is necessary to copy the document_logo file for a new instance
    (without deleting this file from the original instance).

    Retrieves the document_logo file and its original name.
    Adds a 'copy_' to the name. The new instance will have this file with a new name, for example:
    'orig.png' -> 'copy_orig.png'

    Gets the type (model) of the original object and the original object itself.
    Saves the document_logo file to the copied instance and to the original one.
    Without such saving, the post_save signal on the ShootingPlan model
    will transfer the image from the original instance to the copied one.

    This system is implemented because when creating a new object,
    its document_logo must have a path like:
        '{owner_id}/{model}/{model instance.id}/{filename}'
    The new instance does not have an id yet and therefore all images are placed in the None folder.
        '{owner_id}/{model}/None/{filename}'
    Then the signal transfers them from there to the appropriate folder:
        '10/shootingplan/None/orig.png' -> '10/shootingplan/1/orig.png'

    Thus, if you do not save the document_logo for both copies, the original and the copied one,
    that document_logo will simply be transferred from the original instance to the copied one.
    """
    if copied_instance.document_logo:
        picture_copy = ContentFile(copied_instance.document_logo.read())
        old_picture_name = copied_instance.document_logo.name.split("/")[-1]
        new_picture_name = 'copy_' + old_picture_name

        model = type(copied_instance)
        old_parent_obj = model.objects.get(pk=original_instance_pk)
        copied_instance.document_logo.save(new_picture_name, picture_copy)
        old_parent_obj.document_logo.save(old_picture_name, picture_copy)
