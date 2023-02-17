import os
from django_celery import app

import celery
# for email
import cv2
import shutil
import requests
import moviepy.editor as mpe
import settings
from . import signals
from bordomatic.services import save_bordomatic, \
    delete_temp_files, CreateVideoFunc, get_coefficient_for_zoom
from rest_framework.exceptions import NotFound
from .models import Bordomatic, BordomaticPrivate


@app.task
def task_async_for_sending_message(bordomatic_id, task_id):
    signals.user_signal.send(sender=None, instance=None, bordomvatic_id=bordomatic_id,
                             task_id=task_id)


@app.task
def create_video_async(model, bordomatic_id, width, height, fps, video_name, temp_video_path, video_path, #video_type,
                       image_folder):
    try:
        dim = (width, height)

        bordomatic = model.objects.get(id=bordomatic_id)

        video = cv2.VideoWriter(temp_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, dim)

        for image_data in bordomatic.images.all():
            response = requests.get(image_data.image.url, stream=True)

            temp_file_path = f'{image_folder}/test.jpg'

            with open(temp_file_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)

            frame = cv2.imread(temp_file_path)

            zoom = get_coefficient_for_zoom(image_data.effectValue)
            CreateVideoFunc(video, frame, dim, image_data.frame_time, fps, zoom, image_data.effectName)  # запись кадров

            os.remove(temp_file_path)

        video.release()
        cv2.destroyAllWindows()
        # print(temp_video_path)

        mpe_video = mpe.VideoFileClip(temp_video_path)

        for audio_data in bordomatic.audios.all():
            audio_clip = mpe.AudioFileClip(f'{audio_data.audio.url}')

            audio_clip = audio_clip.volumex(audio_data.volume)
            audio_clip = audio_clip.set_end(audio_data.end)
            audio_clip = audio_clip.set_start(audio_data.begin, change_end=False)

            if mpe_video.audio:
                clips = [mpe_video.audio, audio_clip]
            else:
                clips = [audio_clip]

            final_audio = mpe.CompositeAudioClip(clips)
            mpe_video = mpe_video.set_audio(final_audio)

        temp_video_path_with_audio = f"{settings.VIDEO_FOLDER_PATH}/{video_name}_with_audio.mp4"
        mpe_video.write_videofile(temp_video_path_with_audio)
        temp_video_path = temp_video_path_with_audio
        video_data = {'width': width, 'height': height, 'fps': fps} #'video_type': video_type,
        save_bordomatic(video_data, bordomatic_id, temp_video_path, video_path)

        delete_temp_files([settings.VIDEO_FOLDER_PATH])
    finally:
        task_async_for_sending_message.delay(bordomatic_id=bordomatic.id, task_id=celery.current_task.request.id)

    print('------------------------задача выполнена-----------------------------------')
