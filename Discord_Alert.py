import discord
from discord.ext import commands, tasks
from DatabaseReader import DatabaseReader
import atexit
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timezone, timedelta
import pytz
from dotenv import load_dotenv
import os

# Constants from .env file
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
Bot_CHANNEL_ID = int(os.getenv("BOT_CHANNEL_ID"))
UVALab_CHANNEL_ID = int(os.getenv("UVALAB_CHANNEL_ID"))

LN2_Level_ALERT_THRESHOLD = float(os.getenv("LN2_THRESHOLD")) #Volts
ColdHead_TEMP_HIGH = float(os.getenv("ColdHead_TEMP_HIGH")) #Kelvin
ColdHead_TEMP_LOW = float(os.getenv("ColdHead_TEMP_LOW")) #Kelvin

# Path to SQLite DB
db_path = r"Z:\spin\instance\flaskr.sqlite"


# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Global reference to avoid duplicate alerts
alert_triggered = False


@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    channel = bot.get_channel(Bot_CHANNEL_ID)
    if channel:
        await channel.send("👁️👄👁️ Always watching...")
    check_thermocouple.start()  # Start background monitoring
    check_ColdHeads.start()
    check_data_staleness.start()




async def send_shutdown_alert():
    await bot.wait_until_ready()
    channel = bot.get_channel(Bot_CHANNEL_ID)
    if channel:
        await channel.send(content=":wave: Bye~ :skull:\n")
        

@bot.event
async def on_disconnect():
    print("🔌 Bot disconnected from Discord. :headstone:")


@bot.command(name='ShutDown')
async def shutdown_bot(ctx):

    allowed_user_ids = [274700280409489409,1319339525385752661,940096349586743328]  
    if ctx.author.id not in allowed_user_ids:
        await ctx.send("❌ You are not authorized to shut me down.")
        return

    await ctx.send("⚠️ Shutting down bot...")
    await send_shutdown_alert()
    await bot.close()

@bot.command(name='Commands')
async def help_command(ctx):
    if ctx.channel.id != Bot_CHANNEL_ID:
        return

    help_message = (
        "📖 **Available Commands**:\n"
        "• `!LN2` – Show the current LN2 thermocouple voltage.\n"
        "• `!ShutDown` – Shut down the bot (restricted access).\n"
        "• `!Update` Give a status report.\n"
        "• `!Commands` – Show this help message.\n"

    )
    await ctx.send(help_message)


#Tasks and Commands
alert_triggered_stale_data = False

@tasks.loop(seconds=60.0)
async def check_data_staleness():
    global alert_triggered_stale_data

    try:
        reader = DatabaseReader(db_path)
        last_timestamp = reader.get_last_timestamp("HMI") 
        reader.close()

        if last_timestamp is None:
            print("⚠️ No timestamp found in database.")
            return

        # Current time in Eastern
        now = datetime.now(pytz.timezone("US/Eastern"))

        # Make sure last_timestamp is timezone-aware
        if last_timestamp.tzinfo is None:
            last_timestamp = pytz.timezone("US/Eastern").localize(last_timestamp)

        elapsed = now - last_timestamp

        if elapsed > timedelta(minutes=5):
            if not alert_triggered_stale_data:
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    await channel.send(
                        "🚨 **ALERT:** The database could be down!\n"
                        f"Last data timestamp: `{last_timestamp.strftime('%Y-%m-%d %H:%M:%S')}`"
                    )
                alert_triggered_stale_data = True
        else:
            alert_triggered_stale_data = False

    except Exception as e:
        print(f"[Staleness Check Error] {e}")


@tasks.loop(seconds=60.0)  # check every 60 seconds
async def check_thermocouple():
    global alert_triggered
    try:
        reader = DatabaseReader(db_path)
        raw_V = reader.get_latest_value("Labjack", "thermocouple")
        reader.close()

        if raw_V is not None and raw_V >= LN2_Level_ALERT_THRESHOLD and not alert_triggered:
            channel = bot.get_channel(Bot_CHANNEL_ID)
            if channel:
                await channel.send("🚨 **ALERT:** Purifier needs to be refilled!")
                alert_triggered = True  # avoid spam
        elif raw_V is not None and raw_V < LN2_Level_ALERT_THRESHOLD:
            alert_triggered = False  # reset when value drops

    except Exception as e:
        print(f"[Monitor Error] {e}")



alert_triggered_ColdHeads = False
@tasks.loop(seconds=60.0)
async def check_ColdHeads():
    global alert_triggered_ColdHeads

    SENSOR_NAMES = ["ti501_ai", "ti502_ai", "ti503_ai", "ti504_ai", "ti505_ai"]
    OUT_OF_RANGE = lambda v: v is not None and (v > ColdHead_TEMP_HIGH or v < ColdHead_TEMP_LOW)

    try:
        reader = DatabaseReader(db_path)
        triggered = []

        for sensor in SENSOR_NAMES:
            value = reader.get_latest_value("HMI", sensor)
            if OUT_OF_RANGE(value):
                triggered.append((sensor, value))

        reader.close()

        if triggered and not alert_triggered_ColdHeads:
            channel = bot.get_channel(Bot_CHANNEL_ID)
            if channel:
                msg = "🚨 **ColdHead Temp ALERT** 🚨\n"
                for name, value in triggered:
                    status = "🥶 Too Cold!" if value < LOW_TEMP else "🥵 Too Hot!"
                    msg += f"• `{name}` = `{value:.2f}` V {status}\n"

                msg += "\nAny value < `3.0` or > `5.0` is considered unsafe!"
                await channel.send(msg)
                alert_triggered_ColdHeads = True

        elif not triggered:
            alert_triggered_ColdHeads = False

    except Exception as e:
        print(f"[ColdHead Monitor Error] {e}")

