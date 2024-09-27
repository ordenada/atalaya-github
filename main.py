"""Main"""
import os
import hmac
import hashlib
from typing import Optional
from dotenv import load_dotenv
from flask import Flask, request, abort, Response

from webhook import ping


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

    reply: Optional[tuple[Response, int]] = None

    if not event:
        abort(400)
    elif event == 'ping':
        reply = await ping.run(data)

    if reply:
        return reply

    return Response(status=204)

if __name__ == '__main__':
    app.run(debug=True)
