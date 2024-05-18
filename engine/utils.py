import base64

import requests
from django.core.files.base import ContentFile

from engine.models import InternalExceptions, KeyManagement, Items, ListingType, Category


def send_wechat_message_reply(instance):
    from_user_name = instance.wechat_id
    url = instance.pic_url
    title = generate_item_content(url, "Tell me about this image")
    reply_message = {
        "touser": from_user_name,  # Use the 'FromUserName' you received in the incoming message
        "msgtype": "text",
        "text": {
            "content": title
        }
    }

    # Send the message using the WeChat API
    try:
        appid = "wx7ca28a877b5f606d"
        appsecret = "e80ccba43de5e0ac70dfdd61ab2ee9ed"
        response1 = requests.post(
            'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(
                appid, appsecret))
        try:
            token = response1.json()["access_token"]
            response = requests.post('https://api.weixin.qq.com/cgi-bin/message/custom/send',
                                     params={'access_token': token},
                                     json=reply_message)
            InternalExceptions.objects.create(text=response.json())
            print(response.json())
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


def upload_new_wechat_listing(url):
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
        filename = url.split('/')[-1]

        # Save the image to the model instance
        item.image.save(filename, ContentFile(response.content), save=True)
    except Exception as e:
        InternalExceptions.objects.create(text=str(e))