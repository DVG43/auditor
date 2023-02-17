import os
import cv2 as cv2

from django.core.files.base import ContentFile

import settings
from .models import BordomaticPrivate, ImageForBordomaticPrivate, ImageForBordomatic, \
    AudioForBordomatic, AudioForBordomaticPrivate

coefficient = {
    '10%': 1.1, '20%': 1.2, '30%': 1.30, '40%': 1.4, '50%': 1.5, '60%': 1.6, '70%': 1.7, '80%': 1.8,
    '90%': 1.9, '100%': 2.0,
    '1x': 1.20, '2x': 1.25, '3x': 1.30, '4x': 1.35, '5x': 1.40, '6x': 1.45, '7x': 1.6, '8x': 1.65,
    '9x': 1.7, '10x': 1.75, '11x': 1.8, '12x': 1.85, '13x': 1.90, '14x': 1.95, '15x': 2.0, '16x': 2.5
}

def get_elem_by_key_value(key: str, list_data: list, expected_value: str = None) -> dict:
    for dict_elem in list_data:
        dict_value = dict_elem.get(key)

        if expected_value is not None:
            if dict_value == expected_value:
                return dict_elem

        else:
            return dict_value
        # for elem_key in dict_elem.keys():
        #     if elem_key == key and dict_elem[key] == value:
        #         return dict_elem


def save_bordomatic(video_data, bordomatic_id, temp_video_path, new_path):
    # if video_data["video_type"] == 'private':
    model = BordomaticPrivate
    #
    # else:
    #     model = Bordomatic
    #
    # video_data.pop('video_type')

    bordomatic = model.objects.get(id=bordomatic_id)
    model.objects.filter(id=bordomatic_id).update(**video_data)

    with open(temp_video_path, "rb") as fh:
        with ContentFile(fh.read()) as file_content:
            bordomatic.video.save(f'{new_path}', file_content, save=True)

    bordomatic.save()

    if settings.USE_S3:
        bordomatic_url = bordomatic.video.url
    else:
        bordomatic_url = temp_video_path

    return {"bordomatic_url": bordomatic_url, "bordomatic_id": bordomatic.id}


def save_image_for_bordomatic(image_data, bordomatic_id, temp_image_path, new_path, images_ids):
    #if image_data['imageType'] == 'private':
    model = ImageForBordomaticPrivate
    # else:
    #     model = ImageForBordomatic

    image_for_bordomatic = model(               #сохранение данных кадра
        bordomatic_id=bordomatic_id,
        frame_time=image_data['frameTime'],
        effectValue=image_data['effectValue'],
        effectName=image_data['effectName'],
        subtitle=image_data['subtitle'],
        subtitleView=image_data['subtitleView']
    )

    with open(temp_image_path, "rb") as fh:
        with ContentFile(fh.read()) as file_content:
            image_for_bordomatic.image.save(f'{new_path}', file_content, save=True)

    image_for_bordomatic.save()

    images_ids.append(image_for_bordomatic.id)


def save_audio_for_bordomatic(audio_data, bordomatic_id, temp_audio_path, new_path,
                              audio_name, audios_ids):
    #if audio_data['audioType'] == 'private':
    model = AudioForBordomaticPrivate
    # else:
    #     model = AudioForBordomatic

    audio_for_bordomatic = model(bordomatic_id=bordomatic_id,
                                 begin=audio_data['begin'],
                                 end=audio_data['end'],
                                 volume=audio_data['volume'],
                                 name_audio=audio_name)

    with open(temp_audio_path, "rb") as fh:
        with ContentFile(fh.read()) as file_content:
            audio_for_bordomatic.audio.save(f'{new_path}', file_content, save=True)

    audio_for_bordomatic.save()

    audios_ids.append(audio_for_bordomatic.id)


def create_directories_for_bordomatic(request, storyboard_id):
    directories = (
        f"{settings.VIDEO_FOLDER_PATH}/{request.user.email}/",
        f"{settings.VIDEO_FOLDER_PATH}/{request.user.email}/storyboard№{storyboard_id}",

        f"{settings.IMAGES_FOLDER_PATH}/{request.user.email}",
        f"{settings.IMAGES_FOLDER_PATH}/{request.user.email}/storyboard№{storyboard_id}"
    )

    for directory in directories:
        if not os.path.exists(directory):
            os.mkdir(directory)


def delete_temp_files(directories: list):
    for directory in directories:
        for file in os.listdir(directory):
            file_path = '/'.join([directory, file])

            is_file = os.path.isfile(file_path)
            if is_file and not file_path.endswith('.dockerenv'):
                os.remove(file_path)



