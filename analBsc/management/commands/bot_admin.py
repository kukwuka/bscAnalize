from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from telegram import Update, ForceReply
from telegram.ext import CallbackContext, Updater, CommandHandler

from analBsc import service
from analBsc.models import Admin


def authorize_in_system(update: Update) :
    username = update.message.chat.username
    chat_id = update.message.chat.id
    try:
        admin = Admin.objects.get(user_name=username)
        if not admin.external_id == int(chat_id):
            admin.external_id = int(chat_id)
            admin.save()
            update.message.reply_markdown_v2(
                f'Вы автаризованы под ником {admin.user_name}',
                reply_markup=ForceReply(selective=True),
            )
        return admin
    except ObjectDoesNotExist:
        update.message.reply_markdown_v2(
            'Вас нет в списках на админство(',
            reply_markup=ForceReply(selective=True),
        )
        raise NameError('Не админ(')


def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    try:
        admin = authorize_in_system(update)
        update.message.reply_markdown_v2(
            'Ждите инфу , пока можете юзнуть команду /yesterday',
            reply_markup=ForceReply(selective=True),
        )
    except Exception:
        pass


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    try:
        admin = authorize_in_system(update)
        update.message.reply_markdown_v2(
            'Ждите инфу , пока можете юзнуть команду /yesterday',
            reply_markup=ForceReply(selective=True),
        )
    except Exception:
        pass


def yesterday(update: Update, _: CallbackContext):
    """Send a message when the command /start is issued."""
    admin = authorize_in_system(update)
    delta = service.yesterday_buy_sold_delta()
    print(delta)
    update.message.reply_text(
        f'{delta}',
        reply_markup=ForceReply(selective=True),
    )
    # except Exception as e:
    #     print(e)


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **kwargs):
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        updater = Updater(settings.TOKEN_ADMIN)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("yesterday", yesterday))

        # on non command i.e message - echo the message on Telegram

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()
