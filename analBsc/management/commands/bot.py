from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from telegram import Update, ForceReply
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater, CommandHandler

from analBsc.models import Profile


def check_username_authorized(username: str, chat_id: int):
    try:
        password_used = Profile.objects.get(user_name=username, external_id=chat_id).password_used
        return password_used
    except ObjectDoesNotExist:
        return False


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
            reply_markup=ForceReply(selective=True),
        )
    except ObjectDoesNotExist:
        update.message.reply_text(
            'Пароль неверный',
            reply_markup=ForceReply(selective=True),
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
