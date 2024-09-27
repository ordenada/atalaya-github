"""Main"""
import os
import hmac
import hashlib
import json
from dotenv import load_dotenv
from flask import Flask, request, abort, Response

import event_map
from webhook import ping, push


load_dotenv()

SECRET = os.environ['SECRET']

# This function validate the signature using the secret and the hmac alhgorithm


def verify_signature(secret: str, payload: str, signature: str):
    """Verify the Github signature.

    Args:
        secret (str): The current secret.
        payload (str): The payload.
        signature (str): The provided signature.

    Returns:
        bool: True if the signature is verified.
    """
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = f'sha256={mac.hexdigest()}'
    return hmac.compare_digest(expected_signature, signature)


def load_config():
    """Load config from config.json"""
    with open('config.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Get the event map config
    event_map_list: list[event_map.EventMapConfig] = data['events']
    return event_map_list


app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
async def webhook_receiver():
    """webhook"""
    signature = request.headers.get('X-Hub-Signature-256')
    payload = request.data
    if signature is None or not verify_signature(SECRET, payload, signature):
        abort(400, 'What')

    # Check the event
    event = request.headers.get('X-GitHub-Event')
    print('event:', event)

    data = request.json  # Get the JSON data from the incoming request

    print("Received webhook data:", data)

    event_map_list = load_config()
    events = [
        event_map
        for event_map in event_map_list
        if event \
            and event_map['_'] == 'event-map' \
                and event_map['event_type'] == event]

    if not event:
        abort(400)
    elif event == 'ping':
        await ping.run(data)
    elif event == 'push':
        await push.run(data, event_map_list=events)
    else:
        abort(400)

    return Response(status=204)

if __name__ == '__main__':
    app.run(debug=True)
