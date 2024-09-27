"""Define the event map config class"""

from typing import Optional, TypedDict, Literal

class TelegramTarget(TypedDict):
    """TelegramTarget"""
    _: Literal['telegram-target']
    chat: int
    topic: Optional[int]


class Worker(TypedDict):
    """Listener"""
    _: Literal['worker']


class PushNotificationWorker(Worker):
    """PushNotification"""
    _: Literal['push-worker']
    message: str
    telegram_target: Optional[TelegramTarget]


class EventListener(TypedDict):
    """EventListener"""
    _: Literal['event-listener']


class PushEventListener(EventListener):
    """EventListener"""
    _: Literal['push-event-listener']
    repository_target: str
    worker: Optional[Worker]


class EventMapConfig(TypedDict):
    """EventMapConfig"""

    _: Literal['event-map']
    service_name: str
    """A custom name"""
    event_type: str
    """Define the event type"""
    listener: EventListener
