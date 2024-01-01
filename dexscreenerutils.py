import discord
def format_currency(value):
    try:
        return "${:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "N/A"

def format_percentage(value):
    try:
        return "{:.2f}%".format(float(value))
    except (ValueError, TypeError):
        return "N/A"
def process_dexscreener_pool(pool_data):
    # Extract the base token name and address
    quote_token = pool_data.get('quoteToken', {})
    quote_token_name = quote_token.get('symbol', 'N/A')
    base_token = pool_data.get('baseToken', {})
    base_token_name = base_token.get('name', 'N/A')
    base_token_address = base_token.get('address', 'N/A')
    base_token_str = f"{base_token_name} ({base_token_address})"
    quote_token_str = f"{quote_token_name}"
    # Extract other required fields
    price_usd = format_currency(pool_data.get('priceUsd', 'N/A'))
    volume_h1 = format_currency(pool_data.get('volume', {}).get('h1', 'N/A'))
    price_change_h1 = format_percentage(pool_data.get('priceChange', {}).get('h1', 'N/A'))
    price_change_h24 = format_percentage(pool_data.get('priceChange', {}).get('h24', 'N/A'))
    liquidity_usd = format_currency(pool_data.get('liquidity', {}).get('usd', 'N/A'))
    fdv = format_currency(pool_data.get('fdv', 'N/A'))

    processed_data = {
        "Quote Token/Network": quote_token_str,
        "Base Token": base_token_str,
        "Price USD": price_usd,
        "1H Volume": volume_h1,
        "1H Price Change": price_change_h1,
        "24H Price Change": price_change_h24,
        "Liquidity (USD)": liquidity_usd,
        "Fully Diluted Valuation (USD)": fdv
    }
    return processed_data


async def send_dexscreener_token_info(ctx, processed_data):
    embed = discord.Embed(title=processed_data["Base Token"], color=0x0099ff)
    for key, value in processed_data.items():
        value = str(value)[:1024] if value else 'N/A'
        embed.add_field(name=key, value=value, inline=False)

    await ctx.send(embed=embed)