import json
import os
from wsgiref.util import FileWrapper

from PIL import Image
from drf_spectacular.utils import extend_schema, OpenApiParameter

from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework import views
from rest_framework import generics
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

import settings
from .tasks import create_video_async
from .models import Bordomatic, BordomaticPrivate, AudioForBordomaticPrivate, ImageForBordomaticPrivate
from .serializers import BordomaticModelSerializer, BordomaticPrivateModelSerializer, \
    BordomaticPrivateModelReadSerializer, \
    BordomaticAudioSerializer, AudioDataSerializer, ImageDataSerializer
    #BordomaticImageSerializer
    #BordomaticModelReadSerializer
from bordomatic.services import get_elem_by_key_value, save_image_for_bordomatic, \
    delete_temp_files, save_audio_for_bordomatic
from utils import get_data_response


# class BordomaticViewSet(ModelViewSet):
#     queryset = Bordomatic.objects.select_related('storyboard__owner',
#                                                  'storyboard__host_project',
#                                                  'storyboard__host_project__owner',
#                                                  'storyboard__owner__subscription'). \
#         prefetch_related('storyboard__frames__owner',
#                          'storyboard__frames__shots')
#     serializer_class = BordomaticModelSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_serializer_class(self):
#         if self.action in ('list', 'retrieve'):
#             return BordomaticModelReadSerializer
#         return self.serializer_class


class BordomaticPrivateViewSet(ModelViewSet):
    queryset = BordomaticPrivate.objects.select_related('storyboard__owner',
                                                        'storyboard__host_project',
                                                        'storyboard__host_project__owner',
                                                        'storyboard__owner__subscription'). \
        prefetch_related('storyboard__frames__owner',
                         'storyboard__frames__shots')
    serializer_class = BordomaticPrivateModelSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return BordomaticPrivateModelReadSerializer
        return self.serializer_class


@extend_schema(parameters=[
    OpenApiParameter(name='width', required=True, type=int),
    OpenApiParameter(name='height', required=True, type=int),

    OpenApiParameter(name='fps', required=True, type=float),
    OpenApiParameter(name='video_name', required=True, type=str),

    OpenApiParameter(name='storyboard_id', required=True, type=int),
    #OpenApiParameter(name='video_type', required=True, type=str),

    OpenApiParameter(name='bordomatic_id', required=True, type=int), ]
)
class CreateMovieAPIView(views.APIView):
    serializer_class = serializers.Serializer
    parser_classes = [MultiPartParser, JSONParser]

    image_extensions = ['jpg', 'jpeg', 'png']
    audio_extensions = ['mp3', 'ogg', 'aac', 'wav']
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        storyboard_id = int(request.query_params.get('storyboard_id'))
        #video_type = request.query_params.get('video_type')
        bordomatic_id = int(request.query_params.get('bordomatic_id'))

        width = int(request.query_params.get('width'))
        height = int(request.query_params.get('height'))
        fps = float(request.query_params.get('fps'))

        if width < 2:
            return Response('Введите ширину больше 1', status=400)

        if height < 2:
            return Response('Введите высоту больше 1', status=400)

        if fps == 0:
            return Response('Введите фпс больше 0', status=400)

        image_folder = settings.IMAGES_FOLDER_PATH

        video_name = f"{request.query_params.get('video_name').split('.')[0]}"
        temp_video_path = f"{settings.VIDEO_FOLDER_PATH}/{video_name}.mp4"

        video_path = f"video/{request.user.email}" \
                     f"/storyboard№{storyboard_id}/{video_name}.mp4"

        #if video_type == 'private':
        model = BordomaticPrivate

        # else:
        #     model = Bordomatic

        if not model.objects.filter(id=bordomatic_id).exists():
            raise NotFound(detail='Бордоматик с таким ID не найден', code=400)

        task = create_video_async.delay(model, bordomatic_id, width, height, #video_type,
                                        fps, video_name, temp_video_path,
                                        video_path, image_folder)

        return Response({"detail": 'задача по созданию видео поставлена в очередь', "task_id": task.id}, status=201)


@extend_schema(parameters=[
    OpenApiParameter(name='path', required=True, type=str)
])
class GetCreatedVideoAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        path = request.query_params.get('path')

        try:
            file = FileWrapper(open(path, 'rb'))
        except Exception as exc:
            return Response(f'{exc}', status=400)

        response = HttpResponse(file, content_type='video/mp4', status=200)
        response['Content-Disposition'] = 'attachment; filename=my_video.mp4'

        return response


# @extend_schema(parameters=[
#     OpenApiParameter(name='video_type', required=True)
# ])
# class GetBordomaticAPIView(generics.ListAPIView):
#     serializer_class = BordomaticModelSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, *args, **kwargs):
#         storyboard_id = kwargs['storyboard_id']
#
#         #if request.query_params.get("video_type") == 'private':
#         model = BordomaticPrivate
#         # else:
#         #     model = Bordomatic
#
#         return get_data_response(self.serializer_class,
#                                  model.objects.filter(storyboard_id=storyboard_id,
#                                                       storyboard__owner=request.user))


