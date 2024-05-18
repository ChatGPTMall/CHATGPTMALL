import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from engine.models import Chatbots, WechatMessages, KeyManagement
from engine.thread_functions import run_in_thread
from engine.utils import send_wechat_message_reply, get_as_base64_url, generate_item_content, upload_new_wechat_listing


@receiver(post_save, sender=WechatMessages)
def wechat_message_recieved(sender, instance, created, **kwargs):
    # if created:
    if instance.pic_url != "":
        url = instance.pic_url
        run_in_thread(send_wechat_message_reply, (instance,))
        run_in_thread(upload_new_wechat_listing, (url,))
