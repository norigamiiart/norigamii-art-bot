import os
import discord
import requests
import asyncio

# ---------------------------
# CONFIG
# ---------------------------
TOKEN = os.getenv("DISCORD_TOKEN")  # Set this in Railway variables
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))  # Also set this in Railway
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "your_username_here")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))  # 300 = every 5 min

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_post_id = None


async def check_instagram():
    """Periodically checks Instagram for new posts and notifies Discord."""
    global last_post_id
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("❌ Channel not found. Check your CHANNEL_ID.")
        return

    print(f"✅ Monitoring Instagram posts from @{INSTAGRAM_USERNAME}...")

    while not client.is_closed():
        try:
            # Using Instagram's public page JSON (may change occasionally)
            url = f"https://www.instagram.com/{INSTAGRAM_USERNAME}/?__a=1&__d=dis"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            data = response.json()

            post = data["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]
            post_id = post["id"]
            post_url = f"https://www.instagram.com/p/{post['shortcode']}/"
            image_url = post["display_url"]

            if last_post_id is None:
                last_post_id = post_id
            elif post_id != last_post_id:
                last_post_id = post_id

                embed = discord.Embed(
                    title=f"📸 New Instagram post by @{INSTAGRAM_USERNAME}!",
                    url=post_url,
                    color=0xE1306C  # Instagram pink
                )
                embed.set_image(url=image_url)
                embed.set_footer(text="Instagram • New post detected")

                await channel.send(content="@everyone", embed=embed)
                print(f"✅ Posted new notification for {post_url}")

        except Exception as e:
            print(f"⚠️ Error checking Instagram: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    client.loop.create_task(check_instagram())


client.run(TOKEN)
