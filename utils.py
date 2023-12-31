import pandas as pd
import mplfinance as mpf
import discord


def calculate_ichimoku(df):
    # Calculate Ichimoku Cloud components
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['Tenkan-sen'] = (high_9 + low_9) / 2

    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['Kijun-sen'] = (high_26 + low_26) / 2

    df['Senkou_Span_A'] = (df['Tenkan-sen'] + df['Kijun-sen']) / 2

    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['Senkou_Span_B'] = (high_52 + low_52) / 2

    df['Chikou_Span'] = df['Close'].shift(periods=-26)

    return df
def create_custom_style():
    # Define market colors for up and down candles
    mc = mpf.make_marketcolors(
        up='lightgreen', down='lightcoral',
        edge='inherit', wick='inherit',
        volume='in', ohlc='i'
    )

    # Create a custom style
    s = mpf.make_mpf_style(
        marketcolors=mc, 
        facecolor='black',  # Background color of the chart
        figcolor='white',   # Color of the area around the chart
        gridcolor='black',   # Grid color (set to 'black' or '' to hide)
    )
    return s
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

async def send_token_info(ctx, tokeninfo):
    processed_data = await process_token_info(tokeninfo)

    # Create an embed for the message
    embed = discord.Embed(title=processed_data["Pool Name"], color=0x0099ff)  # Customize the title and color

    # Add fields to the embed
    embed.add_field(name="Pool Address", value=processed_data["Pool Address"], inline=False)
    embed.add_field(name="Base Token Price USD", value=processed_data["Base Token Price USD"], inline=True)
    embed.add_field(name="Quote Token Price USD", value=processed_data["Quote Token Price USD"], inline=True)
    embed.add_field(name="Fully Diluted Valuation (USD)", value=processed_data["Fully Diluted Valuation (USD)"], inline=False)
    embed.add_field(name="Market Cap (USD)", value=processed_data["Market Cap (USD)"], inline=True)
    embed.add_field(name="1H Price Change Percentage", value=processed_data["1H Price Change Percentage"], inline=True)
    embed.add_field(name="24H Price Change Percentage", value=processed_data["24H Price Change Percentage"], inline=False)
    embed.add_field(name="1H Volume (USD)", value=processed_data["1H Volume (USD)"], inline=True)
    embed.add_field(name="24H Volume (USD)", value=processed_data["24H Volume (USD)"], inline=True)
    embed.add_field(name="Reserve in USD", value=processed_data["Reserve in USD"], inline=False)
    embed.add_field(name="Base Token ID", value=processed_data["Base Token ID"], inline=True)
    embed.add_field(name="Quote Token ID", value=processed_data["Quote Token ID"], inline=True)
    embed.add_field(name="DEX ID", value=processed_data["DEX ID"], inline=False)

    await ctx.send(embed=embed)
def get_token_name(token_data):
    # Check if 'data' is in the response and it has at least one item
    if 'data' in token_data and len(token_data['data']) > 0:
        # Get the 'name' attribute from the first item's 'attributes'
        token_name = token_data['data'][0]['attributes'].get('name', 'N/A')
    else:
        token_name = 'Unknown Token'  # Default name if 'data' is empty or not present

    return token_name

def process_top_pools(toppoolinfo, ctx):
    # Assuming toppoolinfo is a dictionary containing the 'data' key with relevant information
    df_top_pools = pd.json_normalize(toppoolinfo['data']).head(10)

    for index, pool_info in df_top_pools.iterrows():
        pool_address = pool_info['id'].split('_')[1]  # Extract pool address from the id
        # Construct the message
        message = (
            f"Pool Name: {pool_info.get('attributes.name', 'N/A')}\n"
            f"Pool Address: {pool_address}\n"
            f"Base Token Price USD: {format_currency(pool_info.get('attributes.base_token_price_usd'))}\n"
            f"Quote Token Price USD: {format_currency(pool_info.get('attributes.quote_token_price_usd'))}\n"
            f"Fully Diluted Valuation (USD): {format_currency(pool_info.get('attributes.fdv_usd'))}\n"
            f"Market Cap (USD): {format_currency(pool_info.get('attributes.market_cap_usd'))}\n"
            f"1H Price Change Percentage: {format_percentage(pool_info.get('attributes.price_change_percentage.h1'))}\n"
            f"24H Price Change Percentage: {format_percentage(pool_info.get('attributes.price_change_percentage.h24'))}\n"
            f"1H Volume (USD): {format_currency(pool_info.get('attributes.volume_usd.h1'))}\n"
            f"24H Volume (USD): {format_currency(pool_info.get('attributes.volume_usd.h24'))}\n"
            f"Reserve in USD: {format_currency(pool_info.get('attributes.reserve_in_usd'))}\n"
            f"Base Token ID: {pool_info.get('relationships.base_token.data.id', 'N/A')}\n"
            f"Quote Token ID: {pool_info.get('relationships.quote_token.data.id', 'N/A')}\n"
            f"DEX ID: {pool_info.get('relationships.dex.data.id', 'N/A')}\n"
        )

        # Send message or add to an embed, depending on your use case
        return processed_data
