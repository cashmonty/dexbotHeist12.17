
import discord
from apirequest import get_ohlc_data, get_token_info, get_floor_info, get_trade_info
from utils import get_token_name_and_pool, process_ohlc_data_and_generate_chart, process_trades, send_token_info, get_token_name
from discord.ext import commands
import textwrap

async def send_split_messages(ctx, message, char_limit=2000):
    # Split the message into chunks of 'char_limit' characters
    for chunk in textwrap.wrap(message, char_limit, replace_whitespace=False):
        await ctx.send(chunk)
@commands.command(name='help', help='call cash plz')
async def help(ctx):
    # Customize the title, color, and optionally, a description
    embed = discord.Embed(title="**Cashmontee Commands**", color=0x0099ff, description="List of available commands:")

    # Adding fields for each command
    embed.add_field(name="**Token Command**", value="`/token <contract address> [network]`\nDefault `[network]` is ETH.", inline=False)
    embed.add_field(name="**Chart Command**", value="`/chart <contract address> [timeframe] [amount of candles]`\nDefaults to 1h and 100 candles if 1 argument provided.", inline=False)
    embed.add_field(name="**Chart Command with Indicators**", value="Indicators:\n`/chartichi` (same as `/chart`)\n`/chartdonchian` (same as `/chart`)", inline=False)

    # Sending the embed
    await ctx.send(embed=embed)
@commands.command(name='floor', help='the floor price yo')
async def floor(ctx, slugdisplay):
    await get_floor_info(ctx, slugdisplay)
@commands.command(name='token', help='Get information about a specific token')
async def token(ctx, token_address, network:str = 'eth'):
    tokeninfo = await get_token_info(token_address, network)  # Fetch token info

    if tokeninfo is not None:
        await send_token_info(ctx, tokeninfo)  # Send formatted token info
    else:
        await ctx.send("Error retrieving token information.")
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
        await ctx.send("Error retrieving token information.")


@commands.command(name='chart', help='Generate a simple candlestick chart for a given token and interval')
async def chart(ctx, token_address: str, interval: str = '1h', max_size: str = '100'):
    try:
        token_data = await get_token_info(token_address, network='eth')
        ohlc_data = await get_ohlc_data(token_address, interval, max_size)
        
        if ohlc_data is not None:
            token_name = get_token_name(token_data)  # Removed await
            chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, token_name, 'default')
            await ctx.send(file=discord.File(chart_file))
        else:
            await ctx.send("Failed to fetch OHLC data.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@commands.command(name='chartichi', help='Generate a simple candlestick chart for a given token and interval')
async def chartichi(ctx, token_address: str, interval: str = '1h', max_size: str = '100'):
    try:
        token_data = await get_token_info(token_address, network='eth')
        ohlc_data = await get_ohlc_data(token_address, interval, max_size)
        
        if ohlc_data is not None:
            token_name = get_token_name(token_data)  # Removed await
            chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, token_name, 'ichimoku')
            await ctx.send(file=discord.File(chart_file))
        else:
            await ctx.send("Failed to fetch OHLC data.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@commands.command(name='chartdonchian', help='Generate a simple candlestick chart for a given token and interval')
async def chartdonchian(ctx, token_address: str, interval: str = '1h', max_size: str = '100'):
    try:
        token_data = await get_token_info(token_address, network='eth')
        ohlc_data = await get_ohlc_data(token_address, interval, max_size)
        
        if ohlc_data is not None:
            token_name = get_token_name(token_data)  # Removed await
            chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, token_name, 'donchian')
            await ctx.send(file=discord.File(chart_file))
        else:
            await ctx.send("Failed to fetch OHLC data.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")