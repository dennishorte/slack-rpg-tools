import random
import requests

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'


def parse_dice(dice_string):
    # Extract the number of dice from the string, defaulting to 0 if not specified.
    num_dice, remainder = dice_string.split('d')
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


def get_dice_values(num, size):
    rolls = []
    for i in range(num):
        rolls.append(random.randint(1, size))
    return rolls


def formatted_user_id(user_id):
    return '<@{}>'.format(user_id)


@app.route('/slack/rpg/dice/', methods=['POST'])
def roll_dice():
    data = request.form
    print('----------------------------------------------')
    print(data)

    args = request.form['text'].strip()
    args = args.split(' ', 1)
    dice_string = args[0]

    num_dice, die_size, modifier = parse_dice(dice_string)
    result = get_dice_values(num_dice, die_size)

    message = '{} rolled {} and got *{}* _rolls: {}_'.format(
        formatted_user_id(request.form['user_id']),
        dice_string,
        sum(result) + modifier,
        result
    )

    return jsonify(
        success=True,
        response_type="in_channel",
        text=message,
    )
