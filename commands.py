
import discord
from poolfilter import fetch_and_filter_pools
from dexscreenerutils import process_dexscreener_pool, send_dexscreener_token_info
from apirequest import get_ohlc_data, get_token_info, get_floor_info, get_top_pools, get_trade_info, get_wallet_info, get_cat_pools, fetch_pair_data
from utils import get_token_name_and_pool, process_ohlc_data_and_generate_chart, process_trades, send_token_info, get_token_name, process_wallet, send_top_pools_info
from discord.ext import commands
import textwrap

async def send_split_messages(ctx, message, char_limit=2000):
    # Split the message into chunks of 'char_limit' characters
    for chunk in textwrap.wrap(message, char_limit, replace_whitespace=False):
        await ctx.send(chunk)

@commands.command(name='dexbot', help='call cash plz')
async def dexbot(ctx):


    # Ensure these files exist in your bot's working directory
    commands_file1 = 'commandshelp1.png'
    commands_file2 = 'commandshelp2.png'

    # Send the PNG files
    await ctx.send(file=discord.File(commands_file1))
    await ctx.send(file=discord.File(commands_file2))

@commands.command(name='floor', help='the floor price yo')
async def floor(ctx, slugdisplay):
    await get_floor_info(ctx, slugdisplay)

@commands.command(name='token', help='Get information about a specific token')
async def token(ctx, token_identifier, network='eth'):
    toppoolinfo = await get_token_info(token_identifier, network)

    if toppoolinfo is not None:
        await send_token_info(ctx, toppoolinfo)
    else:
        await ctx.send("Error retrieving token info. Make sure in your command you format it as /token (name or address) (network). Default network is Eth.")
@commands.command(name='toppools', help='Get information about a specific wallet')
async def toppools(ctx, network='eth'):
    toppoolinfo = await get_top_pools(network)  # Fetch token info

    if toppoolinfo is not None:
        await send_top_pools_info(ctx, toppoolinfo)
    else:
        await ctx.send("Error retrieving token information. Default network is Eth, if you would like different type /toppools (network). if Gecko Terminal has it available it will be printed out")
@commands.command(name='wallet', help='Get information about a specific wallet')
async def wallet(ctx, wallet_address):
    walletinfo = await get_wallet_info(wallet_address)  # Fetch token info

    if walletinfo is not None:
        await process_wallet(walletinfo, wallet_address, ctx)  # Send formatted token info
    else:
        await ctx.send("Only for Ethereum wallets - provides the last 10 trades of the wallet.")
@commands.command(name='trades', help='Get information about a specific token')
async def trades(ctx, token_address, network='eth', trade_volume_in_usd_greater_than='2000'):
    tokeninfo = await get_token_info(token_address, network)
    if tokeninfo:
        token_name, token_pool = get_token_name_and_pool(tokeninfo)
        trade_data= await get_trade_info(token_pool, trade_volume_in_usd_greater_than, network)
        if trade_data:
            await process_trades(trade_data, token_name, token_pool, ctx)
        else:
            await ctx.send("Error retrieving trade information.")
    else:
        await ctx.send("Error retrieving trade information. For /trades (token address) you can add (network) to specify the trades on a specific non-Eth coin. Additionally, /trades (token address) (network) (trade volume you want to search for (last 24h))")


@commands.command(name='chart', help='Generate a simple candlestick chart for a given token and interval')
async def chart(ctx, token_address: str, network: str = 'eth', timeframe: str = 'hour', aggregate='1', limit: str = '200'):
    try:

        token_data = await get_token_info(token_address, network)
        data = token_data['data'][0]
        attributes = data.get('attributes', {})
        token_name = attributes.get('name', 'N/A')
        best_pool_address = data.get('id', 'N/A')
        ohlc_data = await get_ohlc_data(best_pool_address, network, timeframe, aggregate, limit)
        print(token_name)
        print(best_pool_address)        
        if ohlc_data is not None:
            chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, token_name, 'default')
            await ctx.send(file=discord.File(chart_file))
        else:
            await ctx.send("Failed to fetch OHLC data.")
    except Exception as e:
        await ctx.send("An error occurred. Arguments for /chart are `/chart (token address or symbol) (network(default=eth) (timeframe(minute, hour, day)) (per candle # (example: 1 would be 1h when combined with minute, hour, or day)) (number of candles) -- you can add these extra arguments but default is 1h and 200 candles")



