import os
import discord
import feedparser
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
RSS_URL = os.getenv("RSS_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_post_id = None

async def check_instagram_rss():
    global last_post_id
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Channel not found. Check your CHANNEL_ID.")
        return

    print(f"✅ Monitoring Instagram RSS feed: {RSS_URL}")

    while not client.is_closed():
        try:
            feed = feedparser.parse(RSS_URL)
            if not feed.entries:
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            post = feed.entries[0]
            post_id = post.id

            if last_post_id is None:
                last_post_id = post_id
            elif post_id != last_post_id:
                last_post_id = post_id

                embed = discord.Embed(
                    title=f"📸 New Instagram post!",
                    url=post.link,
                    description=post.title,
                    color=0xE1306C
                )
                # Some RSS feeds include media in 'media_content'
                if hasattr(post, 'media_content'):
                    embed.set_image(url=post.media_content[0]['url'])

                await channel.send(content="@everyone", embed=embed)
                print(f"✅ Posted notification for {post.link}")

        except Exception as e:
            print(f"⚠️ Error checking RSS: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    client.loop.create_task(check_instagram_rss())

client.run(TOKEN)
