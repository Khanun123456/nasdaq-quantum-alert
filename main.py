import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID   = os.environ.get("CHAT_ID")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


def format_message(data: dict) -> str:
    signal = data.get("signal", "UNKNOWN")
    price  = data.get("price",  "?")
    high   = data.get("high",   "?")
    low    = data.get("low",    "?")
    ticker = data.get("ticker", "NASDAQ")
    tf     = data.get("tf",     "?")
    time   = data.get("time",   "?")

    # คำนวณ TP / SL จาก high/low
    try:
        p = float(price)
        h = float(high)
        l = float(low)
        rng = h - l

        if signal == "BUY":
            tp1 = round(p + rng * 1.0, 2)
            tp2 = round(p + rng * 2.0, 2)
            sl  = round(p - rng * 0.5, 2)
            arrow = "🟢"
            dir_label = "BUY  ▲"
        else:
            tp1 = round(p - rng * 1.0, 2)
            tp2 = round(p - rng * 2.0, 2)
            sl  = round(p + rng * 0.5, 2)
            arrow = "🔴"
            dir_label = "SELL ▼"
    except Exception:
        tp1 = tp2 = sl = "?"
        arrow = "⚪"
        dir_label = signal

    msg = (
        f"⚡ *NASDAQ QUANTUM SIGNAL*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{arrow} *{dir_label}* — `{ticker}` ({tf})\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📍 Price : `{price}`\n"
        f"🎯 TP1   : `{tp1}`\n"
        f"🎯 TP2   : `{tp2}`\n"
        f"🛑 SL    : `{sl}`\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 `{time}`"
    )
    return msg


@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON"}, status_code=400)

    msg = format_message(data)

    async with httpx.AsyncClient() as client:
        await client.post(TELEGRAM_URL, json={
            "chat_id":    CHAT_ID,
            "text":       msg,
            "parse_mode": "Markdown"
        })

    return {"ok": True}


@app.get("/")
def root():
    return {"status": "NASDAQ Quantum Alert Server running"}