@commands.command(name='chartichi', help='Generate a simple candlestick chart for a given token and interval')
async def chartichi(ctx, token_address: str, network: str = 'eth', timeframe: str = 'hour', aggregate='1', limit: str = '200'):
    try:
        token_data = await get_token_info(token_address, network)
        data = token_data['data'][0]
        attributes = data.get('attributes', {})
        token_name = attributes.get('name', 'N/A')
        best_pool_address = data.get('id', 'N/A')
        ohlc_data = await get_ohlc_data(best_pool_address, network, timeframe, aggregate, limit)
        print(token_name)
        print(best_pool_address)        
        if ohlc_data is not None:
            chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, token_name, 'ichimoku')
            await ctx.send(file=discord.File(chart_file))
        else:
            await ctx.send("Failed to fetch OHLC data.")
    except Exception as e:
        await ctx.send("An error occurred. Arguments for /chartichimoku or /chartdonchian are `(token address or symbol) (network(default=eth) (timeframe(minute, hour, day)) (per candle # (example: 1 would be 1h when combined with minute, hour, or day)) (number of candles) -- you can add these extra arguments but default is 1h and 200 candles")

@commands.command(name='chartdonchian', help='Generate a simple candlestick chart for a given token and interval')
async def chartdonchian(ctx, token_address: str, network: str = 'eth', timeframe: str = 'hour', aggregate='1', limit: str = '200'):
    try:
        token_data = await get_token_info(token_address, network)
        data = token_data['data'][0]
        attributes = data.get('attributes', {})
        token_name = attributes.get('name', 'N/A')
        best_pool_address = data.get('id', 'N/A')
        ohlc_data = await get_ohlc_data(best_pool_address, network, timeframe, aggregate, limit)
        print(token_name)
        print(best_pool_address)        
        if ohlc_data is not None:
            chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, token_name, 'donchian')
            await ctx.send(file=discord.File(chart_file))
        else:
            await ctx.send("Failed to fetch OHLC data.")
    except Exception as e:
        await ctx.send("An error occurred. Arguments for /chartichimoku or /chartdonchian are `(token address or symbol) (network(default=eth) (timeframe(minute, hour, day)) (per candle # (example: 1 would be 1h when combined with minute, hour, or day)) (number of candles) -- you can add these extra arguments but default is 1h and 200 candles")
@commands.command(name='chartfib', help='Generate a candlestick chart with Fibonacci retracement levels for a given token and interval')
async def chartfib(ctx, token_address: str, network: str = 'eth', timeframe: str = 'hour', aggregate='1', limit: str = '200'):
    try:
        # Fetch token data
        token_data = await get_token_info(token_address, network)
        data = token_data['data'][0]
        attributes = data.get('attributes', {})
        token_name = attributes.get('name', 'N/A')
        best_pool_address = data.get('id', 'N/A')
        print(token_name)
        print(best_pool_address)
        ohlc_data = await get_ohlc_data(best_pool_address, network, timeframe, aggregate, limit)
        
        if ohlc_data is not None:

            chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, token_name, 'fibonacci')
            
            # Send the chart as a file in the Discord message
            await ctx.send(file=discord.File(chart_file))
        else:
            await ctx.send("Failed to fetch OHLC data.")
    except Exception as e:
        await ctx.send("An error occurred. Arguments for /chartichimoku or /chartdonchian are `(token address or symbol) (network(default=eth) (timeframe(minute, hour, day)) (per candle # (example: 1 would be 1h when combined with minute, hour, or day)) (number of candles) -- you can add these extra arguments but default is 1h and 200 candles")
@commands.command(name='catfilter', help='Get information about the latest pools on a specific network')
async def catfilter(ctx, network='eth'):
    try:
        newpoolinfo = await get_cat_pools(network)
        toppoolinfo = await fetch_and_filter_pools(newpoolinfo)  # Now asynchronous

        if toppoolinfo is not None:
            # Pass ctx to send_top_pools_info
            await send_top_pools_info(ctx, toppoolinfo)
        else:
            await ctx.send("No pools found that match the criteria or error retrieving pool information.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
from discord.ext import commands

@commands.command(name='dexscreener', help='Get DexScreener information for a specific token')
async def dexscreener(ctx, token_identifier):
    try:
        pair_data = await fetch_pair_data(token_identifier)

        # Check if there's data and it contains 'pairs'
        if pair_data and 'pairs' in pair_data and len(pair_data['pairs']) > 0:
            # Process only the first pair
            first_pair = pair_data['pairs'][0]
            processed_data = process_dexscreener_pool(first_pair)
            await send_dexscreener_token_info(ctx, processed_data)
        else:
            await ctx.send(f"No data found for {token_identifier}.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
