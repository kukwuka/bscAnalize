import telegram
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from telegram import Update, ForceReply
from telegram.ext import Filters, MessageHandler, Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from analBsc.models import Profile, Admin


def check_username_authorized(username: str, chat_id: int):
    try:
        password_used = Profile.objects.get(user_name=username, external_id=chat_id).password_used
        return password_used
    except ObjectDoesNotExist:
        return False


def notification_for_admin(text: str):
    bot_admin = telegram.Bot(token=settings.TOKEN_ADMIN)
    admins_query = Admin.objects.all().exclude(external_id=0)
    for admin in admins_query:
        bot_admin.send_message(admin.external_id, text)


def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    username = update.message.chat.username
    chat_id = int(update.message.chat.id)
    password_used = check_username_authorized(username, chat_id)
    if not password_used:
        update.message.reply_markdown_v2(
            'Введите пароль и автаризутесь',
            reply_markup=ForceReply(selective=True),
        )


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""

    update.message.reply_text('Ждите сигнала!')


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    username = update.message.chat.username
    password = update.message.text
    chat_id = update.message.chat.id
    try:
        profile_check = Profile.objects.get(password=password, disabled=True)
        profile_check.authorize(username, chat_id)

        update.message.reply_text(
            'Вы авторизованиы, ждите сигнала',
        )

    except ObjectDoesNotExist:
        update.message.reply_text(
            'Пароль неверный',
        )


def button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    try:
        Profile.objects.get(blockchain_address=query.data, disabled=True)
        query.edit_message_text(text=f" \U0000274c Вы отказались от продажи на сегодня, Благодарим за Ответ")
        notification_for_admin(
            f'\U0000274c Пользователь с адресом {query.data} отказался от сигнала, '
            f'Проверьте егодействия по адресу https://bscscan.com/address/{query.data}'

        )
    except ObjectDoesNotExist:
        query.edit_message_text(
            'Пароль неверный',
        )


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **kwargs):
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        updater = Updater(settings.TOKEN)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        updater.dispatcher.add_handler(CallbackQueryHandler(button))

        # on non command i.e message - echo the message on Telegram
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()

# get balance of user we dont need
# def balance_of_user(update: Update, _: CallbackContext):
#     username = update.message.chat.username
#     profile = Profile.objects.get(user_name=username, disabled=True)
#     user_addresss = profile.blockchain_address
#     password_used = profile.password_used
#     if not password_used:
#         update.message.reply_text(
#             'Введите парольa',
#             reply_markup=ForceReply(selective=True),
#         )
#         return
#     balance = utils.user_Dfx_balance(user_addresss)
#     # print(addresses)
#     # print(sum_of_balances)
#     update.message.reply_text(
#         str(balance),
#         reply_markup=ForceReply(selective=True),
#     )
#
# def info_comand(update: Update, _: CallbackContext):
#     username = update.message.chat.username
#     profile = Profile.objects.get(user_name=username, disabled=True)
#     password_used = profile.password_used
#     if not password_used:
#         update.message.reply_text(
#             'Введите парольa',
#             reply_markup=ForceReply(selective=True),
#         )
#         return
#     profile_query_set = Profile.objects.filter(disabled=True, password_used=True)
#     addresses, sum_of_balances = utils.balance_of_persons(profile_query_set)
#     print(addresses)
#     print(sum_of_balances)
#     update.message.reply_text(
#         str(addresses[profile.blockchain_address] * service.yesterday_buy_sold_delta()),
#         reply_markup=ForceReply(selective=True),
#     )
