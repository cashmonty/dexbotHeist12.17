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

# Define the main processing function
async def process_ohlc_data_and_generate_chart(token_name, ohlc_data, chart_type):
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


    if chart_type == 'ichimoku':
        # Calculate the Ichimoku Cloud on the data
        df_filtered = calculate_ichimoku(df_filtered)

        # Create Ichimoku Cloud lines for plotting
        ichimoku_plots = [
            mpf.make_addplot(df_filtered['Tenkan-sen'], color='#fcc905'),
            mpf.make_addplot(df_filtered['Kijun-sen'], color='#F83C78'),
            mpf.make_addplot(df_filtered['Senkou_Span_A'], color='#006B3D', alpha=0.5),
            mpf.make_addplot(df_filtered['Senkou_Span_B'], color='#D3212C', alpha=0.5),
            mpf.make_addplot(df_filtered['Chikou_Span'], color='#8D8D16'),
        ]

        # Prepare the fill_between parameters
        ichimoku_fill = {
            'y1': df_filtered['Senkou_Span_A'].values,
            'y2': df_filtered['Senkou_Span_B'].values,
            'alpha': 0.5
        }
        title = f'Chart for {token_name}'
        mpf.plot(
            df_filtered,
            title=title,
            type='candle',
            style='yahoo',
            addplot=ichimoku_plots,
            fill_between=ichimoku_fill,
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
            style='yahoo',
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
            style='yahoo',
            savefig='default_chart.png'
        )
        return 'default_chart.png'