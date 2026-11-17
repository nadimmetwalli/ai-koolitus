"""Kontrollib, et kõik on valmis: Python, paketid, API võti ja mudel.

Käivitamine:   python check.py      (Macis: python3 check.py)
Kui näed lõpus "KÕIK OK", oled valmis.
"""
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

print(f"1/4 Python {sys.version.split()[0]}", end=" ... ")
if sys.version_info < (3, 10):
    sys.exit("liiga vana. Vaja on Python 3.10 või uuem (python.org/downloads).")
print("ok")

print("2/4 Paketid", end=" ... ")
try:
    from dotenv import load_dotenv
    from google import genai
except ImportError:
    sys.exit("puuduvad. Käivita:  python -m pip install -r requirements.txt")
print("ok")

print("3/4 API võti (.env)", end=" ... ")
load_dotenv(Path(__file__).parent / ".env")
key = os.getenv("GEMINI_API_KEY", "")
if not key or "paste" in key.lower():
    sys.exit("ei leitud. Kopeeri .env.example failiks .env ja pane sinna oma võti (README.md samm 0).")
print("ok")

model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
print(f"4/4 Mudel {model}", end=" ... ")
client = genai.Client(api_key=key)
try:
    reply = client.models.generate_content(model=model, contents="Ütle ühe lausega tere eesti keeles.")
except Exception as e:
    print("viga")
    print(f"\n{e}\n")
    print("Mida teha:")
    print(" - 'API key not valid' -> kopeeri võti uuesti, ilma tühikute ja jutumärkideta.")
    print(" - '404' või 'not found' -> mudeli nimi on vale. Mudelite loend:\n")
    try:
        for m in client.models.list():
            print("     ", m.name.replace("models/", ""))
    except Exception:
        print("      (loendit ei saanud kätte, vaata aistudio.google.com)")
    print("\n   Pane sobiv nimi faili .env reale GEMINI_MODEL=...")
    print(" - '429' või 'quota' -> proovi mõne sekundi pärast uuesti või vali teine mudel.")
    sys.exit(1)
print("ok")
print(f"\nMudel vastas: {reply.text.strip()}")
print("\nKÕIK OK. Oled valmis!")
