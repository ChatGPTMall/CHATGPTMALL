import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from engine.models import Chatbots, WechatMessages, KeyManagement, VoiceCommandsHistory, VoiceCommands, Items
from engine.thread_functions import run_in_thread
from engine.utils import upload_new_wechat_listing, \
    create_room_and_china_user, send_wechat_room_reply, send_login_otp_reply


@receiver(post_save, sender=WechatMessages)
def wechat_message_recieved(sender, instance, created, **kwargs):
    create_room_and_china_user(instance.wechat_id, instance)
    if instance.msg_type == "text" and instance.text.upper() == "ROOM LOGIN":
        send_login_otp_reply(instance)
    else:
        url = instance.pic_url
        run_in_thread(upload_new_wechat_listing, (url, instance))


@receiver(post_save, sender=VoiceCommands)
def voice_command_recieved(sender, instance, created, **kwargs):
    data = "ON" if instance.switch else "OFF"
    VoiceCommandsHistory.objects.create(
        voice=instance, data=data
    )


@receiver(post_save, sender=Items)
def items_created(sender, instance, created, **kwargs):
    try:
        # if created:
        data = {
             'label': instance.title,
             'ref': str(instance.item_id),
             'price': instance.price,
             'description': instance.description,
             'stock': instance.stock,
             'image_url': instance.qr_code.url
        }

        headers = {
            'Accept': 'application/json',
            'DOLAPIKEY': '79RdTE6zwkW8PxRD15099A4ecKqrCaqE'
        }

        url = 'http://plastireai.com/api/index.php/products'
        response = requests.post(url, json=data, headers=headers)
        print(response.json())
        # dolibarr.Dolibarr.call_create_api()

    except Exception as e:
        print(e)





