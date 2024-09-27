"""
Manager the "push" event
"""
import os
import re
from typing import cast
import event_map
from communications.telegram.bot import TelegramBot


def flatten_dict(d, parent_key='', sep='.'):
    """Flat a dict in one-dimension dict"""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items[f"{new_key}{sep}{i}"] = item
        else:
            items[new_key] = v
    return items


def extract_variables(value):
    """Extract variables"""
    #  Escape the chars if it begins with \
    escaped_braces_pattern = r'\\\{|\}\\'
    # Replace the escaped chars
    unescaped_value = re.sub(escaped_braces_pattern, '{', value)
    unescaped_value = re.sub(escaped_braces_pattern, '}', unescaped_value)

    # Encontrar todas las variables entre {}
    variables = re.findall(r'\{(.*?)\}', unescaped_value)
    return variables


def replace_variables(value: str, substitutions: dict[str, str]):
    """Replace variables"""
    # Replace the escape chars
    value = re.sub(r'\\\{', '{', value)
    value = re.sub(r'\\\}', '}', value)

    # Get the variables
    variables = extract_variables(value)
    # Replace the variables in the string
    for var in variables:
        # Use the .get method to avoid KeyError if the variable is not in
        value = value.replace(f'{{{var}}}', str(substitutions.get(var, f'{{{var}}}')))
    return value


def prepare_computed_vars(data: dict):
    """Prepare computed variables"""
    commits = data.get('commits', [])
    raw_added: list[str] = []
    raw_removed: list[str] = []
    raw_modified: list[str] = []

    for commit in commits:
        raw_added.extend(commit.get('added', []))
        raw_removed.extend(commit.get('removed', []))
        raw_modified.extend(commit.get('modified', []))

    # Prepare in one-line
    added = '\n'.join([f'+ {line}' for line in raw_added])
    removed = '\n'.join([f'- {line}' for line in raw_removed])
    modified = '\n'.join([f'* {line}' for line in raw_modified])

    # Return
    return {
        'added_files': added,
        'removed_files': removed,
        'modified_files': modified,
        'ln': '\n',
    }


async def run(data: dict, event_map_list: list[event_map.EventMapConfig]):
    """
    Process the "push" event
    """
    for event in event_map_list:
        try:
            if event['_'] != 'event-map':
                print('malformed event:', event)
                continue

            if event['event_type'] != 'push':
                print('unknown event type :', event)
                continue

            print('calling to', event['service_name'])
            if event['listener']['_'] == 'push-event-listener':
                listener = cast(event_map.EventListener, event['listener'])
                if listener['_'] != 'push-event-listener':
                    print('malformed listener:', listener)
                    continue

                listener = cast(event_map.PushEventListener, event['listener'])
                repository_target = listener['repository_target']
                # Check the repository for the event
                if repository_target != data['repository']['full_name']:
                    print('error: different repository target:',
                          data['repository']['full_name'])
                    continue

                worker = listener.get('worker')
                if not worker:
                    print('no worker for', event['service_name'])
                    continue

                if worker['_'] != 'push-worker':
                    print('worker ignored:', worker)
                    continue

                worker = cast(event_map.PushNotificationWorker, worker)

                message = worker['message']
                variables = extract_variables(message)
                print(variables)
                data_values = flatten_dict(data)
                data_values.update(prepare_computed_vars(data))
                message = replace_variables(message, data_values)

                print('message from',
                      event['service_name'] + ':',
                      message)
                if worker['telegram_target']:
                    target = cast(event_map.TelegramTarget, worker['telegram_target'])
                    # Create a Telegram bot object
                    token = os.environ.get('TELEGRAM_BOT_TOKEN')
                    if not token:
                        print('missing the telegram bot token')
                        continue
                    telegram_bot = TelegramBot(token=token)
                    await telegram_bot.bot.send_message(
                        chat_id=target['chat'],
                        text=message,
                        message_thread_id=target.get('topic'),
                    )
        # pylint: disable=broad-exception-caught
        except Exception as err:
            print(err)
            raise err
