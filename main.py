import os
import uuid
import threading
from flask import Flask, send_file, request as flask_request
from discord.ext import commands
import discord

# ТВОИ ДАННЫЕ
TOKEN = "MTM3MzcxNTU3OTgxNDQxNjQ4NA.GjhiCV.Yg4wztFoAJnNWOLlk0u4HD9_MotG-M60kHufAk"
OWNER_ID = 1361430335782518995

# Папка для файлов
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask API
app = Flask(__name__)
file_storage = {}  # file_id: {"path": ..., "owner": ...}

@app.route("/file/<file_id>")
def serve_file(file_id):
    if file_id not in file_storage:
        return "Файл не найден.", 404

    owner_id = file_storage[file_id]["owner"]
    requester_id = flask_request.args.get("user_id")

    if str(requester_id) != str(owner_id):
        return "Ты не овнер, чтобы смотреть этот файл.", 403

    return send_file(file_storage[file_id]["path"], as_attachment=True)

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# Discord бот
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

@bot.command()
async def scriptfile(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("Ты не овнер, брат.")
        return

    if not ctx.message.attachments:
        await ctx.send("Прикрепи .txt файл.")
        return

    attachment = ctx.message.attachments[0]
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.txt")
    await attachment.save(file_path)

    file_storage[file_id] = {
        "path": file_path,
        "owner": ctx.author.id
    }

    url = f"https://твоё-имя.railway.app/file/{file_id}?user_id={ctx.author.id}"
    await ctx.send(f"Файл загружен: {url}")

bot.run(TOKEN)
