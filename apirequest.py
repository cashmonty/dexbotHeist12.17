import aiohttp
import datetime
import asyncio
import os
import discord
import requests
from utils import get_token_name_and_pool


SYVE_API_KEY = os.getenv('SYVE_API_KEY')
tensorapikey = os.getenv('X-TENSOR-API-KEY')
async def get_floor_info(ctx, slugdisplay):
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
        'X-TENSOR-API-KEY': tensorapikey
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
            floor_1h = f"{floor_1h:.4f}SOL"  # Formatting to two decimal places

        # Format Floor Change 24h
        if floor_24h != "N/A":
            floor_24h = float(floor_24h)  # Keep the original value
            floor_24h = f"{floor_24h:.4f}SOL"  # Formatting to two decimal places


        # Create embed with formatted prices
        embed = discord.Embed(title=f"{slugdisplay}", color=0x0099ff)
        embed.add_field(name="Buy Now Price", value=buy_now_price, inline=False)
        embed.add_field(name="Floor Change 24h", value=floor_24h, inline=False)
        embed.add_field(name="Floor Change 1h", value=floor_1h, inline=False)

        await ctx.send(embed=embed)

async def get_top_pools(network):
    url = f"https://api.geckoterminal.com/api/v2/networks/{network}/pools?include=include&page=1"
    headers = {'Accept': 'application/json;version=20230302'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
                
            else:
                print(f"Error fetching data with status code: {response.status}")
                return None
            
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
async def get_token_info(token_identifier, network):
    url = f'https://api.geckoterminal.com/api/v2/search/pools'
    headers = {'Accept': 'application/json;version=20230302'}
    params = {
        'query': token_identifier,
        'network': network,
        'page': 1
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error fetching data with status code: {response.status}")
                return None
async def get_wallet_info(wallet_address):
    url = 'https://api.syve.ai/v1/wallet-api/latest-performance-per-token'
    key = SYVE_API_KEY


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

async def get_ohlc_data(pool_address, network='eth', timeframe='hour', aggregate='1', limit='200'):
    # Constructing the URL with path parameters
    url = f'https://api.geckoterminal.com/api/v2/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}'

    # Setting up the query parameters
    params = {
        'aggregate': aggregate,
        'limit': limit
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error fetching data with status code: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"HTTP request error: {e}")
        return None
    except asyncio.TimeoutError as e:
        print(f"Request timed out: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None