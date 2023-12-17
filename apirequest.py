import aiohttp
import datetime
import asyncio
import os
import requests

API_KEY = os.getenv('SYVE_API_KEY')
def get_floor_info(slugdisplay):
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

    variables = {
        "slugsDisplay": slugdisplay
    }

    headers = {
        'Content-Type': 'application/json',
        'X-TENSOR-API-KEY': api_key
    }
        

    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})

    if response.status_code == 200:
        data = response.json()
        all_collections = data.get("data", {}).get("allCollections", {}).get("collections", [])
        
        for collection in all_collections:
            stats = collection.get("statsV2", {})
            buy_now_price = stats.get("buyNowPrice", "N/A")
            floor_1h = stats.get("floor1h", "N/A")
            floor_24h = stats.get("floor24h", "N/A")
            # ... [access other stats similarly]

            # Format and send a message for each collection
            stats_message = f"Data for collection {slugdisplay}: Buy Now Price: {buy_now_price}, Floor 1h: {floor_1h}, Floor 24h: {floor_24h}"
            return stats_message
    
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


async def get_ohlc_data(token_address, interval, max_size):
    url = 'https://api.syve.ai/v1/price/historical/ohlc'

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