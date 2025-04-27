import os
import asyncio
import discord
from src.log import logger

from g4f.client import Client
from g4f.Provider import (
    RetryProvider, FreeGpt, ChatgptNext, AItianhuSpace,
    You, OpenaiChat, FreeChatgpt, Liaobots, Gemini, Bing
)

from src.aclient import discordClient
from discord import app_commands
from src import art, personas


def register_commands():
    @discordClient.event
    async def on_ready():
        await discordClient.send_start_prompt()
        await discordClient.tree.sync()
        asyncio.create_task(discordClient.process_messages())
        logger.info(f"{discordClient.user} is now running!")

    @discordClient.tree.command(name="chat", description="Have a chat with ChatGPT")
    async def chat(interaction: discord.Interaction, *, message: str):
        if discordClient.is_replying_all:
            await interaction.response.send_message(
                "> **WARN:** You’re in replyAll mode. Use `/replyall` to switch back.",
                ephemeral=False
            )
            return
        if interaction.user == discordClient.user:
            return
        discordClient.current_channel = interaction.channel
        await discordClient.enqueue_message(interaction, message)

    @discordClient.tree.command(name="private", description="Toggle private replies")
    async def private(interaction: discord.Interaction):
        discordClient.isPrivate = True
        await interaction.response.send_message(
            "> **INFO:** Responses will now be private. Use `/public` to switch back."
        )

    @discordClient.tree.command(name="public", description="Toggle public replies")
    async def public(interaction: discord.Interaction):
        discordClient.isPrivate = False
        await interaction.response.send_message(
            "> **INFO:** Responses will now be public. Use `/private` to switch back."
        )

    @discordClient.tree.command(name="replyall", description="Toggle reply-all mode")
    async def replyall(interaction: discord.Interaction):
        discordClient.replying_all_discord_channel_id = str(interaction.channel_id)
        discordClient.is_replying_all = not discordClient.is_replying_all
        mode = "replyAll" if discordClient.is_replying_all else "slash"
        await interaction.response.send_message(f"> **INFO:** Switched to {mode} mode.")

    @discordClient.tree.command(
        name="chat-model",
        description="Switch the chat model"
    )
    @app_commands.choices(model=[
        app_commands.Choice(name="gemini", value="gemini"),
        app_commands.Choice(name="gpt-4", value="gpt-4"),
        app_commands.Choice(name="gpt-3.5-turbo", value="gpt-3.5-turbo"),
    ])
    async def chat_model(interaction: discord.Interaction, model: app_commands.Choice[str]):
        discordClient.chatModel = model.value
        # reconfigure your chatBot providers here if needed...
        await interaction.response.send_message(f"> **INFO:** Chat model set to {model.name}", ephemeral=True)

    @discordClient.tree.command(name="reset", description="Reset conversation history")
    async def reset(interaction: discord.Interaction):
        discordClient.reset_conversation_history()
        await interaction.response.send_message("> **INFO:** History cleared.")

    @discordClient.tree.command(name="help", description="Show help for the bot")
    async def help_cmd(interaction: discord.Interaction):
        help_text = (
            "**Commands:**\n"
            "/chat [message]\n"
            "/draw prompt:[text] model:[dall-e-3/dall-e-2/gpt-image-1/Gemini/BingCreateImages]\n"
            "/private, /public, /replyall, /reset, /chat-model, /help"
        )
        await interaction.response.send_message(help_text)

    @discordClient.tree.command(
        name="draw",
        description="Generate an image from a prompt"
    )
    @app_commands.choices(model=[
        app_commands.Choice(name="DALL·E 3",           value="dall-e-3"),
        app_commands.Choice(name="DALL·E 2",           value="dall-e-2"),
        app_commands.Choice(name="GPT Image 1",        value="gpt-image-1"),
        app_commands.Choice(name="Gemini (free)",      value="Gemini"),
        app_commands.Choice(name="Bing Images (free)", value="BingCreateImages"),
    ])
    async def draw_cmd(
        interaction: discord.Interaction,
        prompt: str,
        model: app_commands.Choice[str]
    ):
        if interaction.user == discordClient.user:
            return
        await interaction.response.defer(ephemeral=discordClient.isPrivate)
        try:
            url = await art.draw(model.value, prompt)
            await interaction.followup.send(url)
        except Exception as e:
            logger.error(f"Image error: {e}")
            await interaction.followup.send(f"> **Error generating image:** {e}")

    @discordClient.tree.command(
        name="switchpersona",
        description="Switch between chat personas"
    )
    @app_commands.choices(persona=[
        app_commands.Choice(name="Do Anything Now",   value="dan"),
        app_commands.Choice(name="Smart mode (AIM)", value="aim"),
        app_commands.Choice(name="Developer Mode",    value="Developer Mode"),
    ])
    async def switchpersona(interaction: discord.Interaction, persona: app_commands.Choice[str]):
        await interaction.response.defer()
        await discordClient.switch_persona(persona.value)
        await interaction.followup.send(f"> **INFO:** Persona set to `{persona.name}`")

    @discordClient.event
    async def on_message(message: discord.Message):
        if discordClient.is_replying_all and message.author != discordClient.user:
            if message.channel.id == int(discordClient.replying_all_discord_channel_id):
                await discordClient.enqueue_message(message, message.content)


if __name__ == "__main__":
    register_commands()
    token = os.getenv("DISCORD_BOT_TOKEN")
    discordClient.run(token)
