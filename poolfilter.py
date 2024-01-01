import requests
import pandas as pd
import time


async def fetch_and_filter_pools(newpoolinfo):
    all_pools = newpoolinfo.get('data', [])  # Safely get the 'data' list
    
    # Define your filters
    min_liquidity = 10000  # replace with your actual values
    min_fdv = 60000
    max_fdv = 20000000
    min_volume_24h = 32000
    min_volume_5m = 1400
    pair_age = 2 * 60 * 60  # 2 hours in seconds
    
    current_time = time.time()

    def filter_pool(pool):
        attributes = pool.get('attributes', {})
        liquidity = float(attributes.get('reserve_in_usd', 0))
        fdv = float(attributes.get('fdv_usd', 0))
        volume_24h = float(attributes.get('volume_usd', {}).get('h24', 0))

        # Filter conditions
        if liquidity < min_liquidity or not (min_fdv <= fdv <= max_fdv):
            return False
        created_at = time.mktime(time.strptime(attributes.get('pool_created_at'), '%Y-%m-%dT%H:%M:%SZ'))
        if current_time - created_at < pair_age:
            return False
        if volume_24h < min_volume_24h:
            return False
        return True

    # Apply the filters
    filtered_pools = [pool for pool in all_pools if filter_pool(pool)]

    # Return data in the same format as the API response
    return {'data': filtered_pools}
