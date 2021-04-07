import datetime

import telegram
from django.conf import settings

from analBsc import utils, service
from djangoProject.celery import app
from .models import Profile, Admin


@app.task()
def let_update_schedule():
    print("starting set schedule for messages")
    profile_query_set = Profile.objects.filter(disabled=True, password_used=True)
    addresses, sum_of_balances = utils.balance_of_persons(profile_query_set)
    time_delta = datetime.timedelta(minutes=1).seconds / len(profile_query_set)
    yesterday_delta = service.yesterday_buy_sold_delta()

    if yesterday_delta > 0:
        for i in range(len(profile_query_set)):
            time_to_send = time_delta * (i + 1)
            summ = addresses[profile_query_set[i].blockchain_address] * yesterday_delta * profile_query_set[
                i].coefficient
            text = f'вы можете сегодня продать' \
                   f' {str(summ)} '
            chat_id = profile_query_set[i].external_id
            address = profile_query_set[i].blockchain_address
            print(address)
            send_message.apply_async((chat_id, text, address), countdown=time_to_send)
            admin_check_user_movies.apply_async((address,), countdown=time_to_send + time_delta)
    else:
        for i in range(len(profile_query_set)):
            time_to_send = time_delta * (i + 1)
            text = f'Не продавайте сегодня (совет)'
            chat_id = profile_query_set[i].external_id
            address = profile_query_set[i].blockchain_address
            send_message.apply_async((chat_id, text, address), countdown=time_to_send)


@app.task()
def send_message(chat_id: int, text: str, address: str):
    print(f'sending message to {str(chat_id)} with test : {text}')
    bot = telegram.Bot(token=settings.TOKEN)
    bot.send_message(chat_id, text)
    send_notification_to_admins(text, address)


def send_notification_to_admins(client_message: str, address: str):
    bot_admin = telegram.Bot(token=settings.TOKEN_ADMIN)
    admins_query = Admin.objects.all().exclude(external_id=0)
    text = f"""Отправилось сообщение пользователю с адресом {address}, с текстом :
    {client_message}"""
    for admin in admins_query:
        print(text)
        bot_admin.send_message(admin.external_id, text)


@app.task()
def admin_check_user_movies(address):
    bot_admin = telegram.Bot(token=settings.TOKEN_ADMIN)
    admins_query = Admin.objects.all().exclude(external_id=0)
    text = f""" У адреса: {address} истекло время , проверьте какие операции он совершил в админ панели или на bscScan по ссылку
        https://bscscan.com/address/{address}
    """
    for admin in admins_query:
        bot_admin.send_message(admin.external_id, text)
