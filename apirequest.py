import aiohttp
import datetime
import asyncio
import os
import discord
import requests


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
            buy_now_price = stats.get("buyNowPrice", "N/A")
            floor_1h = stats.get("floor1h", "N/A")
            floor_24h = stats.get("floor24h", "N/A")
            # ... [access other stats similarly]

            embed = discord.Embed(title=f"{slugdisplay}", color=0x0099ff)
            embed.add_field(name="Buy Now Price", value=f"{buy_now_price}", inline=False)
            embed.add_field(name="Floor Change 24h", value=f"{floor_24h}", inline=False)
            embed.add_field(name="Floor Change 1h", value=f"{floor_1h}", inline=False)
            await ctx.send(embed=embed)
    
async def get_token_info(token_address, network='eth'):
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


async def get_ohlc_data(token_address, interval, max_size):
    url = 'https://api.syve.ai/v1/price/historical/ohlc'
    token_data = await get_token_info(token_address)
    token_name = token_data['attributes']['name']  # Adjust according to the actual structure of token_data
    # Setting default values for other parameters
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
                    ohlc_data = await response.json()
                    # Include token_name in the data returned
                    return ohlc_data, token_name
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