#####Update#####


async def send_status_update():
    try:

        if not Bot_CHANNEL_ID or not UVALAB_CHANNEL_ID:
            print("One or more channels not found.")
            return

        reader = DatabaseReader(db_path)

        # Get values from HMI
        pt501 = reader.get_latest_value("HMI", "pt501_ai")
        pt502 = reader.get_latest_value("HMI", "pt502_ai")
        ti_values = [
            reader.get_latest_value("HMI", sensor)
            for sensor in ["ti501_ai", "ti502_ai", "ti503_ai", "ti504_ai", "ti505_ai"]
        ]
        fc501 = reader.get_latest_value("HMI", "fc501_ai")
        fc502 = reader.get_latest_value("HMI", "fc502_ai")
        lit501 = reader.get_latest_value("HMI", "lit501_ai")
        ait501_ai = reader.get_latest_value("HMI", "ait501_ai")

        reader.close()

        # Compute average ColdHead temp
        valid_tis = [val for val in ti_values if val is not None]
        ti_avg = sum(valid_tis) / len(valid_tis) if valid_tis else None

        # Build message
        msg = "📊 **Automated System Status Update** 📊\n"
        msg += f"• Dewar Pressure: `{pt501:.2f}`\n" if pt501 is not None else "• `pt501_ai`: `No data`\n"
        msg += f"• Inlet Pressure: `{pt502:.2f}`\n" if pt502 is not None else "• `pt502_ai`: `No data`\n"
        msg += f"• Avg ColdHead Temp: `{ti_avg:.2f}`\n" if ti_avg is not None else "• Avg `ti50x_ai`: `No data`\n"
        msg += f"• Inlet Flow: `{fc501:.2f}`\n" if fc501 is not None else "• `fc501_ai`: `No data`\n"
        msg += f"• Outlet Flow: `{fc502:.2f}`\n" if fc502 is not None else "• `fc502_ai`: `No data`\n"
        msg += f"• Liquid Helium: `{lit501:.2f}%`\n" if lit501 is not None else "• `lit501_ai`: `No data`\n"
        msg += f"• Helium Purity: `{ait501_ai:.3f}%`\n" if ait501_ai is not None else "• `ait501_ai`: `No data`\n"
        msg += f"• ColdHead Alert: `{alert_triggered_ColdHeads}`\n"
        msg += f"• LN2 Alert: `{alert_triggered}`"

        # Send to both channels
        await UVALAB_CHANNEL_ID.send(msg)
        await BOT_CHANNEL_ID.send(msg)

    except Exception as e:
        error_msg = f"❌ Failed to fetch system status: `{str(e)}`"
        if BOT_CHANNEL_ID:
            await BOT_CHANNEL_ID.send(error_msg)
        elif UVALAB_CHANNEL_ID:
            await UVALAB_CHANNEL_ID.send(error_msg)
        else:
            print(error_msg)


@bot.command(name='Update')
async def status_update(ctx):
    await send_status_update()


@bot.command(name='Data')
async def last_timestamp_cmd(ctx):
    try:
        reader = DatabaseReader(db_path)
        ts = reader.get_last_timestamp("HMI")
        reader.close()

        if ts:
            await ctx.send(f"🕒 Last data entry: `{ts.strftime('%Y-%m-%d %H:%M:%S')}`")
        else:
            await ctx.send("⚠️ No timestamp found in database.")

    except Exception as e:
        await ctx.send(f"❌ Error: `{str(e)}`")

@bot.command(name='LN2')
async def Alert_LN2(ctx):
    if ctx.channel.id != Bot_CHANNEL_ID:
        return

    try:
        reader = DatabaseReader(db_path)
        raw_V = reader.get_latest_value("Labjack", "thermocouple")
        reader.close()

        if raw_V is None:
            await ctx.send("⚠️ No thermocouple data found.")
            return

        await ctx.send(f"🌡️ LN2 Thermocouple Reading:\n• Raw Voltage: `{raw_V:.3f} V`")

    except Exception as e:
        await ctx.send(f"❌ Error retrieving temperature: `{str(e)}`")


#######SIlly#####


@bot.command(name='Devin')
async def greet_devin(ctx):
    await ctx.send("Hello Dima.")

@bot.command(name='Dima')
async def greet_dima(ctx):
    await ctx.send("Hello Jay.")

@bot.command(name='Jay')
async def greet_jay(ctx):
    await ctx.send("Hello Devin.")




#DO NOT SHARE THIS TOKEN
try:
    bot.run(TOKEN)
finally:
    print("🛑 Bot is shutting down...")
