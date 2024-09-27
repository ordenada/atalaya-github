"""
Manager the "ping" event
"""

from flask import jsonify


async def run(_data: dict):
    """
    Return "pong"
    """
    return jsonify({"msg": "pong"}), 200
