import re
from decimal import Decimal
from typing import Dict
from urllib.parse import urlencode

import aiohttp

import ujson

from ..box import box
from ..command import argument
from ..event import Message
from ..session import client_session

QUERY_RE = re.compile(
    '^(\d+(?:\.\d+)?)\s*(\S+)(?:\s+(?:to|->|=)\s+(\S+))?$',
    re.IGNORECASE
)
SHORTCUT_TABLE: Dict[str, str] = {
    '$': 'USD',
    '달러': 'USD',
    '\\': 'KRW',
    '원': 'KRW',
    '엔': 'JPY',
    '유로': 'EUR',
}


class ExchangeError(Exception):
    """Exception for exchange."""


class SameBaseAndTo(ExchangeError):
    """Base and to symbol is same."""


class WrongBase(ExchangeError):
    """Wrong base unit."""


class WrongTo(ExchangeError):
    """Wrong to unit."""


async def get_exchange_rate(base: str, to: str) -> Dict:
    """Get exchange rate."""

    if base == to:
        raise SameBaseAndTo()

    url = 'https://api.fixer.io/latest?{}'.format(
        urlencode({'base': base, 'symbols': to})
    )

    try:
        async with client_session() as session:
            async with session.get(url) as res:
                data = await res.json(loads=ujson.loads)
                if to in data['rates']:
                    return data
                else:
                    raise WrongTo()
    except aiohttp.client_exceptions.ClientResponseError:
        raise WrongBase()


@box.command('환율', ['exchange'])
@argument('query', nargs=-1, concat=True)
async def exchange(bot, event: Message, query: str):
    """
    환전시 얼마가 되는지 계산.

    `환율 100엔` (100 JPY가 KRW로 얼마인지 계산)
    `환율 100 JPY to USD` (100 JPY가 USD로 얼마인지 계산)

    """

    match = QUERY_RE.match(query)
    if match:
        quantity = Decimal(match.group(1))
        base = SHORTCUT_TABLE.get(match.group(2), match.group(2))
        to = SHORTCUT_TABLE.get(match.group(3), match.group(3)) or 'KRW'

        data = None
        error = None
        try:
            data = await get_exchange_rate(base, to)
        except SameBaseAndTo:
            error = '변환하려는 두 화폐가 같은 단위에요!'
        except WrongBase:
            error = '출발 화폐가 지원되는 통화기호가 아니에요!'
        except WrongTo:
            error = '도착 화폐가 지원되는 통화기호가 아니에요!'

        if error:
            await bot.say(
                event.channel,
                error
            )
            return

        if data:
            date = data['date']
            rate = Decimal(data['rates'][to])

            result = quantity * rate

            await bot.say(
                event.channel,
                f'{quantity} {base} == {result:.2f} {to} ({date})'
            )
        else:
            await bot.say(
                event.channel,
                '알 수 없는 에러가 발생했어요! 아빠에게 문의해주세요!'
            )
    else:
        await bot.say(
            event.channel,
            '주문을 이해하는데에 실패했어요!'
        )
