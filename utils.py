import pandas as pd
import mplfinance as mpf
import discord
import matplotlib.pyplot as plt


def create_custom_style():
    # Define market colors for up and down candles
    mc = mpf.make_marketcolors(
        up='lightgreen', down='lightcoral',
        edge='inherit', wick='inherit',
        volume='in', ohlc='i'
    )
    # Get the base style of 'nightclouds'
    base_style = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc, gridcolor='white')



    return base_style
def add_fibonacci_retracement_levels(ax, high, low):
    # Initialize Fibonacci levels
    fib_levels = {}
    if high > low:
        # Calculate Fibonacci retracement levels based on the swing high and low
        fib_levels['23.6%'] = high - (high - low) * 0.236
        fib_levels['38.2%'] = high - (high - low) * 0.382
        fib_levels['50.0%'] = high - (high - low) * 0.5
        fib_levels['61.8%'] = high - (high - low) * 0.618
        fib_levels['100.0%'] = low
    else:
        # Calculate Fibonacci extension levels
        fib_levels['61.8%'] = low + (high - low) * 0.618
        fib_levels['100.0%'] = high
        fib_levels['138.2%'] = low + (high - low) * 1.382
        fib_levels['161.8%'] = low + (high - low) * 1.618
        fib_levels['200.0%'] = low + (high - low) * 2.0

    # Define colors for each level - this needs to be adjusted as per your preference
    fib_colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow']

    # Plot each Fibonacci level with its color as a solid line and add the price text
    for (level, price), color in zip(fib_levels.items(), fib_colors):
        ax.axhline(y=price, color=color, linestyle='-', linewidth=2, alpha=0.7)
        # Position the text on the right, indicating the Fibonacci level and price
        ax.text(0.98, price, f'{level} ({price:.2f})', 
                verticalalignment='center', horizontalalignment='right', 
                color=color, alpha=0.9, transform=ax.get_yaxis_transform())

    return ax


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

async def send_token_info(ctx, toppoolinfo):
    if 'data' not in toppoolinfo or not toppoolinfo['data']:
        await ctx.send("No pool data available.")
        return

    # Accessing only the first pool's data
    first_pool_data = toppoolinfo['data'][0]
    processed_data = process_top_pools(first_pool_data)

    # Create an embed for the first pool
    embed = discord.Embed(title=processed_data["Token Name"], color=0x0099ff)
    for key, value in processed_data.items():
        value = str(value)[:1024] if value else 'N/A'
        embed.add_field(name=key, value=value, inline=False)

    # Send the embed for the first pool
    await ctx.send(embed=embed)

def process_top_pools(pool_data):
    attributes = pool_data.get('attributes', {})
    token_name = attributes.get('name', 'N/A')

    processed_data = {
        "Token Name": token_name,
        "Token Address": pool_data.get('id'),
        "Base Token Price USD": attributes.get('base_token_price_usd'),
        "Fully Diluted Valuation (USD)": format_currency(attributes.get('fdv_usd')),
        "1H Price Change Percentage": format_percentage(attributes.get('price_change_percentage', {}).get('h1'))
    }
    return processed_data

# Ensure that format_currency and format_percentage functions are defined here.
def get_token_name(token_data):
    # Check if 'data' is in the response and it has at least one item
    if 'data' in token_data and len(token_data['data']) > 0:
        # Get the 'name' attribute from the first item's 'attributes'
        token_name = token_data['data'][0]['attributes'].get('name', 'N/A')
        
    else:
        token_name = 'Unknown Token'  # Default name if 'data' is empty or not present

    return token_name

async def send_dexscreener_token_info(ctx, toppoolinfo):


    # Initialize an empty list to hold all embeds
    embeds = []

    # Process only the first 10 pools
    for pool_info in toppoolinfo['data'][:10]:
        processed_data = process_top_pools(pool_info)

        # Create an embed for the pool
        embed = discord.Embed(title=processed_data["Token Name"], color=0x0099ff)
        for key, value in processed_data.items():
            # Ensure value is a string and not too long for an embed field
            value = str(value)[:1024] if value else 'N/A'
            embed.add_field(name=key, value=value, inline=False)

        # Add the completed embed for this pool to the list
        embeds.append(embed)

    # Send all embeds in one message
    await ctx.send(embeds=embeds)
async def send_top_pools_info(ctx, toppoolinfo):
    if 'data' not in toppoolinfo or not toppoolinfo['data']:
        await ctx.send("No pool data available.")
        return

    # Initialize an empty list to hold all embeds
    embeds = []

    # Process only the first 10 pools
    for pool_info in toppoolinfo['data'][:10]:
        processed_data = process_top_pools(pool_info)

        # Create an embed for the pool
        embed = discord.Embed(title=processed_data["Token Name"], color=0x0099ff)
        for key, value in processed_data.items():
            # Ensure value is a string and not too long for an embed field
            value = str(value)[:1024] if value else 'N/A'
            embed.add_field(name=key, value=value, inline=False)

        # Add the completed embed for this pool to the list
        embeds.append(embed)

    # Send all embeds in one message
    await ctx.send(embeds=embeds)

