import datetime

import telegram
from django.conf import settings

from analBsc import utils, service
from djangoProject.celery import app
from .models import Profile


@app.task()
def let_update_schedule():
    print("starting set schedule for messages")
    profile_query_set = Profile.objects.filter(disabled=True, password_used=True)
    addresses, sum_of_balances = utils.balance_of_persons(profile_query_set)
    time_to_stop = datetime.timedelta(minutes=1).seconds / len(profile_query_set)
    yesterday_delta = service.yesterday_buy_sold_delta()

    if yesterday_delta > 0:
        for i in range(len(profile_query_set)):
            time_to_send = time_to_stop * (i + 1)
            text = f'вы можете сегодня продать {str(addresses[profile_query_set[i].blockchain_address] * yesterday_delta)}'
            chat_id = profile_query_set[i].external_id
            send_message.apply_async((chat_id, text), countdown=time_to_send)
    else:
        for i in range(len(profile_query_set)):
            time_to_send = time_to_stop * (i + 1)
            text = f'Не продавайте сегодня (совет)'
            chat_id = profile_query_set[i].external_id
            send_message.apply_async((chat_id, text), countdown=time_to_send)


@app.task()
def send_message(chat_id: int, text: str):
    print(f'sending message to {str(chat_id)} with test : {text}')
    bot = telegram.Bot(token=settings.TOKEN)
    bot.send_message(chat_id, text)
