import datetime
import hashlib
import re
import hashlib
import functools
import typing
import asyncio

# credit Lukasz Kwiencinski
# https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

def timelog(text, return_text=False):
    now = datetime.datetime.now()
    now_text = now.strftime("%Y-%m-%d %H:%M:%S")
    text = f"[{now_text}] - {text}"
    print(text)
    if return_text:
        return text

def hash256(string):
    return hashlib.sha3_256(string.encode('utf-8')).hexdigest()

def remove_unicode(string):
    return re.sub(r"\\u.{4}", "", string)

def only_a_to_z(string):
    return re.sub(r'[^0-9a-z]',"",asciinator(string.lower()))

def asciinator(text):
    return text.replace("é", "e").replace("—", "-")

def get_longest_text(lst):
    longest_text_len = 0
    for item in lst:
        current_text_len = len(item)
        if current_text_len > longest_text_len:
            longest_text_len = current_text_len
    return longest_text_len