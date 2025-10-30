"""
🪽 TEXT ANGEL API – FastAPI Backend
Protective rewrite and shielding service for emotional tone refinement.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os, re

# === Load environment ===
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found. Please set it in your environment or .env file.")

# === Initialize OpenAI client ===
try:
    # For modern SDK (>=1.0)
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception:
    # For legacy SDK (<1.0)
    import openai
    openai.api_key = OPENAI_API_KEY
    client = None
    
# === Handle either modern (OpenAI class) or legacy (openai.api_key) client ===
try:
    from openai import OpenAI  # ✅ modern client (v1.x+)
    client = OpenAI(api_key=OPENAI_API_KEY)
    use_new_client = True
except ImportError:
    import openai               # 🕰️ legacy fallback (v0.28 style)
    openai.api_key = OPENAI_API_KEY
    client = None
    use_new_client = False

# === FastAPI App Initialization ===
app = FastAPI(title="TEXT ANGEL API", version="2.0")

# Allow Streamlit / Flutter / iOS local dev to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # during dev; restrict later to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Schemas ===
class RewriteRequest(BaseModel):
    tone: str
    message: str

class RewriteResponse(BaseModel):
    rewritten: str
    tone: str

class ShieldRequest(BaseModel):
    message: str

class ShieldResponse(BaseModel):
    shielded: str
    count: int
    blocked_words: list[str]

# === Tone Prompts ===
TONE_PROMPTS = {
    "GRACE": "Rewrite the following message with kindness, care, and gentleness.",
    "TRUTH": "Rewrite the following message to be honest, clear, and respectful.",
    "CALM": "Rewrite the following message in a peaceful and soft tone, with no harshness or aggression."
}

# === Rewrite Logic ===
def handle_rewrite_input(tone: str, message: str) -> str:
    """Send rewrite request to OpenAI with selected tone."""
    prompt_text = TONE_PROMPTS.get(tone.upper(), TONE_PROMPTS["GRACE"])
    prompt = f"{prompt_text}\n\nMessage: {message}"

    try:
        if use_new_client:
            # ✅ Modern OpenAI Python client (v1.x+)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a kind, emotionally intelligent assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()

        else:
            # 🕰️ Legacy SDK style (v0.28)
            import openai
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a kind, emotionally intelligent assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200,
            )
            return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rewrite failed: {str(e)}")

# === Shield Logic ===
def shield_input_text(message: str) -> tuple[str, int, list[str]]:
    """Replace flagged words with censor blocks."""
    blocked_words = ["shit", "fuck", "bitch", "asshole", "dick", "hate", "stupid", "ugly"]
    count = 0
    found = []
    for word in blocked_words:
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        matches = pattern.findall(message)
        if matches:
            found.extend(matches)
            count += len(matches)
            message = pattern.sub(lambda m: "▆" * len(m.group()), message)
    return message, count, found

# === Routes ===
@app.post("/rewrite", response_model=RewriteResponse)
async def rewrite(req: RewriteRequest):
    rewritten = handle_rewrite_input(req.tone, req.message)
    return {"rewritten": rewritten, "tone": req.tone.upper()}

@app.post("/shield", response_model=ShieldResponse)
async def shield(req: ShieldRequest):
    shielded, count, found = shield_input_text(req.message)
    return {"shielded": shielded, "count": count, "blocked_words": found}

@app.get("/ping")
def ping():
    return {"status": "alive", "message": "TEXT ANGEL API is listening 🪽"}