async def send_top_pools_info(ctx, toppoolinfo):
    # Assuming toppoolinfo is a list of pools
    for pool_info in toppoolinfo[:10]:  # Process only the first 10 pools
        processed_data = await process_top_pools(pool_info)

        # Create an embed for the message
        embed = discord.Embed(title=processed_data["Pool Name"], color=0x0099ff)  # Customize the title and color

        # Add fields to the embed
        embed.add_field(name="Pool Name", value=processed_data["Pool Name"], inline=False)
        embed.add_field(name="Pool Address", value=processed_data["Pool Address"], inline=False)
        embed.add_field(name="Price", value=processed_data["Pool Address"], inline=False)
        embed.add_field(name="FDV", value=processed_data["Pool Address"], inline=False)
        embed.add_field(name="DEX", value=processed_data["Pool Address"], inline=False)
        embed.add_field(name="Volume 1h", value=processed_data["Pool Address"], inline=False)
        embed.add_field(name="Volume 24h", value=processed_data["Pool Address"], inline=False)
        # Add other fields as required

        await ctx.send(embed=embed)
def get_token_name_and_pool(tokeninfo):
    # Check if 'data' is in the response and it has at least one item
    if 'data' in tokeninfo and len(tokeninfo['data']) > 0:
        # Get the 'name' attribute from the first item's 'attributes'
        token_name = tokeninfo['data'][0]['attributes'].get('name', 'N/A')
        token_pool = tokeninfo['data'][0]['attributes'].get('address', 'N/A')    
        print(token_name, token_pool)    
    else:
        token_name = 'Unknown Token'  # Default name if 'data' is empty or not present

    return token_name, token_pool
async def process_token_info(tokeninfo):
    df_pools = pd.json_normalize(tokeninfo['data'])
    pools_data = df_pools.set_index(df_pools['id'].apply(lambda x: x.split('_')[1])).to_dict('index')
    
    pool_address, pool_info = next(iter(pools_data.items()))

    data_to_display = {
        "Pool Name": pool_info.get('attributes.name', 'N/A'),
        "Pool Address": pool_address,
        "Base Token Price USD": format_currency(pool_info.get('attributes.base_token_price_usd')),
        "Quote Token Price USD": format_currency(pool_info.get('attributes.quote_token_price_usd')),
        "Fully Diluted Valuation (USD)": format_currency(pool_info.get('attributes.fdv_usd')),
        "Market Cap (USD)": format_currency(pool_info.get('attributes.market_cap_usd')),
        "1H Price Change Percentage": format_percentage(pool_info.get('attributes.price_change_percentage.h1')),
        "24H Price Change Percentage": format_percentage(pool_info.get('attributes.price_change_percentage.h24')),
        "1H Volume (USD)": format_currency(pool_info.get('attributes.volume_usd.h1')),
        "24H Volume (USD)": format_currency(pool_info.get('attributes.volume_usd.h24')),
        "Reserve in USD": format_currency(pool_info.get('attributes.reserve_in_usd')),
        "Base Token ID": pool_info.get('relationships.base_token.data.id', 'N/A'),
        "Quote Token ID": pool_info.get('relationships.quote_token.data.id', 'N/A'),
        "DEX ID": pool_info.get('relationships.dex.data.id', 'N/A')
    }

    return data_to_display
async def convert_block_to_timeframe(block_number):
    # Placeholder for the function that converts block numbers to human-readable timeframes
    # Implement the logic based on your blockchain data
    return "Human-readable Timeframe"
async def process_wallet(walletinfo, wallet_address, ctx):
    # Convert the list of dictionaries (walletinfo) to a DataFrame
    df_wallet = pd.json_normalize(walletinfo)

    # Sort by 'timestamp.last_trade' in descending order and take the top 10
    df_wallet = df_wallet.sort_values(by='timestamp.last_trade', ascending=False).head(10)

    # Now create the Discord embed
    embed = discord.Embed(title=f"Recent Trades: {wallet_address}", color=0x00ff00)

    for _, row in df_wallet.iterrows():
        token_address = row['token_address']
        token_symbol = row['token_symbol']
        first_trade_block = row['timestamp.first_trade']
        last_trade_block = row['timestamp.last_trade']
        profit = row['total.profit']

        embed.add_field(
            name=f"Token: {token_symbol}",
            value=(f"Token Address: {token_address}\n"
                   f"Block of First Trade: {first_trade_block}\n"
                   f"Block of Last Trade: {last_trade_block}\n"
                   f"Total Profit (USD): ${float(profit):,.2f}\n"),
            inline=False
        )

    await ctx.send(embed=embed)
