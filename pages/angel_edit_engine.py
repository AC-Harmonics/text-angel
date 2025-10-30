import re
import json
import openai

# Load tone prompts
with open("tone_prompts.json", "r") as f:
    tone_prompts = json.load(f)

# Load shield words
with open("shield_filter_words.json", "r") as f:
    shield_words = json.load(f)

def handle_rewrite_input(tone, original):
    """
    Rewrites a message using the selected tone and applies shielding.
    Returns the rewritten message and count of shielded words.
    """
    if tone not in tone_prompts:
        return original, 0

    system_prompt = tone_prompts[tone]
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": original}
        ]
    )
    rewritten = completion['choices'][0]['message']['content']
    shielded, count = shield_input_text(rewritten)
    return shielded, count

def shield_input_text(input_text):
    """
    Replaces any shielded words from shield_filter_words.json with ▆▆▆.
    Returns the filtered text and the number of words replaced.
    """
    count = 0
    pattern = re.compile(r'\b(' + '|'.join(re.escape(w) for w in shield_words) + r')\b', re.IGNORECASE)
    
    def replacer(match):
        nonlocal count
        count += 1
        return "▆▆▆"

    filtered = pattern.sub(replacer, input_text)
    return filtered, count
