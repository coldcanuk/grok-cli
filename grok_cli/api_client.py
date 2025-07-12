"""API client functions for Grok CLI."""

import json
import sys
import time
import random
import requests
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

API_URL = "https://api.x.ai/v1/chat/completions"

# Fun waiting messages for rate limiting
WAIT_MESSAGES = [
    "🚀 Sending space bits to Grok...",
    "🚽 Waiting for Grok to get out of the bathroom...",
    "🧠 Giving Grok time to grok your request...",
    "☕ Grok is making coffee, be right back...",
    "🎮 Grok is speedrunning your request...",
    "🌮 Grok stepped out for tacos, uno momento...",
    "🧘 Grok is meditating on your query...",
    "🎸 Grok is tuning their neural guitar...",
    "🌌 Recalibrating the space-time continuum...",
    "🦾 Grok is doing push-ups to warm up...",
    "🎲 Rolling dice to determine response order...",
    "🔮 Consulting the crystal ball API...",
    "🏃 Grok is running laps around the data center...",
    "🎪 The circus of consciousness is preparing...",
    "🌈 Painting rainbows in the cloud...",
    "🎯 Aiming for the perfect response...",
    "🚁 Grok's neurons are taking a helicopter tour...",
    "🎨 Grok is artistically crafting your answer...",
    "🏗️ Building bridges between bits and bytes...",
    "🎭 The AI drama club is rehearsing..."
]

def api_call(key, messages, model, stream, tools=None, retry_count=0):
    """Make an API call to Grok API with retry logic."""
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = {"messages": messages, "model": model, "stream": stream}
    
    if tools:
        data["tools"] = tools
        data["tool_choice"] = "auto"  # Let Grok decide when to use tools
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, stream=stream, timeout=(10, 60))
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:  # Rate limit
            retry_count += 1
            
            # Check for Retry-After header (can be seconds or HTTP date)
            retry_after = e.response.headers.get('Retry-After')
            if retry_after:
                try:
                    # Try to parse as integer (seconds)
                    wait_time = int(retry_after)
                except ValueError:
                    # Try to parse as HTTP date
                    try:
                        retry_date = parsedate_to_datetime(retry_after)
                        wait_time = max(0, (retry_date - datetime.now(timezone.utc)).total_seconds())
                    except:
                        # Fallback to exponential backoff
                        wait_time = min(5 * (2 ** (retry_count - 1)) + random.random() * 3, 60)
            else:
                # No Retry-After header, use exponential backoff with jitter
                wait_time = min(5 * (2 ** (retry_count - 1)) + random.random() * 3, 60)
            
            # Select a fun message
            msg_index = retry_count % len(WAIT_MESSAGES)
            print(f"\n{WAIT_MESSAGES[msg_index]}")
            print(f"Rate limit hit. Waiting {wait_time:.1f} seconds... (attempt {retry_count}/10)")
            
            if retry_count >= 10:
                print("\n💡 Tip: Consider spreading out your requests or upgrading your API tier.")
                sys.exit("API Error: Too many rate limit retries. Please try again later.")
            
            # Show a progress bar
            show_progress_bar(wait_time)
            
            return api_call(key, messages, model, stream, tools, retry_count)
        elif e.response.status_code >= 500:  # Server error
            retry_count += 1
            if retry_count >= 3:
                sys.exit(f"API Error: Server error persists after {retry_count} retries. Status: {e.response.status_code}")
            print(f"\n💤 Grok seems sleepy (error {e.response.status_code}). Giving them a moment... (attempt {retry_count}/3)")
            time.sleep(5 * retry_count)
            return api_call(key, messages, model, stream, tools, retry_count)
        else:
            # Other HTTP errors
            error_msg = f"API Error: HTTP {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail.get('error', {}).get('message', str(error_detail))}"
            except:
                error_msg += f" - {e.response.text[:200]}"
            sys.exit(error_msg)
    except requests.exceptions.Timeout:
        sys.exit("API Error: The request timed out. The server may be slow or unreachable.")
    except requests.exceptions.RequestException as e:
        sys.exit(f"API Error: {e}. Check your network connection and API key.")

def show_progress_bar(wait_time):
    """Display a progress bar for the wait time."""
    start_time = time.time()
    while time.time() - start_time < wait_time:
        elapsed = time.time() - start_time
        progress = int((elapsed / wait_time) * 20)
        bar = "█" * progress + "░" * (20 - progress)
        remaining = wait_time - elapsed
        print(f"[{bar}] {remaining:.1f}s remaining", end="\r", flush=True)
        time.sleep(0.1)
    print(" " * 50, end="\r")  # Clear the progress bar

def show_thinking_message():
    """Display a fun thinking message during response generation."""
    import json
    import random
    import os

    thinking_path = os.path.join(os.path.dirname(__file__), "thinking.json")
    messages = []
    try:
        with open(thinking_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Accept either a list of dicts with 'message', or a list of strings
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict) and "message" in data[0]:
                    messages = [entry["message"] for entry in data if "message" in entry]
                elif isinstance(data[0], str):
                    messages = data
    except Exception as e:
        messages = ["Grok is thinking..."]

    if not messages:
        messages = ["Grok is thinking..."]

    message = random.choice(messages)
    print(f"\n{message}")

def show_startup_message():
    """Display a fun startup message."""
    import json
    import random
    import os
    
    startup_path = os.path.join(os.path.dirname(__file__), "startup.json")
    startup_messages = []
    try:
        with open(startup_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict) and "message" in data[0]:
                    startup_messages = [entry["message"] for entry in data if "message" in entry]
                elif isinstance(data[0], str):
                    startup_messages = data
    except Exception:
        startup_messages = ["Grok is starting up..."]
    if not startup_messages:
        startup_messages = ["Grok is starting up..."]
    print(f"\n{random.choice(startup_messages)}\n")
