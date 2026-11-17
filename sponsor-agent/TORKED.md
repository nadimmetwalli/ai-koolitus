# Tõrked ja lahendused

| Mida näed | Mis juhtus | Mida teha |
|---|---|---|
| `python` ei tööta / "not found" (Windows) | Python ei ole PATH-is | Paigalda uuesti ja märgi "Add python.exe to PATH". Proovi ka `py` `python` asemel. |
| `python` näitab 2.x (Mac) | Vana süsteemi-Python | Kasuta `python3` |
| `ModuleNotFoundError: No module named 'google'` | Paketid on paigaldamata | `python -m pip install -r requirements.txt` (Macis `python3 -m pip ...`) |
| `externally-managed-environment` (Mac) | Homebrew Python keelab globaalse paigaldamise | `python3 -m venv .venv`, siis `source .venv/bin/activate`, siis uuesti pip install. Edaspidi aktiveeri enne igat sessiooni. |
| `pip` ei ole tuntud | Vale pip | Kasuta alati `python -m pip ...` |
| PowerShell: "running scripts is disabled" (venv'i aktiveerimisel) | Windowsi poliitika | Ära kasuta venv'i Windowsis, paigalda otse. |
| `check.py`: "ei leitud" võtme juures | `.env` puudub või on vales kaustas | Fail peab olema samas kaustas kui `check.py`. Windowsis vaata, et see ei ole `.env.txt`. |
| `API key not valid` | Võti kopeeriti valesti | Kopeeri uuesti, ilma tühikute ja jutumärkideta. |
| `404` / "model not found" | Mudeli nimi on aegunud | `check.py` prindib mudelite loendi. Pane sobiv nimi `.env` faili `GEMINI_MODEL=` reale. |
| `429` / "quota" | Liiga palju päringuid | Oota minut, proovi uuesti. Kui kordub, vali teine mudel. |
| `leidsin 0 rida` | `find_rows` TODO on tegemata või nimi ei sobi | Jooksuta `python test_tools.py` |
| `check_sheet.py`: "PUUDU" veeru juures | Tabelis on veerg teise nimega | Lisa nimi `tools.py` → `HEADER_ALIASES` |
| "Ei saa faili ... lugeda" | Fail on Excelis lukus | Sulge Excel või tee koopia |
| "Tundmatu failitüüp" | Fail on .xls, .numbers või Google Sheets'i link | Google Sheets'is: File → Download → Microsoft Excel (.xlsx) |
| Agent loeb vale tabelit (harjutustabelit) | Sinu fail ei ole kaustas `data/` | Pane .xlsx kausta `data/`. `check_sheet.py` näitab, mida loetakse. |
| Agent ei lisa manust | Kaustas `attachments/` pole faili, või `prompt.md`-s pole manuse reeglit | `check_sheet.py` näitab manuseid. Lisa reegel: millal milline fail. |
| `.eml` ei avane | Arvutis pole e-posti programmi | Kasuta sama nimega `.txt` faili: kopeeri tekst, lisa manused ise |
| "projekt.md on veel täitmata" | Sõna "ASENDA" on veel failis | Kirjuta oma projekti info ja kustuta "ASENDA" |
| Agent kirjutab kirju ilma sinu reegliteta | `prompt.md` TODO-d on tühjad | Täida need |
| Terminalis "Viga: ..." | `agent.py` püüab vead kinni ja näitab lühikest veateadet | Loe veateksti, enamasti on seal vihje (võti, mudeli nimi, limiit) |

## Võtme lekkimise korral
Kui panid võtme kogemata kuhugi avalikku: mine AI Studios, **kustuta see võti** ja tee uus.