async def process_trades(trade_data, token_name, token_pool, ctx):
    # Load into a DataFrame
    df = pd.json_normalize(trade_data['data'])

    # Sort by 'volume_in_usd' in descending order and take the top 10
    df = df.sort_values(by='attributes.volume_in_usd', ascending=False).head(10)

    # Now create the Discord embed
    embed = discord.Embed(title="Recent Trades", color=0x00ff00)

    for index, row in df.iterrows():
        kind = row['attributes.kind']
        volume_in_usd = row['attributes.volume_in_usd']
        block_number = row['attributes.block_number']
        wallet = row['attributes.tx_from_address']

        embed.add_field(
            name=f"Trader {wallet}",
            value=(f"Token: {token_name}\n"
                   f"Kind: {kind.capitalize()}\n"
                   f"Volume (USD): ${float(volume_in_usd):,.2f}\n"
                   f"Time: {block_number}"),
            inline=False
        )

    await ctx.send(embed=embed)
async def process_ohlc_data_and_generate_chart(ohlc_data, token_name, chart_type):
    df = pd.DataFrame(ohlc_data['data'])
    df['date_open'] = pd.to_datetime(df['date_open'])
    df.set_index('date_open', inplace=True)
    df.sort_index(ascending=True, inplace=True)
    # Renaming columns to match mplfinance requirements
    df.rename(columns={
        'price_open': 'Open',
        'price_high': 'High',
        'price_low': 'Low',
        'price_close': 'Close',
        'volume_1h_usd': 'Volume'
    }, inplace=True)

    Q1_high = df['High'].quantile(0.25)
    Q3_high = df['High'].quantile(0.75)
    IQR_high = Q3_high - Q1_high

    Q1_low = df['Low'].quantile(0.25)
    Q3_low = df['Low'].quantile(0.75)
    IQR_low = Q3_low - Q1_low

    upper_bound_high = Q3_high + 1.5 * IQR_high
    lower_bound_low = Q1_low - 1.5 * IQR_low

    df_filtered = df[(df['High'] <= upper_bound_high) & (df['Low'] >= lower_bound_low)]

    custom_style = create_custom_style()
    

    if chart_type == 'ichimoku':
        # Calculate the Ichimoku Cloud on the data
        df_filtered = calculate_ichimoku(df)
        ichimoku_plots = [
            mpf.make_addplot(df_filtered['Tenkan-sen'], color='#00FFFF'),  # Cyan for Tenkan-sen
            mpf.make_addplot(df_filtered['Kijun-sen'], color='#FF00FF'),   # Magenta for Kijun-sen
            mpf.make_addplot(df_filtered['Senkou_Span_A'], color='#00FF00', alpha=0.5),  # Light green for Senkou Span A
            mpf.make_addplot(df_filtered['Senkou_Span_B'], color='#FFA500', alpha=0.5),  # Bright orange for Senkou Span B
            mpf.make_addplot(df_filtered['Chikou_Span'], color='#ADD8E6')  # Light blue for Chikou Span
        ]

        # Fill between Senkou Span A and B
        ichimoku_fill_up = dict(y1=df_filtered['Senkou_Span_A'].values, y2=df_filtered['Senkou_Span_B'].values,
                                where=df_filtered['Senkou_Span_A'] >= df_filtered['Senkou_Span_B'], alpha=0.5, color='#a6f7a6')
        ichimoku_fill_down = dict(y1=df_filtered['Senkou_Span_A'].values, y2=df_filtered['Senkou_Span_B'].values,
                                where=df_filtered['Senkou_Span_A'] < df_filtered['Senkou_Span_B'], alpha=0.5, color='#CD5555')

        title = f'Chart for {token_name}'
        mpf.plot(
            df_filtered,
            title=title,
            type='candle',
            style=custom_style,
            volume=True,
            addplot=ichimoku_plots,
            fill_between=[ichimoku_fill_up, ichimoku_fill_down],
            savefig='ichimoku_chart.png'
        )
        return 'ichimoku_chart.png'

    elif chart_type == 'donchian':
        # Calculate Donchian Channels
        period = 10
        df_filtered['Upper'] = df_filtered['High'].rolling(period).max()
        df_filtered['Lower'] = df_filtered['Low'].rolling(period).min()
        df_filtered['Middle'] = (df_filtered['Upper'] + df_filtered['Lower']) / 2

        # Donchian Channel plots
        donchian_plots = [
            mpf.make_addplot(df_filtered['Upper'], color='#2962FF'),
            mpf.make_addplot(df_filtered['Middle'], color='#FF6D00'),
            mpf.make_addplot(df_filtered['Lower'], color='#2962FF'),
        ]

        # Prepare the fill_between parameters for Donchian Channels
        donchian_fill = {
            'y1': df_filtered['Upper'].values,
            'y2': df_filtered['Lower'].values,
            'alpha': 0.1,
            'color': '#2962FF'
        }
        title = f'Chart for {token_name}'
        mpf.plot(
            df_filtered,
            title=title,
            type='candle',
            style=custom_style,
            volume=True,
            addplot=donchian_plots,
            fill_between=donchian_fill,
            savefig='donchian_chart.png'
        )
        return 'donchian_chart.png'
    else:
        title = f'Chart for {token_name}'
        # Default candlestick plot
        mpf.plot(
            df_filtered,
            title=title,
            mav=(13,25),
            type='candle',
            style=custom_style,
            volume=True,
            savefig='default_chart.png'
        )
        return 'default_chart.png'