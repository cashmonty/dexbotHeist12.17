import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from commands import chart, chartichi, chartdonchian, token, floor, trades, wallet, toppools


# Load environment variables
load_dotenv()
bot_token = os.getenv('BOT_TOKEN')


intents = discord.Intents.default()
intents.messages = True  # Enable any other intents as needed
intents.message_content = True 
bot = commands.Bot(command_prefix="/", intents=intents)


bot.add_command(token)
bot.add_command(chart)
bot.add_command(chartichi)
bot.add_command(chartdonchian)
bot.add_command(floor)
bot.add_command(trades)
bot.add_command(wallet)
bot.add_command(toppools)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Run the bot
bot.run(bot_token)



