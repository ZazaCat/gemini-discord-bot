import google.generativeai as genai
import discord
from discord.ext import commands
import keep_alive
import asyncio
import random
import os
import json
import requests
import base64
import io
from PIL import Image
from io import BytesIO

api_key = "AIzaSyC6EyUOiiK-EjUNpUquggehmSjYsSFA0L4"
genai.configure(api_key=api_key)

text_model = genai.GenerativeModel('gemini-pro')
image_model = genai.GenerativeModel('gemini-pro-vision')

user_chats = {}

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    }
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)

second_image_model = genai.GenerativeModel('gemini-pro-vision')

@bot.event
async def on_message(message):
    try:
        user = message.author
        user_id = message.author.id
        if user_id not in user_chats:
            user_chats[user_id] = text_model.start_chat(history=[])
        user_chat = user_chats[user_id]
        if bot.user.mention in message.content:
            user_input = message.content.replace(bot.user.mention, "").strip()

            # Check if there are image attachments
            if message.attachments:
                image_parts = []
                # Loop through each attachment and add it to image_parts
                for attachment in message.attachments:
                    image_data = await attachment.read()
                    image_mime = attachment.content_type
                    image_parts.append({
                        "mime_type": image_mime,
                        "data": image_data
                    })

                # Create prompt_parts with image_parts and user_input
                prompt_parts = image_parts + [user_input]

                # Generate response using image model
                response = image_model.generate_content(prompt_parts, generation_config=generation_config, safety_settings=safety_settings)

                # Generate second response for image breakdown
                second_prompt_parts = image_parts + ["Generate a breakdown response for this photo and an answer. I want you to describe everything in the photo. Literally everything you see in the photo must be part of your response. Do not miss a single thing. EVERYTHING YOU SEE IN THE PHOTO MUST BE IN THE RESPONSE. EVERY PIXEL IN THE IMAGE MUST BE EXAMINED AND ADDED TO THE RESPONSE. EVERY OBJECT IN THE PHOTO MUST BE ADDED TO THE RESPONSE. IT MUST BE EXTREMELY ACCURATE. Do not include something that isn't in the photo"]
                second_response = second_image_model.generate_content(second_prompt_parts, generation_config=generation_config, safety_settings=safety_settings)

                secondvisionresponse = second_response.text

                # Create embed with response details
                title = user_input[:30] + "..." if len(user_input) > 30 else user_input
                embed = discord.Embed(title=title, description=response.text, color=0x418bf1)

                # Set thumbnail to the URL of the first image attachment
                embed.set_thumbnail(url=message.attachments[0].url)

                # Reply to the user with the embed
                await message.reply(embed=embed)

                # Append user input and model response to chat history
                user_chat.history.append({
                    "role": "user",
                    "parts": [{"text": user_input}]
                })
                user_chat.history.append({
                    "role": "model",
                    "parts": [{"text": "Full image detail: " + secondvisionresponse + "Here is the short image detail, please don't send the full image detail, only the short image detail, here it is: " + response.text}]
                })
            else:
                # If no image attachments, process text input as before
                if message.guild is not None:
                    channel = message.channel
                    channel_name = channel.name
                    guild = message.guild
                    guild_name = guild.name
                    user_name = user.name
                    response = user_chat.send_message(f"""Google Gemini is a powerful AI model capable of understanding and generating text, images, and code. It's designed to handle complex tasks and can operate across and combine different types of information including text, code, audio, image, and video. It's available in three versions: Gemini Ultra for highly complex tasks, Gemini Pro for scaling across a wide range of tasks, and Gemini Nano for on-device tasks. You are currently using the Gemini Pro version of Gemini. Please generate a short response. Not too long. You are currently chatting with {user_name} in {channel_name} in the server {guild_name}.
                                           input: Hi
                                           output: Hello!
                                           input: Who are you
                                           output: My name is Gemini, an AI created by Google. What about you? 🤔
                                           input: {user_input}
                                           output: """)
                else:
                    response = user_chat.send_message(f"""Google Gemini is a powerful AI model capable of understanding and generating text, images, and code. It's designed to handle complex tasks and can operate across and combine different types of information including text, code, audio, image, and video. It's available in three versions: Gemini Ultra for highly complex tasks, Gemini Pro for scaling across a wide range of tasks, and Gemini Nano for on-device tasks. You are currently using the Gemini Pro version of Gemini. Please generate a short response. Not too long.
                                           input: Hi
                                           output: Hello!
                                           input: Who are you
                                           output: My name is Gemini, an AI created by Google. What about you? 🤔
                                           input: {user_input}
                                           output: """)
                title = user_input[:30] + "..." if len(user_input) > 30 else user_input
                embed = discord.Embed(title=title, description=response.text, color=0x418bf1)
                await message.reply(embed=embed)
    except Exception as e:
        print(f"An error occurred: {e}")
        await message.respond("An error occurred.")

@bot.slash_command(name="reset", description="Reset the chat history")
async def reset(ctx):
    user_id = ctx.author.id
    user_chats[user_id] = text_model.start_chat(history=[])
    await ctx.respond("Chat history has been reset.")

@bot.slash_command(name="help", description="Tutorial for using Gemini")
async def help(ctx):
    await ctx.respond("Hello! Welcome to Gemini. To use Gemini, simply mention the bot and type your message. It works for DMs too! You can use Vision by adding an image attachment to your message.")

keep_alive.keep_alive()

bot.run("MTE4NTc4Nzg5ODM0NDI0NzM0Ng.GXM1p1.U9Cm8pDFf-ORSrg0Y7nXSZJfFs_KftjaK486TU")