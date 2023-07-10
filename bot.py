import discord
import requests
import certifi
import os
from bs4 import BeautifulSoup
import html

YOUR_BOT_TOKEN = 'Insert Token Here'
SPOONACULAR_API_KEY = 'Insert Token Here'

# Set SSL certificate file path
os.environ["SSL_CERT_FILE"] = certifi.where()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Bot is ready.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!imhungry'):
        await get_and_send_random_recipe(message.channel)

async def get_and_send_random_recipe(channel):
    recipe, image_url = await get_random_recipe()
    if len(recipe) > 2000:
        # Split the recipe into multiple messages
        messages = [recipe[i:i+2000] for i in range(0, len(recipe), 2000)]
        for msg in messages:
            await channel.send(msg)
    else:
        await channel.send(recipe)

    if image_url:
        await channel.send(image_url)

async def get_random_recipe():
    url = f"https://api.spoonacular.com/recipes/random?apiKey={SPOONACULAR_API_KEY}&number=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        recipe = data["recipes"][0]
        recipe_name = recipe["title"]
        recipe_instructions = recipe["instructions"]
        recipe_summary = recipe["summary"]
        image_url = recipe["image"]

        # Format summary
        summary = html.unescape(recipe_summary)
        summary = summary.replace("<b>", "").replace("</b>", "").strip()

        # Format instructions
        instructions = html.unescape(recipe_instructions).strip()

        # Remove HTML tags from summary and instructions
        summary = BeautifulSoup(summary, 'html.parser').get_text()
        instructions = BeautifulSoup(instructions, 'html.parser').get_text()

        # Construct the recipe message
        recipe_message = f"Recipe: {recipe_name}\n\nSummary: {summary}\n\nInstructions: {instructions}"
        return recipe_message, image_url
    else:
        return "Sorry, I couldn't fetch a recipe at the moment.", None

client.run(YOUR_BOT_TOKEN)
