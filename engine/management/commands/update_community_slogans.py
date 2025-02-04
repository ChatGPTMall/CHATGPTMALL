import json
import os
import openai
from django.core.management.base import BaseCommand
from engine.models import Community


def batch_qs(qs, batch_size=500):
    """
    Returns a (start, end, total, queryset) tuple for each batch in the given
    queryset.

    Usage:
        # Make sure to order your queryset
        article_qs = Article.objects.order_by('id')
        for start, end, total, qs in batch_qs(article_qs):
            print "Now processing %s - %s of %s" % (start + 1, end, total)
            for article in qs:
                print article.body
    """
    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield start, end, total, qs[start:end]


class Command(BaseCommand):
    help = 'Imports data from an Excel file'

    def get_openai_response(self, communities):
        system_prompt = ("You will be provided list of dictionaries contains community name & communtiy_id "
                         "some og the  them might have country names  in name"
                         "mentioned in text also your job is to provided latitude & longitude and slogan & "
                         "description for those communities \n")
        system_prompt += "You should respond in JSON as in this example and all the keys & values should be in string"
        system_prompt += """
                [
                    { 
                        'community_name': 'name of community',
                        "community_id": "8VBCFO",
                        'latitude': 34.5, 
                        'longitude': 76.2, 
                        'slogan': 'Test slogan', 
                        'description': 'test description' 
                    },
                     {
                        'community_name': 'name of community',
                        "community_id": "9VBCFS",
                        'latitude': 34.5, 
                        'longitude': 76.2, 
                        'slogan': 'Test slogan', 
                        'description': 'test description' 
                    },
                    
            """
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": "Here is the list community names {} please provided latitude,"
                                "longitude, slogan & description  based on community name every "
                                "community will have country name or state name mentioned "
                               "please used that".format(communities)
                }
            ],
            response_format={"type": "json_object"}
        )
        result = completion.choices[0].message.content
        return result

    def handle(self, *args, **kwargs):
        all_communities = Community.objects.all()
        for start, end, total, communities in batch_qs(all_communities, batch_size=5):
            result = self.get_openai_response(list(communities.values("name", "community_id")))
            for community in json.loads(result).get("communities"):
                try:
                    comm = communities.get(community_id=community.get("community_id"))
                    comm.slogan = community.get("slogan")
                    comm.description = community.get("description")
                    comm.latitude = community.get("latitude")
                    comm.longitude = community.get("longitude")
                    comm.save()
                except Exception as e:
                    print(str(e))

        self.stdout.write(self.style.SUCCESS('Finished updating data.'))