def get_token_name_and_pool(token_data):
    # Check if 'data' is in the response and it has at least one item
    if 'data' in token_data and len(token_data['data']) > 0:
        # Get the 'name' attribute from the first item's 'attributes'
        token_name = token_data['data'][0]['attributes'].get('name', 'N/A')
        pool_address = token_data['data'][0]['attributes'].get('address', 'N/A')    
        print(token_name, pool_address)    
    else:
        token_name = 'Unknown Token'  # Default name if 'data' is empty or not present

    return token_name, pool_address
async def process_token_info(pool_info):
    attributes = pool_info.get('attributes', {})
    relationships = pool_info.get('relationships', {})
    # Correctly extracting the 'name' from the 'attributes' dictionary
    token_name = attributes.get('name', 'N/A')

    data_to_display = {
        "Token Name": token_name,
        "Token Address": pool_info.get('id'),
        "Base Token Price USD": pool_info.get('base_token_price_usd'),
        "Quote Token Price USD": format_currency(pool_info.get('quote_token_price_usd')),
        "Fully Diluted Valuation (USD)": format_currency(pool_info.get('fdv_usd')),
        "Market Cap (USD)": format_currency(pool_info.get('market_cap_usd')),
        "1H Price Change Percentage": format_percentage(pool_info.get('price_change_percentage.h1')),
        "24H Price Change Percentage": format_percentage(pool_info.get('price_change_percentage.h24')),
        "1H Volume (USD)": format_currency(pool_info.get('volume_usd.h1')),
        "24H Volume (USD)": format_currency(pool_info.get('volume_usd.h24')),
        "Reserve in USD": format_currency(pool_info.get('reserve_in_usd')),
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
    # Extract OHLCV data
    ohlcv_list = ohlc_data['data']['attributes']['ohlcv_list']
    
    # Create DataFrame
    df = pd.DataFrame(ohlcv_list, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')  # assuming the timestamp is in seconds
    df.set_index('Timestamp', inplace=True)

    df.sort_index(ascending=True, inplace=True)

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
    
    if chart_type == 'fibonacci':
        high_price = df_filtered['High'].max()
        low_price = df_filtered['Low'].min()
        recent_close_price = df_filtered['Close'].iloc[-1]  # Gets the most recent closing price
        title = f'Chart for {token_name}'

        # Plot the initial chart and get the Axes object (or list of objects)
        fig, ax = mpf.plot(df_filtered, type='candle', style=custom_style, title=title, volume=True, returnfig=True)

        # Ensure ax is the primary Axes object, not a list
        primary_ax = ax[0] if isinstance(ax, list) else ax

        # Add Fibonacci retracement levels and annotations to the primary Axes
        add_fibonacci_retracement_levels(primary_ax, high_price, low_price)

        # Add a dotted horizontal line for the most recent closing price
        primary_ax.axhline(recent_close_price, color='gray', linestyle='dotted', linewidth=2, label=f'Current Price: {recent_close_price}')

        # Optional: Add a legend to the plot
        primary_ax.legend()

        # Save the plot to a file
        chart_file = "fibonacci_chart.png"
        fig.savefig(chart_file)
        return chart_file
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
        fig, ax = plt.subplots()
        mpf.plot(
            df_filtered,
            ax=ax,
            title=title,
            type='candle',
            style=custom_style,
            volume=True,
            addplot=ichimoku_plots,
            fill_between=[ichimoku_fill_up, ichimoku_fill_down]
        )
        
        recent_close_price = df_filtered['Close'].iloc[-1]
        ax.axhline(recent_close_price, color='gray', linestyle='dotted', linewidth=2)

        fig.savefig('ichimoku_chart.png')
        return 'ichimoku_chart.png'

    elif chart_type == 'donchian':
        # Calculate Donchian Channels
        period = 25
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
        fig, ax = plt.subplots()
        mpf.plot(
            df_filtered,
            ax=ax,
            title=title,
            type='candle',
            style=custom_style,
            volume=True,
            addplot=donchian_plots,
            fill_between=donchian_fill
        )

        recent_close_price = df_filtered['Close'].iloc[-1]
        ax.axhline(recent_close_price, color='gray', linestyle='dotted', linewidth=2)

        fig.savefig('donchian_chart.png')
        return 'donchian_chart.png'

    else:
        title = f'Chart for {token_name}'
        fig, ax = plt.subplots()
        mpf.plot(
            df_filtered,
            ax=ax,
            title=title,
            mav=(13,25),
            type='candle',
            style=custom_style,
            volume=True
        )

        recent_close_price = df_filtered['Close'].iloc[-1]
        ax.axhline(recent_close_price, color='gray', linestyle='dotted', linewidth=2)

        fig.savefig('default_chart.png')
        return 'default_chart.png'