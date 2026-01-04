from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import config
from database import db
from imdb import get_movie

bot = Client(
    "Jmscchub",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# 🔹 FORCE SUB
async def force_sub(bot, user_id):
    try:
        await bot.get_chat_member(config.FORCE_SUB_CHANNEL, user_id)
        return True
    except:
        return False

# 🔹 SEARCH HANDLER
@bot.on_message(filters.text & filters.private)
async def search(bot, message):
    if not await force_sub(bot, message.from_user.id):
        btn = [[InlineKeyboardButton("📢 Join Channel", url="https://t.me/yyvybttc")]]
        return await message.reply("❌ Pehle channel join karo", reply_markup=InlineKeyboardMarkup(btn))

    query = message.text.lower()
    files = await db.find({"keywords": {"$regex": query}}).to_list(50)

    if not files:
        return await message.reply("❌ Movie nahi mili")

    imdb_data = get_movie(query)

    await send_page(message, files, imdb_data, page=0)

# 🔹 SEND PAGE
async def send_page(message, files, imdb_data, page):
    start = page * config.RESULTS_PER_PAGE
    end = start + config.RESULTS_PER_PAGE
    chunk = files[start:end]

    buttons = []
    for f in chunk:
        buttons.append([
            InlineKeyboardButton(
                f"{f['quality']} | {f['size']} MB",
                url=f"https://t.me/bhbyvyub/{f['msg_id']}"
            )
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅ Back", callback_data=f"page_{page-1}"))
    if end < len(files):
        nav.append(InlineKeyboardButton("Next ➡", callback_data=f"page_{page+1}"))
    if nav:
        buttons.append(nav)

    caption = f"""
🎬 *{imdb_data['title']} ({imdb_data['year']})*
⭐ Rating: {imdb_data.get('rating', 'N/A')}
📁 Files Found: {len(files)}
"""

    await message.reply_photo(
        imdb_data["poster"],
        caption=caption,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🔹 CALLBACK
@bot.on_callback_query(filters.regex("page_"))
async def pagination(bot, query):
    page = int(query.data.split("_")[1])
    text = query.message.caption.split("\n")[0]
    search_term = text.replace("🎬", "").strip()

    files = await db.find({"keywords": {"$regex": search_term.lower()}}).to_list(50)
    imdb_data = get_movie(search_term)

    await query.message.delete()
    await send_page(query.message, files, imdb_data, page)

bot.run()
