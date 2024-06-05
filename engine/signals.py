import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from engine.models import Chatbots, WechatMessages, KeyManagement
from engine.thread_functions import run_in_thread
from engine.utils import upload_new_wechat_listing, \
    create_room_and_china_user, send_wechat_room_reply


@receiver(post_save, sender=WechatMessages)
def wechat_message_recieved(sender, instance, created, **kwargs):
    create_room_and_china_user(instance.wechat_id)
    run_in_thread(send_wechat_room_reply, (instance, ))
    # if created and instance.pic_url:
    url = instance.pic_url
    run_in_thread(upload_new_wechat_listing, (url, instance))

