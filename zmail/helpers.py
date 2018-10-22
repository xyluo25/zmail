import datetime
import os
import re
from typing import Optional

from .exceptions import InvalidArguments
from .structures import CaseInsensitiveDict

DATETIME_PATTERN = re.compile(r'([0-9]+)?-?([0-9]{1,2})?-?([0-9]+)?\s*([0-9]{1,2})?:?([0-9]{1,2})?:?([0-9]{1,2})?\s*')


def convert_date_to_datetime(_date: str or datetime.datetime) -> datetime.datetime:
    """Convert date like '2018-1-1 12:00:00 to datetime object.'"""
    if isinstance(_date, datetime.datetime):
        # Shortcut
        return _date

    _match_info = DATETIME_PATTERN.fullmatch(_date)
    if _match_info is not None:
        year, month, day, hour, minute, second = [int(i) if i is not None else None for i in _match_info.groups()]
    else:
        raise InvalidArguments('Invalid date format ' + str(_date))

    if None in (year, month, day):
        now = datetime.datetime.now()
        year = year or now.year
        month = month or now.month
        day = day or now.day
    if None in (hour, minute, second):
        hour = hour or 0
        minute = minute or 0
        second = second or 0

    return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)


def match_conditions(mail_headers: CaseInsensitiveDict,
                     subject: Optional[str] = None,
                     start_time: Optional[datetime.datetime] = None,
                     end_time: Optional[datetime.datetime] = None,
                     sender: Optional[str] = None) -> bool:
    """Match all conditions."""
    mail_subject = mail_headers.get('subject')  # type:str or None
    mail_sender = mail_headers.get('from')  # type:str or None
    mail_date = mail_headers.get('date')  # type: datetime.datetime or None

    if subject is not None:
        if mail_subject is None or subject not in mail_subject:
            return False

    if sender is not None:
        if mail_sender is None or sender not in mail_sender:
            return False

    if start_time is not None:
        if isinstance(start_time, str):
            start_as_datetime = convert_date_to_datetime(start_time)
        elif isinstance(start_time, datetime.datetime):
            start_as_datetime = start_time
        else:
            raise InvalidArguments('after excepted type str or datetime.datetime got {}'.format(type(start_time)))

        if mail_date is None or start_as_datetime > mail_date:
            return False

    if end_time is not None:
        if isinstance(end_time, str):
            end_as_datetime = convert_date_to_datetime(end_time)
        elif isinstance(end_time, datetime.datetime):
            end_as_datetime = end_time
        else:
            raise InvalidArguments('before excepted type str or datetime.datetime got {}'.format(type(end_time)))

        if mail_date is None or end_as_datetime < mail_date:
            return False

    return True


def make_iterable(obj) -> list or tuple:
    """Get an iterable obj."""
    return obj if isinstance(obj, (tuple, list)) else (obj,)


def get_abs_path(file: str) -> str:
    """if the file exists, return its abspath or raise a exception."""
    if os.path.exists(file):
        return file

    # Assert file exists in currently directory.
    work_path = os.path.abspath(os.getcwd())

    if os.path.exists(os.path.join(work_path, file)):
        return os.path.join(work_path, file)
    else:
        raise FileExistsError("The file %s doesn't exist." % file)
