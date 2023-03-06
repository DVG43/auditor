import os, random, string, urllib3, shutil
from hashlib import md5
import openai
from settings import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY
PATH_IMAGES = "/app/backend/src/share/auditor-v2_media/images/"


def organize_data_row_sort_arrays(instance):
    # чистка и сортировка массивов сортировки
    instance_data_row_attribute = None
    for attr in dir(instance):
        if attr.endswith('element') or attr == 'locations':
            instance_data_row_attribute = getattr(instance, attr)
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

    # отключаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = False

    instance.save()

    # включаем изменение last_modified_date
    for field in instance._meta.local_fields:
        if field.name == "last_modified_date":
            field.auto_now = True

    return instance


def text_generator(prompt, model, max_tokens):
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0.7,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response


def gen_unique_filename(ext):
    s = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(10))
    return md5(s.encode('utf8')).hexdigest() + ext

size_dict = {0: '256x256', 1: '512x512', 2: '1024x1024'}


def image_generator(prompt, n=1, size=2):
    """
    Создает изображения по описанию prompt. Изображения сохраняютя в PATH_IMAGES.
    param:
      prompt (str): описание желаемого изображения, максимальная длина 1000 символов
      n (int): количество генерируемых изображений на основе описания prompt, от 1 до 10
      size (int): размер генерируемых изображений: 0, 1 или 2
    """
    save_dir = os.getcwd()
    images = list()

    try:
        os.chdir(PATH_IMAGES)
        response = openai.Image.create(prompt=prompt, n=n, size=size_dict[size])

        http = urllib3.PoolManager()
        for i in range(n):
            image_url = response['data'][i]['url']
            filename = gen_unique_filename('.png')
            images.append(filename)
            with http.request('GET', image_url, preload_content=False) as resp, open(filename, 'wb') as out_file:
                shutil.copyfileobj(resp, out_file)

    except Exception as err:
        raise Exception(err)
    finally:
        os.chdir(save_dir)

    return images


def image_edit(baseimage, prompt, pathname, filename, ext='png', mask=None, n=1, size=2):
    """
    Создает отредактированное или расширенное изображение на основе исходного изображения baseimage и подсказки prompt.
    param:
      baseimage (str): изображение для редактирования, должно быть действительным файлом PNG, размером менее 4 МБ и квадратной формы, если маска не указана, изображение должно иметь прозрачность, которая будет использоваться в качестве маски
      prompt (str): описание желаемого изображения, максимальная длина 1000 символов
      pathname (str): путь куда сохранять файлы изображнений
      filename (str): имя файла без расширения
      ext (str): тип файла bmp|png|jpg|etc
      mask (str): имя файла дополнительного изображения, чьи полностью прозрачные области (например, где альфа равна нулю) указывают, где изображение должно быть отредактировано, должно быть действительным файлом PNG, менее 4 МБ и иметь те же размеры, что и изображение baseimage
      n (int): количество генерируемых изображений, от 1 до 10
      size (int): размер генерируемых изображений: 0, 1 или 2
    """
    save_dir = os.getcwd()
    try:
        os.chdir(pathname)
        response = openai.Image.create_edit(image=open(baseimage, "rb"), mask=mask and open(mask, "rb"), prompt=prompt,
                                            n=n, size=size_dict[size])

        http = urllib3.PoolManager()
        for i in range(n):
            image_url = response['data'][i]['url']
            with http.request('GET', image_url, preload_content=False) as resp, open(f"{filename}{i}.{ext}",
                                                                                     'wb') as out_file:
                shutil.copyfileobj(resp, out_file)
    except Exception as e:
        raise
        #logging.exception(e)
    finally:
        os.chdir(save_dir)


def variation(baseimage, pathname, filename, ext='png', n=1, size=2):
    """
    Создает вариант(ы) данного изображения.
    param:
      baseimage (str): изображение для использования в качестве основы, должно быть действительным файлом PNG, размером менее 4 МБ и квадратной формы
      pathname (str): путь куда сохранять файлы изображнений
      filename (str): имя файла без расширения
      ext (str): тип файла bmp|png|jpg|etc
      n (int): количество генерируемых изображений, от 1 до 10
      size (int): размер генерируемых изображений: 0, 1 или 2
    """
    save_dir = os.getcwd()
    try:
        os.chdir(pathname)
        response = openai.Image.create_variation(image=open(baseimage, "rb"), n=n, size=size_dict[size])
        http = urllib3.PoolManager()
        for i in range(n):
            image_url = response['data'][i]['url']
            with http.request('GET', image_url, preload_content=False) as resp, open(f"{filename}{i}.{ext}", 'wb') as out_file:
                shutil.copyfileobj(resp, out_file)
    except Exception as e:
        raise
        #logging.exception(e)
    finally:
        os.chdir(save_dir)
