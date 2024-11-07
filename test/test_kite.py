import asyncio
from concurrent.futures import ThreadPoolExecutor

import pytest

from kite import kite_quote_service
from singleton import kite_info_service, kite_quote_service


def test_kite_info_sync():
    kite_info_service._sync_model_with_kite()


@pytest.mark.asyncio
async def test_kite_tick():
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        loop.run_in_executor(pool, kite_quote_service.add_stock, "NIFTY 50")
    await asyncio.get_event_loop().create_future()
