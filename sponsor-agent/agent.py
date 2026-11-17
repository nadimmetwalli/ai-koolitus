"""Sponsoriagent: valmistab õpilase ettevõtetele ette e-kirjade mustandid.

Käivitamine:   python agent.py Mari
(Windowsis `python`, Macis `python3`.)

Agendi tsükkel, mida teek meie eest jooksutab:

    mudel mõtleb        ->  "Kõigepealt vaatan, millised ettevõtted on Marile antud"
    mudel kutsub        ->  find_rows("Mari")
    me jooksutame       ->  tulemus läheb mudelile tagasi
    mudel vaatab        ->  "Kolm ettevõtet. Esimesele vajan malli ja manust."
    mudel kutsub        ->  list_attachments(), get_template("esmakontakt")  ... jne
    kuni mudel ütleb    ->  "Valmis" ja annab lõppvastuse

Iga tööriistakutse prinditakse terminali, nii näed tsüklit toimumas.
Agendil ei ole tööriista kirja SAATMISEKS. See on teadlik piire (guardrail).
"""
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # et õ, ä, ö, ü prinditaks Windowsis õigesti
except Exception:
    pass

try:
    from dotenv import load_dotenv
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit("Puudu on paketid. Käivita:  python -m pip install -r requirements.txt")

import tools

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")
DEFAULT_MODEL = "gemini-3.5-flash-lite"
MODEL = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or "paste" in api_key.lower():
        sys.exit("GEMINI_API_KEY puudub. Pane võti faili .env (vaata README.md samm 0) ja proovi uuesti.")

    name = " ".join(sys.argv[1:]).strip() or input("Mis on sinu nimi? ").strip()
    if not name:
        sys.exit("Nimi on vajalik.")

    if "ASENDA" in (ROOT / "projekt.md").read_text(encoding="utf-8"):
        sys.exit("Fail projekt.md on veel täitmata. Kirjuta sinna oma projekti päris info (README.md samm 0.6).")
    if tools.using_sample():
        print("NB! Loen harjutustabelit (väljamõeldud). Oma tabeli jaoks pane see kausta data/ (README.md samm 0.6).")

    system_prompt = (ROOT / "prompt.md").read_text(encoding="utf-8")  # <- see on agendi "iseloom" ja reeglid
    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[tools.find_rows, tools.list_attachments, tools.get_template, tools.save_draft],  # <- mudel näeb ainult neid
        temperature=0.3,
        # Vaikimisi lõpetab teek pärast 10 tööriistakutset. Meil on kutseid rohkem.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=60),
    )

    print(f"\nAgent ({MODEL}) alustab. Õpilane: {name}\n")
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Minu nimi on {name}. Valmista ette minu ettevõtete e-kirjade mustandid.",
        config=config,
    )
    print("\n--- AGENDI ARUANNE ---")
    print(response.text)
    print("\nMustandid on kaustas drafts/ (.eml fail avaneb e-posti programmis, manused sees). Vaata need üle enne saatmist.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # lihtne ja arusaadav veateade, mitte pikk traceback
        sys.exit(f"\nViga: {e}\n\nAbi: vaata TORKED.md")
