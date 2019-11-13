import random
import requests

from flask import Flask
from flask import request

app = Flask(__name__)

BEARER_TOKEN = None

@app.route('/')
def hello_world():
    return 'Hello from Flask!'


def send_public_message(channel_id, message):
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer {}".format(BEARER_TOKEN),
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


def escape_user_id(user_id):
    return '<@{}>'.format(user_id)


class DiceCommand(object):
    def __init__(self, dice_command_string):
        self.num_dice = None
        self.die_size = None
        self.modifier = None
        self.dice_string = None
        self.comment = None
        self.rolls = []

        self._get_dice_string_and_comment(dice_command_string)
        self._parse_dice_string()
        self.roll()


    def _get_dice_string_and_comment(self, dice_args):
        """
        Returns a tuple of two string, the dice part (eg. 2d6+2), and a possibly
        empty arbitrary message.
        """
        args = dice_args.strip().split(' ', 1)
        self.dice_string = args[0]
        if len(args) > 1:
            self.comment = args[1]


    def _parse_dice_string(self):
        # Extract the number of dice from the string, defaulting to 1 if not specified.
        num_dice, remainder = self.dice_string.split('d')
        if not num_dice:
            num_dice = 1

        # Extract the modifier from the die size
        if '+' in remainder:
            die_size, modifier = remainder.split('+')
        elif '-' in remainder:
            die_size, modifier = remainder.split('-')
            modifier = '-' + modifier
        else:
            modifier = 0
            die_size = remainder

        # Convert the die size to an int
        self.num_dice = int(num_dice)
        self.modifier = int(modifier)
        self.die_size = int(die_size)

    def roll(self):
        self.rolls = []
        for i in range(self.num_dice):
            self.rolls.append(random.randint(1, self.die_size))
        return sum(self.rolls) + self.modifier


def send_die_roll_message(channel_id, user_id, dice_args):
    """
    Channel and username should be in escaped format.
      eg. <@U1234|user> <#C1234|general>
    """
    dice = DiceCommand(dice_args)
    message = '{} got *{}* on {}'.format(
        escape_user_id(user_id),
        dice.roll(),
        dice.dice_string,
    )

    if dice.comment:
        message += ': _{}_'.format(dice.comment)

    print('===== posting message =====')
    print(message)
    print(channel_id)

    send_public_message(channel_id, message)


@app.route('/slack/rpg/dice/', methods=['POST'])
def roll_dice():
    data = request.form
    print('----------------------------------------------')
    print(data)

    send_die_roll_message(
        request.form.get('channel_id'),
        request.form.get('user_id'),
        request.form.get('text'),
    )

    return '', 200

@app.route('/slack/rpg/secretdice/', methods=['POST'])
def secretly_roll_dice():
    send_public_message(
        request.form.get('channel_id'),
        '{} secretly rolls some dice.'.format(
            escape_user_id(request.form.get('user_id'))
        )
    )

    return '', 200
