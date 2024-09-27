"""
Manager the "ping" event
"""

async def run(data: dict):
    """
    Process the "ping" event
    """
    print(f'ping: {data["zen"]} - {data["hook_id"]}')
