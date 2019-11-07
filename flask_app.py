import random
import requests

from flask import Flask
from flask import request

app = Flask(__name__)

BEARER_TOKEN = None

@app.route('/')
def hello_world():
    return 'Hello from Flask!'


def parse_dice_text(dice_text):
    """
    Returns a tuple of 3 ints.
      0: the number of dice
      1: the size of each die (eg. number of faces)
      2: the modifier to apply to the die (eg. +2 or -3 or 0)
    """

    # Extract the number of dice from the string, defaulting to 0 if not specified.
    num_dice, remainder = dice_text.split('d')
    if not num_dice:
        num_dice = 1
    else:
        num_dice = int(num_dice)

    # Extract the modifier from the die size
    if '+' in remainder:
        die_size, modifier = remainder.split('+')
        modifier = int(modifier)
    elif '-' in remainder:
        die_size, modifier = remainder.split('-')
        modifier = -int(modifier)
    else:
        modifier = 0
        die_size = remainder

    # Convert the die size to an int
    die_size = int(die_size)

    return num_dice, die_size, modifier


def parse_dice_args(dice_args):
    """
    Returns a tuple of two string, the dice part (eg. 2d6+2), and a possibly
    empty arbitrary message.
    """
    args = dice_args.strip().split(' ', 1)
    if len(args) == 1:
        args.append('')
    return args

def get_dice_rolls(num, size):
    rolls = []
    for i in range(num):
        rolls.append(random.randint(1, size))
    return rolls


def send_die_roll_message(channel_id, user_id, dice_args):
    """
    Channel and username should be in unescaped format.
      eg. just U1234 or #C1234, and NOT <@U1234|user> <#C1234|general>
    """
    dice_text, comment = parse_dice_args(dice_args)
    num_dice, die_size, modifier = parse_dice_text(dice_text)
    dice_rolls = get_dice_rolls(num_dice, die_size)
    message = '<@{}> got *{}* on {}'.format(
        user_id,
        sum(dice_rolls) + modifier,
        dice_text,
    )

    if comment:
        message += ': _{}_'.format(comment)

    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer {}".format(BEARER_TOKEN)
    }

    message_response = requests.post(
        'https://slack.com/api/chat.postMessage',
        headers=headers,
        json={
            'channel': channel_id,
            'text': message,
        }
    )

    print(message_response.__dict__)

@app.route('/slack/rpg/dice/', methods=['POST'])
def roll_dice():
    send_die_roll_message(
        request.form.get('channel_id'),
        request.form.get('user_id'),
        request.form.get('text'),
    )

    return '', 200
