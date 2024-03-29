import aiohttp
import datetime
import asyncio
import os
import discord
import pandas as pd
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
            await ctx.send("Ensure the slug or display name is correct. Only provides data if available.")
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
    url = f"https://api.geckoterminal.com/api/v2/networks/{network}/trending_pools?include=include&page=1"
    headers = {'Accept': 'application/json;version=20230302'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
                
            else:
                print(f"Error fetching data with status code: {response.status}")
                return None
async def get_cat_pools(network):
    base_url = f"https://api.geckoterminal.com/api/v2/networks/{network}/new_pools"
    headers = {'Accept': 'application/json;version=20230302'}
    max_pages = 10
    all_pools = []

    async with aiohttp.ClientSession() as session:
        for page in range(1, max_pages + 1):
            params = {'include': 'base_token,quote_token', 'page': page}
            async with session.get(base_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    pools = data.get('data', [])
                    
                    # If there are no pools, we've reached the end
                    if not pools:
                        break
                    
                    all_pools.extend(pools)
                else:
                    print(f"Error fetching data for page {page} with status code: {response.status}")
                    break  # Stop if there's an error

    return {'data': all_pools}
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
    print(token_identifier)
    print(network)
    url = f'https://api.geckoterminal.com/api/v2/search/pools?/{token_identifier}/info'
    headers = {'Accept': 'application/json;version=20230302'}
    params = {
        'query': token_identifier,
        'network': network,
        'page': 1
    }

async def get_token_info(token_identifier, network='eth', include='include', page=1):
    print(token_identifier)
    print(network)
    url = 'https://api.geckoterminal.com/api/v2/search/pools'
    headers = {'Accept': 'application/json;version=20230302'}
    params = {
        'query': token_identifier,
        'network': network,
        'include': include,
        'page': page
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                json_response = await response.json()
                return json_response
            else:
                print("Failed to fetch data:", response.status)
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

async def get_ohlc_data(pool_address, network='eth', timeframe='hour', aggregate='4', limit='200'):
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
async def fetch_pair_data(token_identifier):
    url = f"https://api.dexscreener.com/latest/dex/search/?q={token_identifier}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()  # Return the JSON response from the API
            else:
                print(f"Failed to fetch data: {response.status}")
                return None