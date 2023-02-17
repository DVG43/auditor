from django.db.models import Q
from rest_framework import serializers, status

from .models import Bordomatic, BordomaticPrivate, ImageForBordomatic, ImageForBordomaticPrivate, AudioForBordomatic, \
    AudioForBordomaticPrivate, choises_effectvalue, choises_effectname
from common.models import UserColumn, UserCell
from storyboards.models import Shot, Frame
from common import utils

from rest_framework.response import Response
from .services import save_image_for_bordomatic, delete_temp_files
import settings
from PIL import Image
import os

class ImageDataSerializer(serializers.Serializer):
    #image_type = serializers.CharField()

    frame_time = serializers.IntegerField(default=1000)
    effectName = serializers.ChoiceField(choices=choises_effectname, required=False, allow_null=True)
    effectValue = serializers.ChoiceField(choices=choises_effectvalue, required=False, allow_null=True)
    subtitle = serializers.CharField(required=False)
    subtitleView = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        instance.frame_time = validated_data.get("frame_time", instance.frame_time)
        instance.effectName = validated_data.get("effectName", instance.effectName)
        instance.effectValue = validated_data.get("effectValue", instance.effectValue)
        instance.subtitle = validated_data.get("subtitle", instance.subtitle)
        instance.subtitleView = validated_data.get("subtitleView", instance.subtitleView)
        instance.save()
        return instance


class ImageSerializer(serializers.Serializer):
    name = serializers.CharField()
    data = ImageDataSerializer()


class AudioDataSerializer(serializers.Serializer):
    #audio_type = serializers.CharField()

    begin = serializers.CharField()
    end = serializers.CharField()
    volume = serializers.FloatField()

    def update(self, instance, validated_data):
        instance.begin = validated_data.get("begin", instance.begin)
        instance.end = validated_data.get("end", instance.end)
        instance.volume = validated_data.get("volume", instance.volume)
        instance.save()
        return instance


class AudioSerializer(serializers.Serializer):
    name = serializers.CharField()
    data = AudioDataSerializer()


class BordomaticSerializer(serializers.Serializer):
    image_data = ImageSerializer(many=True)
    images = serializers.ListField(child=serializers.ImageField())

    audio_data = AudioSerializer(many=True, required=False)
    audios = serializers.ListField(required=False, child=serializers.FileField())


class BordomaticAudioSerializer(serializers.Serializer):
    audio_data = AudioSerializer(many=True)
    audios = serializers.ListField(child=serializers.FileField())


class BordomaticImageSerializer(serializers.Serializer):
    image_data = ImageSerializer(many=True)
    images = serializers.ListField(child=serializers.ImageField())


class BordomaticImageModelSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='image.url')

    class Meta:
        model = ImageForBordomatic
        fields = '__all__'


class BordomaticImagePrivateModelSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='image.url')

    class Meta:
        model = ImageForBordomaticPrivate
        fields = '__all__'

#
# class BordomaticAudioModelSerializer(serializers.ModelSerializer):
#     audio = serializers.CharField(source='audio.url')
#
#     class Meta:
#         model = AudioForBordomatic
#         fields = '__all__'


class BordomaticAudioPrivateModelSerializer(serializers.ModelSerializer):
    audio = serializers.CharField(source='audio.url')

    class Meta:
        model = AudioForBordomaticPrivate
        fields = '__all__'


class BordomaticModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bordomatic
        fields = '__all__'


# class BordomaticModelReadSerializer(BordomaticModelSerializer):
#     audios = BordomaticAudioModelSerializer(many=True)
#     images = BordomaticImageModelSerializer(many=True)
#
#     class Meta:
#         model = Bordomatic
#         fields = [
#             'id',
#             'storyboard',
#             'video',
#             'uploaded_at',
#             'fps',
#             'width',
#             'height',
#             'audios',
#             'images'
#         ]
#
#     def to_representation(self, instance):
#         if instance.video:
#             instance.video = instance.video.url
#
#         return super().to_representation(instance)


