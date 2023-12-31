from django.db.models.signals import post_save
from django.dispatch import receiver
from engine.models import Chatbots


@receiver(post_save, sender=Chatbots)
def Chatbot_created(sender, instance, created, **kwargs):
    print(sender, instance, created)
    print(instance.assistant_id)