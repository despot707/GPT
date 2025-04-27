import os
from dotenv import load_dotenv
from g4f.cookies import set_cookies

# Bring in the new command registration and the client instance:
from src.bot import register_commands
from src.aclient import discordClient

load_dotenv()

if __name__ == "__main__":
    # if you still need Bing/Google cookies for g4f:
    set_cookies(".bing.com",     {"_U": os.getenv("BING_COOKIE", "")})
    set_cookies(".google.com",   {"__Secure-1PSID": os.getenv("GOOGLE_PSID", "")})

    # wire up all your slash commands
    register_commands()
    # finally start the bot
    discordClient.run(os.getenv("DISCORD_BOT_TOKEN"))