class BordomaticPrivateModelSerializer(serializers.ModelSerializer):
    images = BordomaticImageModelSerializer(many=True, required=False)

    class Meta:
        model = BordomaticPrivate
        fields = [
            'id',
            'storyboard',
            'video',
            'uploaded_at',
            'fps',
            'width',
            'height',
            'images'
        ]

    def create(self, validated_data):
        storyboard = validated_data.get('storyboard')
        storyboard_id = storyboard.id
        user = storyboard.owner
        frames = Frame.objects.all().filter(host_storyboard__id=storyboard_id)
        column = UserColumn.objects.filter(
            Q(of_storyboard__id=storyboard_id) & Q(column_name="Описание")).first()
        images_ids = []

        # проверяем хватает ли места для изображении бордоматика на диске у пользователя
        size_of_files = 0
        if frames:
            for frame in frames:
                shot = Shot.objects.all().filter(host_frame__id=frame.id).first()
                if shot:
                    size_of_files += shot.file.size
        disk_space = user.disk_space if user.disk_space else 0
        if size_of_files + disk_space > settings.DISK_SIZE:
            return Response({'file': 'Not enough space on disk for file'},
                            status=status.HTTP_400_BAD_REQUEST)
        if frames:
            media_folder = settings.MEDIA_ROOT
            if not os.path.isdir(settings.IMAGES_FOLDER_PATH + f"/{user.email}"):
                os.mkdir(settings.IMAGES_FOLDER_PATH + f"/{user.email}")
            image_folder = settings.IMAGES_FOLDER_PATH + f"/{user.email}"
            ModelClass = self.Meta.model
            bordomatic = ModelClass._default_manager.create(**validated_data)  # saving post object
            for frame in frames:
                shot = Shot.objects.all().filter(host_frame__id=frame.id).first()
                if shot:
                    image_name = shot.file.name.split('/')[-1]
                    img_name, img_format = image_name.split('.')
                    image_path = f"images/{user.email}" \
                                 f"/storyboard№{storyboard_id}/{image_name}"
                    old_image_path = media_folder + '/' + shot.file.name
                    created_image = Image.open(old_image_path)

                    if img_format == 'jpg':
                        created_image.save(f'{image_folder}/{image_name}')
                        temp_image_path = f'{image_folder}/{image_name}'
                    else:
                        rgb_im = created_image.convert('RGB')
                        rgb_im.save(f'{image_folder}/{img_name}.jpg')
                        temp_image_path = f'{image_folder}/{img_name}.jpg'

                    try:
                        image_data = {}
                        #image_data['imageType'] = 'private'
                        image_data['frameTime'] = 1000
                        image_data['effectValue'] = None
                        image_data['effectName'] = None
                        image_data['subtitle'] = ""
                        if column:
                            cell = UserCell.objects.filter(
                                Q(of_frame__id=frame.id) & Q(host_usercolumn__id=column.id)).first()
                            if cell:
                                image_data['subtitle'] = cell.cell_content
                        image_data['subtitleView'] = True
                        save_image_for_bordomatic(image_data, bordomatic.id,
                                                  temp_image_path, image_path, images_ids)
                    except Exception as exc:
                        bordomatic.delete()
                        print('save_image_for_bordomatic error')
                        return Response(f'{exc}', status=400)
            delete_temp_files([image_folder])
            try:
                os.rmdir(image_folder)
            except:
                print("не удалось удалить временную папку для картинок бордоматика")

            if hasattr(bordomatic, "perms"):
                storyboard.owner.grant_object_perm(bordomatic, 'own')

            # обновляем место на диске после сохранения нового файла
            if size_of_files:
                utils.change_disk_space(storyboard.owner, disk_space+size_of_files)

            return bordomatic
        else:
            return Response('frames not found', status=400)

class BordomaticPrivateModelReadSerializer(BordomaticModelSerializer):
    audios = BordomaticAudioPrivateModelSerializer(many=True)
    images = BordomaticImagePrivateModelSerializer(many=True)

    class Meta:
        model = BordomaticPrivate
        fields = [
            'id',
            'storyboard',
            'video',
            'uploaded_at',
            'fps',
            'width',
            'height',
            'audios',
            'images'
        ]

    def to_representation(self, instance):
        if instance.video:
            instance.video = instance.video.url

        return super().to_representation(instance)
