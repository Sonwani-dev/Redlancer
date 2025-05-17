import re
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.helpers import escape_markdown
import asyncpraw

# --- Telegram Bot Token ---
BOT_TOKEN = "7889892752:AAFng1Zv0UWASuSct4SM6BExFQBdF4qaOio"  # Replace with your actual bot token

# --- Reddit API Credentials ---
reddit = asyncpraw.Reddit(
    client_id="xKr6ToQIjRSwpRn00kzH6A",
    client_secret="ALRCIWnwtbXvPdYi8PFxvqVcSa_36Q",
    user_agent="RedlancerBot/0.1 by Organic-Brilliant823"
)

# --- List of Subreddits to search ---
subreddits_str = "+".join([
    "freelance", "jobbit", "slavelabour", "hiring", "techjobs", "remotejs",
    "remotework", "remotejob", "designjobs", "pythonjobs", "forhire",
    "jobs4bitcoins", "remotejobs", "writingopportunities", "gigs",
    "workonline", "hire", "webdevjobs", "codingjobs", "contractorsforhire"
])

# --- /start Command Handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Welcome to Redlancer!*\n"
        "Send me a keyword (e.g. `python`, `video editor`, `design`) to get recent *hiring* posts from Reddit.",
        parse_mode="MarkdownV2"
    )

# --- Handle Keyword Messages ---
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text.lower()
    escaped_keyword = escape_markdown(keyword, version=2)
    results = []

    await update.message.reply_text(
        f"🔎 Searching Reddit *hiring* posts for: *{escaped_keyword}*...",
        parse_mode="MarkdownV2"
    )

    subreddit = await reddit.subreddit(subreddits_str)

    async for post in subreddit.new(limit=50):
        title = post.title.lower()
        body = post.selftext.lower()

        # Skip self-promotion / for hire posts
        if "for hire" in title or "for hire" in body:
            continue

        # Filter by keyword and hiring-related terms
        elif keyword in title or keyword in body:
            if re.search(r'\b(hiring|looking for|seeking|need|wanted)\b', title) or \
               re.search(r'\b(hiring|looking for|seeking|need|wanted)\b', body):

                safe_title = escape_markdown(post.title, version=2)
                safe_url = escape_markdown(post.url, version=2)

                results.append(f"📌 *{safe_title}*\n🔗 {safe_url}")

        if len(results) >= 5:
            break

    if results:
        for result in results:
            await update.message.reply_text(result, parse_mode="MarkdownV2")
    else:
        await update.message.reply_text(
            "😕 No *hiring* posts found with that keyword\\. Try something else!",
            parse_mode="MarkdownV2"
        )

# --- Main Function to Start Bot ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

    print("✅ Redlancer bot is running...")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