@extend_schema(parameters=[
    OpenApiParameter(name='bordomatic_id', required=True, type=int),
    #OpenApiParameter(name='video_type', required=True)
])
class SaveAudioForBordomatic(views.APIView):
    serializer_class = BordomaticAudioSerializer
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [IsAuthenticated]

    audio_extensions = ['mp3', 'ogg', 'aac', 'wav']

    def post(self, request, *args, **kwargs):
        bordomatic_id = int(request.query_params.get('bordomatic_id'))

        #if request.query_params.get('video_type') == 'private':
        model = BordomaticPrivate
        # else:
        #     model = Bordomatic

        try:
            bordomatic = model.objects.get(id=bordomatic_id)
        except Exception as exc:
            return Response(f'{exc}', status=400)

        audio_folder = settings.AUDIO_FOLDER_PATH
        audios = {}

        all_audio_data = json.loads(f"[{request.data.get('audioData')}]")
        all_audio_data.sort(key=lambda i: i['data']['begin'])

        for name_and_files in request.FILES.lists():
            for file in name_and_files[1]:
                if file.name.split('.')[-1] in self.audio_extensions:
                    audio_data = get_elem_by_key_value('name', all_audio_data,
                                                       file.name)
                    if audio_data is None:
                        return Response("Введите правильные данные об аудио", status=400)

                    try:
                        with open(f'{audio_folder}/{file.name}', 'wb') as fh:
                            fh.write(file.read())

                    except Exception:
                        os.mkdir(audio_folder)
                        with open(f'{audio_folder}/{file.name}', 'wb') as fh:
                            fh.write(file.read())

                    audios[f'{audio_folder}/{file.name}'] = audio_data

        audios_ids = []
        for temp_audio_path, audio_data in audios.items():
            audio_name = temp_audio_path.split('/')[-1]
            audio_path = f"audio/{request.user.email}" \
                         f"/storyboard№{bordomatic.storyboard_id}/{audio_name}"

            try:
                save_audio_for_bordomatic(audio_data['data'], bordomatic_id,
                                          temp_audio_path, audio_path, audio_name, audios_ids)
            except Exception as exc:
                return Response(f'{exc}', status=400)

        delete_temp_files([audio_folder])

        return Response({'audios_ids': audios_ids}, status=201)

class UpdateAudioForBordomatic(views.APIView):
    serializer_class = AudioDataSerializer
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [IsAuthenticated]
    def put(self, request, *args, **kwargs):
        pk = kwargs.get("id", None)
        if not pk:
            return Response({"error": "Method PUT not allowed. ID is not mention"})

        try:
            instance = AudioForBordomaticPrivate.objects.get(pk=pk)
        except:
            return Response({"error": "Object does not exists"})

        serializer = AudioDataSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"post": serializer.data})


# @extend_schema(parameters=[
#     OpenApiParameter(name='bordomatic_id', required=True, type=int),
#     #OpenApiParameter(name='video_type', required=True)
# ])
# class SaveImageForBordomatic(views.APIView):
#     serializer_class = BordomaticImageSerializer
#     parser_classes = [MultiPartParser, JSONParser]
#     permission_classes = [IsAuthenticated]
#
#     image_extensions = ['jpg', 'jpeg', 'png']
#
#     def post(self, request, *args, **kwargs):
#         bordomatic_id = int(request.query_params.get('bordomatic_id'))
#
#         #if request.query_params.get('video_type') == 'private':
#         model = BordomaticPrivate
#         # else:
#         #     model = Bordomatic
#
#         try:
#             bordomatic = model.objects.get(id=bordomatic_id)
#         except Exception as exc:
#             return Response(f'{exc}', status=400)
#
#         image_folder = settings.IMAGES_FOLDER_PATH
#         images = {}
#
#         try:
#             all_image_data = json.loads(f"[{request.data.get('imageData')}]")
#         except Exception as exc:
#             return Response(f"{exc}", status=400)
#
#         for name_and_files in request.FILES.lists():
#             for file in name_and_files[1]:
#                 if file.name.split('.')[1] in self.image_extensions:
#                     img_name, img_format = file.name.split('.')
#
#                     created_image = Image.open(file)
#                     image_data = get_elem_by_key_value('name', all_image_data, file.name)
#                     if image_data is None:
#                         return Response("Введите правильные данные о картинке", status=400)
#
#                     if img_format == 'jpg':
#                         created_image.save(f'{image_folder}/{file}')
#
#                         images[f'{image_folder}/{file}'] = image_data
#                     else:
#                         rgb_im = created_image.convert('RGB')
#                         rgb_im.save(f'{image_folder}/{img_name}.jpg')
#
#                         images[f'{image_folder}/{img_name}.jpg'] = image_data
#
#         images_ids = []
#         for temp_image_path, image_data in images.items():
#             image_name = temp_image_path.split('/')[-1]
#             image_path = f"images/{request.user.email}" \
#                          f"/storyboard№{bordomatic.storyboard_id}/{image_name}"
#
#             try:
#                 save_image_for_bordomatic(image_data['data'], bordomatic_id,
#                                           temp_image_path, image_path, images_ids)
#             except Exception as exc:
#                 return Response(f'{exc}', status=400)
#
#         delete_temp_files([image_folder])
#
#         return Response({'images_ids': images_ids}, status=201)

class UpdateImageForBordomatic(views.APIView):
    serializer_class = ImageDataSerializer
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get("id", None)
        if not pk:
            return Response({"error": "Method PUT not allowed. ID is not mention"})

        try:
            instance = ImageForBordomaticPrivate.objects.get(pk=pk)
        except:
            return Response({"error": "Object does not exists"})

        serializer = ImageDataSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"post": serializer.data})
@extend_schema(parameters=[
    OpenApiParameter(name='bordomatic_id', type=int),
    OpenApiParameter(name='audio_id', type=int),
])
class DeleteAudioFromFileAPIView(generics.DestroyAPIView):

    def delete(self, request, *args, **kwargs):
        if request.query_params.get('bordomatic_id'):
            data = {'bordomatic_id': int(request.query_params.get('bordomatic_id'))}

        else:
            data = {'id': int(request.query_params.get('audio_id'))}

        AudioForBordomaticPrivate.objects.filter(**data).delete()
        return Response(status=204)
