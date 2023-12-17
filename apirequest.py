import aiohttp
import datetime
import asyncio
import os

API_KEY = os.getenv('SYVE_API_KEY')

async def get_token_info(token_address, network):
    url = f'https://api.geckoterminal.com/api/v2/networks/{network}/tokens/{token_address}/pools'
    params = {'page': 1}
    headers = {'Accept': 'application/json;version=20230302'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error fetching data with status code: {response.status}")
                return None
    # Exception handling remains the same

async def get_ohlc_data(token_address, interval='1h'):
    url = 'https://api.syve.ai/v1/price/historical/ohlc'
    
    # Set the current timestamp
    now_timestamp = int(datetime.datetime.now().timestamp())

    # Ensure that the API key is not None
    if API_KEY is None:
        raise ValueError("The API_KEY environment variable is not set.")

    # Setting default values for other parameters
    params = {
        'token_address': token_address,
        'pool_address': 'all',  # Default to consider all pools
        'price_type': 'price_token_usd_robust_tick_1',  # Default price type
        'interval': interval,
        'from_timestamp': 0,  # Default
        'until_timestamp': now_timestamp,  # Current timestamp
        'max_size': 100,  # Default
        'fill': 'true',
        'order': 'desc',
        'with_volume': 'true',
        'key': API_KEY  # Ensure the API key is correctly set
    }

    # Check for None values in params
    for key, value in params.items():
        if value is None:
            raise ValueError(f"The value for '{key}' in params cannot be None.")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            # The rest of your function remains unchanged
