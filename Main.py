import discord

from discord.ext import tasks
from datetime import datetime

from config import DISCORD_TOKEN
from Watchlist import load_watchlist, save_watchlist
from Scanner import analyze_symbol

intents = discord.Intents.default()

client = discord.Client(intents=intents)


def build_embed(results):

    embed = discord.Embed(
        title="📊 DCA MARKET REPORT",
        description=f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        color=discord.Color.green()
    )

    strong = []
    dca = []

    for r in results:

        day = r["day"]
        week = r["week"]

        if (
            day["status"] == "STRONG DCA"
            or week["status"] == "STRONG DCA"
        ):

            strong.append(
                f"**{r['symbol']}**\n"
                f"Day: {day['score']}\n"
                f"Week: {week['score']}"
            )

        elif (
            day["status"] == "DCA"
            or week["status"] == "DCA"
        ):

            dca.append(
                f"**{r['symbol']}**\n"
                f"Day: {day['score']}\n"
                f"Week: {week['score']}"
            )

    embed.add_field(
        name=f"🚀 STRONG DCA ({len(strong)})",
        value="\n\n".join(strong) if strong else "None",
        inline=False
    )

    embed.add_field(
        name=f"✅ DCA ({len(dca)})",
        value="\n\n".join(dca) if dca else "None",
        inline=False
    )

    embed.set_footer(
        text=f"Watchlist: {len(WATCHLIST)} symbols"
    )

    return embed

def build_stock_embed(result):

    day = result["day"]
    week = result["week"]

    embed = discord.Embed(
        title=f"📊 {result['symbol']}",
        color=discord.Color.green()
    )

    embed.description = (
        f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"💰 Price: ${day['price']}"
    )

    embed.add_field(
        name=f"📅 DAY | {day['status']}",
        value=
        f"RSI : {day['rsi']} (+{day['rsiScore']})\n"
        f"STO : {day['sto']} (+{day['stoScore']})\n"
        f"SMA : {day['sma']} (+{day['smaScore']})\n"
        f"Momentum : {day['momentum']}\n"
        f"⭐ Score : {day['score']}",
        inline=False
    )

    embed.add_field(
        name=f"📈 WEEK | {week['status']}",
        value=
        f"RSI : {week['rsi']} (+{week['rsiScore']})\n"
        f"STO : {week['sto']} (+{week['stoScore']})\n"
        f"SMA : {week['sma']} (+{week['smaScore']})\n"
        f"Momentum : {week['momentum']}\n"
        f"⭐ Score : {week['score']}",
        inline=False
    )

    return embed

@tasks.loop(minutes=30)
async def scan_market():

    channel = discord.utils.get(
        client.get_all_channels(),
        name="dca-alerts"
    )

    if channel is None:
        print("❌ ไม่พบ channel dca-alerts")
        return

    watchlist = load_watchlist()

    for symbol in watchlist:

        try:
            result = analyze_symbol(symbol)

            if result is None:
                print(f"❌ {symbol} result is None")
                continue

            if result.get("day") is None:
                print(f"❌ {symbol} day is None")
                continue

            if result.get("week") is None:
                print(f"❌ {symbol} week is None")
                continue

            day_status = result["day"]["status"]
            week_status = result["week"]["status"]

            valid_status = ["DCA", "STRONG DCA"]

            if day_status not in valid_status:
                continue

            if week_status not in valid_status:
                continue

            embed = build_stock_embed(result)

            await channel.send(embed=embed)

            print(f"✅ Alert Sent : {symbol}")

        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")

@client.event
async def on_ready():

    print(f"✅ {client.user} Online")

    await client.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="TradingView"
        )
    )

    if not scan_market.is_running():
        scan_market.start()


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content == "!ping":

        await message.channel.send("🏓 Pong!")

    if message.content.startswith("!watch"):

        parts = message.content.split()

        if len(parts) < 2:
            await message.channel.send("❌ ใช้: !watch AAPL")
            return

        symbol = parts[1].upper()

        result = analyze_symbol(symbol)

        if (
            result is None
            or result.get("day") is None
            or result.get("week") is None
        ):
            await message.channel.send(
                f"❌ ไม่สามารถดึงข้อมูล {symbol} ได้"
            )
            return

        embed = build_stock_embed(result)

        await message.channel.send(embed=embed)

        embed = discord.Embed(
            title=f"📊 {symbol}",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="DAY",
            value=(
                f"Status: {day['status']}\n"
                f"Score: {day['score']}\n"
                f"RSI: {day['rsi']}\n"
                f"STO: {day['sto']}\n"
                f"Momentum: {day['momentum']}"
            ),
            inline=False
        )

        embed.add_field(
            name="WEEK",
            value=(
                f"Status: {week['status']}\n"
                f"Score: {week['score']}\n"
                f"RSI: {week['rsi']}\n"
                f"STO: {week['sto']}\n"
                f"Momentum: {week['momentum']}"
            ),
            inline=False
        )

        await message.channel.send(embed=embed)


client.run(DISCORD_TOKEN)