python
import discord
from discord.ext import commands, tasks
import requests
import json
import os
from datetime import datetime
import asyncio
import schedule
import time

# Get token from Railway environment variable
TOKEN = os.environ.get('DISCORD_TOKEN')
CHANNEL_ID = int(os.environ.get('DISCORD_CHANNEL_ID', 0))

# JSON URL - akan kita setup nanti
JSON_URL = os.environ.get('JSON_URL', '')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store processed trades
processed_trades = set()

class TradeMonitor:
    def __init__(self):
        self.last_trades = []
    
    def fetch_trades(self):
        """Fetch trades from JSON URL"""
        try:
            if not JSON_URL:
                print("JSON_URL belum di-set")
                return []
            
            response = requests.get(JSON_URL, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching JSON: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []
    
    def format_embed(self, trade):
        """Create Discord embed for trade"""
        
        if trade.get('action') == 'ENTRY':
            color = discord.Color.green()
            title = "📈 NEW TRADE ENTRY"
        else:
            color = discord.Color.orange()
            title = "⚠️ 2-DAY TP/SL CHECK"
        
        embed = discord.Embed(
            title=title,
            color=color,
            timestamp=datetime.now()
        )
        
        # Add fields
        embed.add_field(name="Ticket", value=f"#{trade.get('ticket', 'N/A')}", inline=True)
        embed.add_field(name="Symbol", value=trade.get('symbol', 'N/A'), inline=True)
        embed.add_field(name="Type", 
                       value=f"{'🟢 BUY' if trade.get('type') == 'BUY' else '🔴 SELL'}", 
                       inline=True)
        
        embed.add_field(name="Entry Price", value=f"{trade.get('entry_price', 0):.5f}", inline=True)
        embed.add_field(name="Current Price", value=f"{trade.get('current_price', 0):.5f}", inline=True)
        embed.add_field(name="Volume", value=f"{trade.get('volume', 0):.2f}", inline=True)
        
        if trade.get('sl', 0) > 0:
            embed.add_field(name="SL", value=f"{trade.get('sl', 0):.5f}", inline=True)
            embed.add_field(name="Dist to SL", value=f"{trade.get('distance_sl', 0):.5f}", inline=True)
        
        if trade.get('tp', 0) > 0:
            embed.add_field(name="TP", value=f"{trade.get('tp', 0):.5f}", inline=True)
            embed.add_field(name="Dist to TP", value=f"{trade.get('distance_tp', 0):.5f}", inline=True)
        
        embed.add_field(name="Open Time", value=trade.get('open_time', 'N/A'), inline=False)
        embed.add_field(name="Check Time", value=trade.get('check_time', 'N/A'), inline=False)
        
        embed.set_footer(text=f"MT5 Bot • {datetime.now().strftime('%H:%M:%S')}")
        
        return embed

# Initialize monitor
monitor = TradeMonitor()

@bot.event
async def on_ready():
    print(f'✅ Bot ready: {bot.user}')
    print(f'✅ JSON URL: {JSON_URL}')
    
    # Send startup message
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="🚀 MT5 Trade Bot Started",
                description=f"Deployed on Railway\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Status", value="✅ Online", inline=True)
            embed.add_field(name="Check Interval", value="5 seconds", inline=True)
            await channel.send(embed=embed)
    except:
        pass
    
    # Start monitoring
    check_trades.start()

@tasks.loop(seconds=5)
async def check_trades():
    """Check for new trades every 5 seconds"""
    try:
        trades = monitor.fetch_trades()
        
        if not trades:
            return
        
        # Get only new trades
        new_trades = []
        for trade in trades[-10:]:  # Check last 10 trades
            trade_id = f"{trade.get('ticket')}_{trade.get('check_time', '')}"
            if trade_id not in processed_trades:
                new_trades.append(trade)
                processed_trades.add(trade_id)
        
        # Send notifications
        channel = bot.get_channel(CHANNEL_ID)
        if channel and new_trades:
            for trade in new_trades:
                embed = monitor.format_embed(trade)
                await channel.send(embed=embed)
                await asyncio.sleep(1)  # Delay between messages
        
        # Clean old processed trades
        if len(processed_trades) > 100:
            # Keep only last 50
            all_trades = list(processed_trades)
            for old_id in all_trades[:-50]:
                processed_trades.remove(old_id)
                
    except Exception as e:
        print(f"Error in check_trades: {str(e)}")

@bot.command(name='status')
async def status(ctx):
    """Check bot status"""
    embed = discord.Embed(
        title="🤖 Bot Status",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    
    embed.add_field(name="Status", value="✅ Online", inline=True)
    embed.add_field(name="Uptime", value="Just started", inline=True)
    embed.add_field(name="Processed Trades", value=str(len(processed_trades)), inline=True)
    embed.add_field(name="JSON URL", value=JSON_URL[:50] + "..." if len(JSON_URL) > 50 else JSON_URL, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    """Check latency"""
    await ctx.send(f'🏓 Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='clear')
@commands.has_permissions(administrator=True)
async def clear_cache(ctx):
    """Clear processed trades cache"""
    processed_trades.clear()
    await ctx.send('✅ Cache cleared!')

# Run bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not set!")
        print("Please set DISCORD_TOKEN environment variable in Railway")
    elif not CHANNEL_ID:
        print("❌ ERROR: DISCORD_CHANNEL_ID not set!")
    else:
        print("🚀 Starting bot...")
        bot.run(TOKEN)
