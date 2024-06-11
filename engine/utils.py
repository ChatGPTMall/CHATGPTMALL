import base64
import uuid

import requests
from django.core.files.base import ContentFile

from engine.models import InternalExceptions, KeyManagement, Items, ListingType, Category, Community, CommunityPosts, \
    WechatOfficialAccount, RoomLoginRequests
from engine.thread_functions import run_in_thread
from users.models import ChinaUsers, User
from skybrain.models import Room, RoomItems


def send_wechat_message_reply(instance, item):
    from_user_name = instance.wechat_id
    url = instance.pic_url
    title = generate_item_content(url, "Tell me about this image")
    appid = ""
    appsecret = ""
    try:
        reply_message = {
            "touser": from_user_name,  # Use the 'FromUserName' you received in the incoming message
            "msgtype": "text",
            "text": {
                "content": f"{title}\n\n{item.image.url if item.image else item.qr_code.url}"  # Include the URL in the message content
            }
        }
        official_account = WechatOfficialAccount.objects.get(official_id=instance.official_account_id)
        if hasattr(official_account, "official_account"):
            appid = official_account.official_account.app_id
            appsecret = official_account.official_account.secret_id
    except Exception as e:
        reply_message = {
            "touser": from_user_name,  # Use the 'FromUserName' you received in the incoming message
            "msgtype": "text",
            "text": {
                "content": "Account Not Registered With Us!!!"
            }
        }
    # Send the message using the WeChat API
    try:

        response1 = requests.post(
            'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
                appid, appsecret))
        try:
            token = response1.json()["access_token"]
            response = requests.post('https://api.weixin.qq.com/cgi-bin/message/custom/send',
                                     params={'access_token': token},
                                     json=reply_message)
            InternalExceptions.objects.create(text=response.json())
        except KeyError:
            pass
    except Exception as e:
        InternalExceptions.objects.create(text=str(e))


def get_as_base64_url(url):
    return base64.b64encode(requests.get(url).content)


def generate_item_content(url, input_):
    openai_key = KeyManagement.objects.filter(platform="OPENAI").last()
    if openai_key:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_key.key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": input_
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"]


def upload_new_wechat_listing(url, instance):
    try:
        title_prompt = "generate title for this"
        description_prompt = "generate description for this"
        category_prompt = "generate one word category for this"
        category_title = generate_item_content(url, category_prompt)
        title = generate_item_content(url, title_prompt)
        description = generate_item_content(url, description_prompt)
        category, _ = Category.objects.get_or_create(title=category_title)
        item = Items(category=category, listing=ListingType.WECHAT, price=10, title=title, description=description)

        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Get the filename from the URL
        filename = category.title + ".jpg"

        # official_id = instance.
        # Save the image to the model instance
        item.image.save(filename, ContentFile(response.content), save=True)
        try:
            wechat_user, _ = ChinaUsers.objects.get(wechat_id=instance.wechat_id)
            room_item = RoomItems.objects.create(
                category=category_title, price=10, name=title, description=description,
                room=wechat_user.room
            )
            room_item.image.save(filename, ContentFile(response.content), save=True)
        except Exception as e:
            pass
        run_in_thread(send_wechat_message_reply, (instance, item))
        run_in_thread(upload_community_posts, (item, instance))
    except Exception as e:
        InternalExceptions.objects.create(text=e)


def upload_community_posts(item, instance):
    official_account = WechatOfficialAccount.objects.get(official_id=instance.official_account_id)
    for community_id in official_account.communities:
        try:
            community = Community.objects.get(community_id=community_id)
            CommunityPosts.objects.get_or_create(community=community, item=item)
        except Exception as e:
            InternalExceptions.objects.create(text=e)


def create_room_and_china_user(wechat_id):
    wechat_user, created = ChinaUsers.objects.get_or_create(wechat_id=wechat_id)
    if created or wechat_user.room is None:
        room = Room.objects.create(custom_instructions=False)
        wechat_user.room = room
        wechat_user.save()
    if wechat_user.user is None:
        user = User.objects.create(
            first_name=str(uuid.uuid4()), email=str(wechat_user.wechat_user_id)+"@yopmail.com")
        wechat_user.user = user
        wechat_user.save()


def send_login_otp_reply(instance):
    try:
        from_user_name = instance.wechat_id
        user = ChinaUsers.objects.get(wechat_id=from_user_name)
        RoomLoginRequests.objects.filter(user=user).update(is_expired=True)
        request = RoomLoginRequests.objects.create(user=user)
        appid = ""
        appsecret = ""
        try:
            reply_message = {
                "touser": from_user_name,  # Use the 'FromUserName' you received in the incoming message
                "msgtype": "text",
                "text": {
                    "content": f"Room Login OTP is: {request.otp}"
                }
            }
            official_account = WechatOfficialAccount.objects.get(official_id=instance.official_account_id)
            if hasattr(official_account, "official_account"):
                appid = official_account.official_account.app_id
                appsecret = official_account.official_account.secret_id
        except Exception as e:
            reply_message = {
                "touser": from_user_name,  # Use the 'FromUserName' you received in the incoming message
                "msgtype": "text",
                "text": {
                    "content": "Account Not Registered With Us!!!"
                }
            }
        # Send the message using the WeChat API
        try:

            response1 = requests.post(
                'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
                    appid, appsecret))
            try:
                token = response1.json()["access_token"]
                response = requests.post('https://api.weixin.qq.com/cgi-bin/message/custom/send',
                                         params={'access_token': token},
                                         json=reply_message)
                InternalExceptions.objects.create(text=response.json())
            except KeyError:
                pass
        except Exception as e:
            InternalExceptions.objects.create(text=str(e))
    except Exception as e:
        InternalExceptions.objects.create(text=str(e))


def send_wechat_room_reply(instance):
    try:
        from_user_name = instance.wechat_id
        user = ChinaUsers.objects.get(wechat_id=from_user_name)
        room_id = user.room.room_id
        room_key = user.room.room_key
        appid = ""
        appsecret = ""
        try:
            reply_message = {
                "touser": from_user_name,  # Use the 'FromUserName' you received in the incoming message
                "msgtype": "text",
                "text": {
                    "content": f"Homelinked Room Credentials \n\n Room ID: {room_id}\n Room Key:{room_key}"
                }
            }
            official_account = WechatOfficialAccount.objects.get(official_id=instance.official_account_id)
            if hasattr(official_account, "official_account"):
                appid = official_account.official_account.app_id
                appsecret = official_account.official_account.secret_id
        except Exception as e:
            reply_message = {
                "touser": from_user_name,  # Use the 'FromUserName' you received in the incoming message
                "msgtype": "text",
                "text": {
                    "content": "Account Not Registered With Us!!!"
                }
            }
        # Send the message using the WeChat API
        try:

            response1 = requests.post(
                'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
                    appid, appsecret))
            try:
                token = response1.json()["access_token"]
                response = requests.post('https://api.weixin.qq.com/cgi-bin/message/custom/send',
                                         params={'access_token': token},
                                         json=reply_message)
                InternalExceptions.objects.create(text=response.json())
            except KeyError:
                pass
        except Exception as e:
            InternalExceptions.objects.create(text=str(e))
    except Exception as e:
        InternalExceptions.objects.create(text=str(e))