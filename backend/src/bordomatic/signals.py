import asyncio

import channels.layers
from django.dispatch import receiver
from celery.result import AsyncResult

from django.dispatch import Signal

user_signal = Signal(providing_args=["instance", "task"])


@receiver(user_signal,
          dispatch_uid="status_task_send")  # Функция update_job_status_listeners будет вызвана только при сохранении экземпляра BordomaticPrivate
def status_task_send(sender, instance, **kwargs):
    '''
    Sends task status to the browser when a video was created
    '''
    import time
    time.sleep(5)  # ждать чтобы задача по созданию видео завершился
    print('---------------------сработал сигнал завершения задачи создания видео------------------------')
    bordomvatic_id = kwargs['bordomvatic_id']
    task_result = AsyncResult(kwargs['task_id'])
    result = {
        "task_id": kwargs['task_id'],
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    message = {
        'bordomvatic_id': bordomvatic_id,
        'task_status': result,
    }
    channel_layer = channels.layers.get_channel_layer()

    # async_to_sync(channel_layer.group_send)(
    #     str(bordomvatic_id),
    #     {
    #         'type': 'send_message',
    #         'text': message
    #     }
    # )

    loop = asyncio.get_event_loop()
    coroutine = channel_layer.group_send(
        str(bordomvatic_id),
        {
            'type': 'send_message',
            'text': message
        })
    loop.run_until_complete(coroutine)
