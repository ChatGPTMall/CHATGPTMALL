from django.db.models.signals import post_save
from django.dispatch import receiver
from engine.assistants import create_assistant
from engine.models import Chatbots


@receiver(post_save, sender=Chatbots)
def wechat_message_recieved(sender, instance, created, **kwargs):
    if created:
        print(instance)
