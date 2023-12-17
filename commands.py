
import discord
from apirequest import get_ohlc_data, get_token_info
from utils import process_ohlc_data_and_generate_chart, process_token_info
from discord.ext import commands
import textwrap

async def send_split_messages(ctx, message, char_limit=2000):
    # Split the message into chunks of 'char_limit' characters
    for chunk in textwrap.wrap(message, char_limit, replace_whitespace=False):
        await ctx.send(chunk)


@commands.command(name='token', help='Get information about a token')
async def token(ctx, token_address: str, network: str = 'eth'):
    tokeninfo = await get_token_info(token_address, network)
    if tokeninfo:
        message = await process_token_info(tokeninfo)
        await send_split_messages(ctx, message)
    else:
        await ctx.send("Error retrieving token information.")

@commands.command(name='chart', help='Generate a simple candlestick chart for a given token and interval')
async def chart(ctx, token_address: str):
    ohlc_data = await get_ohlc_data(token_address)
    if ohlc_data is not None:
        chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, 'default')
        await ctx.send(file=discord.File(chart_file))
    else:
        await ctx.send("Failed to fetch OHLC data.")

@commands.command(name='chartichi', help='Generate an Ichimoku Cloud chart for a given token and interval')
async def chartichi(ctx, token_address: str):
    ohlc_data = await get_ohlc_data(token_address)
    if ohlc_data is not None:
        chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, 'ichimoku')
        await ctx.send(file=discord.File(chart_file))
    else:
        await ctx.send("Failed to fetch OHLC data.")

@commands.command(name='chartdonchian', help='Generate a Donchian Channel chart for a given token and interval')
async def chartdonchian(ctx, token_address: str):
    ohlc_data = await get_ohlc_data(token_address)
    if ohlc_data is not None:
        chart_file = await process_ohlc_data_and_generate_chart(ohlc_data, 'donchian')
        await ctx.send(file=discord.File(chart_file))
    else:
        await ctx.send("Failed to fetch OHLC data.")
