import aiohttp
import datetime
import asyncio
import os
import discord
import requests
from utils import get_token_name_and_pool


API_KEY = os.getenv('SYVE_API_KEY')

async def get_floor_info(ctx, slugdisplay):
    api_key = 'd63f8020-97ac-4592-bf1f-962e19126eb6'
    url = 'https://api.tensor.so/graphql'
    query = """
        query ExampleQuery($slugsDisplay: [String!]) {
            allCollections(slugsDisplay: $slugsDisplay) {
                collections {
                    compressed
                    createdAt
                    creator
                    description
                    id
                    statsV2 {
                        buyNowPrice
                        floor1h
                        floor24h
                        floor7d
                        marketCap
                        numBids
                        sellNowPrice
                    }
                }
            }
        }
    """
    variables = {"slugsDisplay": slugdisplay}
    headers = {
        'Content-Type': 'application/json',
        'X-TENSOR-API-KEY': api_key
    }
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})

    if response.status_code == 200:
        data = response.json()
        all_collections = data.get("data", {}).get("allCollections", {}).get("collections", [])

        if not all_collections:
            await ctx.send("No collections found for the given slug.")
            return

    for collection in all_collections:
        stats = collection.get("statsV2", {})
        
        # Apply formatting to the 'buy now price'
        buy_now_price = stats.get("buyNowPrice", "N/A")
        if buy_now_price != "N/A":
            buy_now_price = float(buy_now_price) * 1e-09  # Convert to SOL
            buy_now_price = f"{buy_now_price:,.2f}SOL"    # Formatting to two decimal places

        floor_1h = stats.get("floor1h", "N/A")
        floor_24h = stats.get("floor24h", "N/A")

        # Format Floor Change 1h
        if floor_1h != "N/A":
            floor_1h = float(floor_1h)   # Keep the original value
            floor_1h = f"{floor_1h:.2f}SOL"  # Formatting to two decimal places

        # Format Floor Change 24h
        if floor_24h != "N/A":
            floor_24h = float(floor_24h)  # Keep the original value
            floor_24h = f"{floor_24h:.2f}SOL"  # Formatting to two decimal places


        # Create embed with formatted prices
        embed = discord.Embed(title=f"{slugdisplay}", color=0x0099ff)
        embed.add_field(name="Buy Now Price", value=buy_now_price, inline=False)
        embed.add_field(name="Floor Change 24h", value=floor_24h, inline=False)
        embed.add_field(name="Floor Change 1h", value=floor_1h, inline=False)

        await ctx.send(embed=embed)
async def get_trade_info(token_pool, trade_volume_in_usd_greater_than, network='eth'):


    url = f'https://api.geckoterminal.com/api/v2/networks/{network}/pools/{token_pool}/trades?trade_volume_in_usd_greater_than={trade_volume_in_usd_greater_than}'

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
async def get_wallet_info(wallet_address):
    url = 'https://api.syve.ai/v1/wallet-api/latest-performance-per-token'
    key = 'g3rt33RwSAceXr'


    params = {
        'key': key,
        'wallet_address': wallet_address,

    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                    # Include token_name in the data returned
                    
                else:
                    print(f"Error fetching data with status code: {response.status}")
                    return None, None
    except aiohttp.ClientError as e:
        print(f"HTTP request error: {e}")
        return None, None
    except asyncio.TimeoutError as e:
        print(f"Request timed out: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

async def get_ohlc_data(token_address, interval, max_size='200'):
    url = 'https://api.syve.ai/v1/price/historical/ohlc'

    pool_address = 'all'  # default to consider all pools
    price_type = 'price_token_usd_robust_tick_1'  # default price type
    from_timestamp = 0  # default
    until_timestamp = int(datetime.datetime.now().timestamp())  # current timestamp
    fill = 'true'
    order = 'desc'
    volume = 'true'
    key = 'g3rt33RwSAceXr'


    params = {
        'key': key,
        'token_address': token_address,
        'pool_address': pool_address,
        'price_type': price_type,
        'interval': interval,
        'from_timestamp': from_timestamp,
        'until_timestamp': until_timestamp,
        'max_size': max_size,
        'order': order,
        'fill': fill,
        'with_volume': volume
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                    # Include token_name in the data returned
                    
                else:
                    print(f"Error fetching data with status code: {response.status}")
                    return None, None
    except aiohttp.ClientError as e:
        print(f"HTTP request error: {e}")
        return None, None
    except asyncio.TimeoutError as e:
        print(f"Request timed out: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None