
import discord
from apirequest import get_ohlc_data, get_token_info, get_floor_info
from utils import process_ohlc_data_and_generate_chart, send_token_info
from discord.ext import commands
import textwrap

async def send_split_messages(ctx, message, char_limit=2000):
    # Split the message into chunks of 'char_limit' characters
    for chunk in textwrap.wrap(message, char_limit, replace_whitespace=False):
        await ctx.send(chunk)
@commands.command(name='help', help='call cash plz')
async def help(ctx):
    # Customize the title, color, and optionally, a description
    embed = discord.Embed(title="Cashmontee Commands", color=0x0099ff, description="List of available commands:")

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


@commands.command(name='chart', help='Generate a simple candlestick chart for a given token and interval')
async def chart(ctx, token_address: str, interval: str = '1h', max_size: str = '100'):
    token_name, ohlc_data = await get_ohlc_data(token_address, interval, max_size)
    if ohlc_data is not None:
        chart_file = await process_ohlc_data_and_generate_chart(token_name, ohlc_data, 'default')
        await ctx.send(file=discord.File(chart_file))
    else:
        await ctx.send("Failed to fetch OHLC data.")

@commands.command(name='chartichi', help='Generate an Ichimoku Cloud chart for a given token and interval')
async def chartichi(ctx, token_address: str,  interval: str = '1h',  max_size: str = '100'):
    token_name, ohlc_data = await get_ohlc_data(token_address, interval, max_size)
    if ohlc_data is not None:
        chart_file = await process_ohlc_data_and_generate_chart(token_name, ohlc_data, 'ichimoku')
        await ctx.send(file=discord.File(chart_file))
    else:
        await ctx.send("Failed to fetch OHLC data.")

@commands.command(name='chartdonchian', help='Generate a Donchian Channel chart for a given token and interval')
async def chartdonchian(ctx, token_address: str,  interval: str = '1h',  max_size: str = '100'):
    token_name, ohlc_data = await get_ohlc_data(token_address, interval, max_size)
    if ohlc_data is not None:
        chart_file = await process_ohlc_data_and_generate_chart(token_name, ohlc_data, 'donchian')
        await ctx.send(file=discord.File(chart_file))
    else:
        await ctx.send("Failed to fetch OHLC data.")
