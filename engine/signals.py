from django.db.models.signals import post_save
from django.dispatch import receiver
from engine.assistants import create_assistant
from engine.models import Chatbots


@receiver(post_save, sender=Chatbots)
def chatbot_created(sender, instance, created, **kwargs):
    if created:
        # print(instance.file)
        # create_assistant(instance)
        pass