def CreateVideoFunc(out, frame, dim, frame_time, fps, zoom, effectName):
    def zoom_frames(src, resolutoin, zoom):  # получить картинку для отдаленного разрешения
        resolutoin_max = (int(resolutoin[0] * zoom), int(resolutoin[1] * zoom))  # нужно ввести данные для отдаленного разрешения
        width = resolutoin_max[0]
        if src.shape[1] < resolutoin_max[0]:
            width = resolutoin_max[0]
        height = int(src.shape[0] * resolutoin_max[0] / src.shape[1])
        dsize = (width, height)
        output = cv2.resize(src, dsize)

        if output.shape[0] < resolutoin_max[1]:
            height = resolutoin_max[1]
            width = int(output.shape[1] * resolutoin_max[1] / output.shape[0])
            dsize = (width, height)
            output = cv2.resize(src, dsize)
        return output

    def zoom_in_zoom_out(frame, effectName, resolutoin, frame_time, fps, i, zoom, dim):
        centre_width = frame.shape[1] / 2
        centre_height = frame.shape[0] / 2
        widthdif = centre_width - (resolutoin[0] / 2)
        heightdif = centre_height - (resolutoin[1] / 2)
        k = i / frame_time * 1000 / fps
        if frame.shape[1] / resolutoin[0] > frame.shape[0] / resolutoin[1]:
            a = k * heightdif * resolutoin[0] / resolutoin[1]
            b = k * heightdif
        else:
            a = k * widthdif
            b = k * widthdif * resolutoin[1] / resolutoin[0]
        if effectName == "zoomIn":
            c = 1
        elif effectName == "zoomOut":
            c = -1
            zoom = 1
        x1 = int(centre_width - (zoom * resolutoin[0] / 2) + a * c)
        x2 = int(centre_width + (zoom * resolutoin[0] / 2) - a * c)
        y1 = int(centre_height - (zoom * resolutoin[1] / 2) + b * c)
        y2 = int(centre_height + (zoom * resolutoin[1] / 2) - b * c)
        # print("(x1", x1, "y1", y1, ")(x2", x2, "y2", y2, "                    k", k)
        return cv2.resize(frame[y1:y2, x1:x2], dim, interpolation=cv2.INTER_LINEAR)

    def move_zoom_frame(frame, effectName, resolutoin, frame_time, fps, i, dim):
        k = i / frame_time * 1000 / fps
        widthdif = frame.shape[1] - resolutoin[0]
        heightdif = frame.shape[0] - resolutoin[1]
        if effectName == "moveTop" or effectName == "moveBottom":
            a = k * heightdif
            centre_width = frame.shape[1] / 2
            b = resolutoin[0] / 2
            x1 = int(centre_width - b)
            x2 = int(centre_width + b)
            if effectName == "moveTop":
                y1 = int(heightdif - a)
                y2 = int(frame.shape[0] - a)
            else:
                y1 = int(a)
                y2 = int(frame.shape[0] - heightdif + a)
        if effectName == "moveLeft" or effectName == "moveRight":
            a = k * widthdif
            centre_height = frame.shape[0] / 2
            b = resolutoin[1] / 2
            y1 = int(centre_height - b)
            y2 = int(centre_height + b)
            if effectName == "moveLeft":
                x1 = int(widthdif - a)
                x2 = int(frame.shape[1] - a)
            else:
                x1 = int(a)
                x2 = int(frame.shape[1] - widthdif + a)
        # print("(x1", x1, "y1", y1, ")(x2", x2, "y2", y2, "                    k", k)
        return cv2.resize(frame[y1:y2, x1:x2], dim, interpolation=cv2.INTER_LINEAR)

    def zoom_without_effects(frame, resolutoin, zoom, dim):
        centre_width = frame.shape[1] / 2
        centre_height = frame.shape[0] / 2
        widthdif = centre_width - (resolutoin[0] / 2)
        heightdif = centre_height - (resolutoin[1] / 2)
        if frame.shape[1] / resolutoin[0] > frame.shape[0] / resolutoin[1]:
            a = heightdif * resolutoin[0] / resolutoin[1]
            b = heightdif
        else:
            a = widthdif
            b = widthdif * resolutoin[1] / resolutoin[0]
        c = 1
        x1 = int(centre_width - (zoom * resolutoin[0] / 2) + a * c)
        x2 = int(centre_width + (zoom * resolutoin[0] / 2) - a * c)
        y1 = int(centre_height - (zoom * resolutoin[1] / 2) + b * c)
        y2 = int(centre_height + (zoom * resolutoin[1] / 2) - b * c)
        # print("(x1", x1, "y1", y1, ")(x2", x2, "y2", y2, "                    k", k)
        return cv2.resize(frame[y1:y2, x1:x2], dim, interpolation=cv2.INTER_LINEAR)

    k = 4 # most be more then 2
    resolutoin = (dim[0]*k, dim[1]*k)
    frame = zoom_frames(frame, resolutoin, zoom)
    #print(type(fps), type(frame_time))
    quantity_frame = int(fps * frame_time // 1000)
    if effectName == "zoomIn" or effectName == "zoomOut":
        frame = cv2.medianBlur(frame, k+1)
        for i in range(quantity_frame):
            resized = zoom_in_zoom_out(frame, effectName, resolutoin, frame_time, fps, i,
                                       zoom, dim)  # обрезка кадра для i-го изображения
            out.write(resized)
    elif effectName == "moveTop" or effectName == "moveLeft" or effectName == "moveRight":
        for i in range(quantity_frame):
            resized = move_zoom_frame(frame, effectName, resolutoin, frame_time, fps,
                                      i, dim)  # обрезка кадра для i-го изображения
            out.write(resized)
    else:
        for i in range(quantity_frame):
            resized = zoom_without_effects(frame, resolutoin, zoom, dim)  # обрезка кадра для i-го изображения
            out.write(resized)

def get_coefficient_for_zoom(effectValue):
    return coefficient.get(effectValue, 1)
