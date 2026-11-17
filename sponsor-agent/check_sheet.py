"""Kontrollib, et agent loeb sinu tabelit õigesti. Ei vaja API võtit ega internetti.

Käivitamine:   python check_sheet.py      (Macis: python3 check_sheet.py)
Prindib ainult arvud ja veerunimed, mitte kontaktandmeid, nii et seda võib ekraanil näidata.
"""
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import tools

try:
    path = tools._sheet_path()
    header, data, sheet = tools._read_table(path)
except Exception as e:
    sys.exit(f"\nViga: {e}")

print(f"Fail:  {path.name}" + ("   <- see on HARJUTUSTABEL. Oma tabeli jaoks lae see alla (.xlsx) ja pane kausta data/" if tools.using_sample() else ""))
print(f"Leht:  {sheet}")

missing = [c for c in tools.REQUIRED if c not in header]
print("\nVeerud, mis agendile vaja:")
for col in tools.REQUIRED:
    print(f"  {'OK   ' if col in header else 'PUUDU'}  {col}")
if missing:
    print("\nSinu tabelis on veerud:")
    for h in header:
        print(f"  - {h!r}")
    print(f"\nPuuduvad: {missing}. Kui sinu tabelis on sama veerg teise nimega, lisa see nimi tools.py -> HEADER_ALIASES.")
    sys.exit(1)

rows = tools._read_rows()
no_mail = sum(1 for r in rows if not tools._summarise(r)["emails"])
print(f"\nRidu kokku: {len(rows)}   (ilma e-postita: {no_mail})")
print("Ridu marketeri kohta (nii, nagu tabelis kirjutatud):")
for name, n in Counter(r.get("Marketer", "").strip() or "(tühi)" for r in rows).most_common():
    print(f"  {n:3d}  {name}")

print("\nKontakteeritud / vastanud (kogu tabelis):")
c = Counter((tools._summarise(r)["kontakteeritud"], tools._summarise(r)["reageerinud"]) for r in rows)
for (k, r), n in sorted(c.items()):
    print(f"  kontakteeritud={k:3s} reageerinud={r:3s}  {n}")

files = tools._attachment_files()
print(f"\nManused kaustas attachments/: {len(files)}" + ("" if files else "   (pole veel; pane sinna oma PDF-id, kui tahad neid kirjadele lisada)"))
for f in files:
    print(f"  - {f.name}  ({round(f.stat().st_size/1024)} KB)")

proj = tools.PROJECT_FILE.read_text(encoding="utf-8") if tools.PROJECT_FILE.exists() else ""
print("\nprojekt.md: " + ("VEEL TÄITMATA (kirjuta sinna oma projekti info)" if "ASENDA" in proj or not proj else "täidetud"))
print("\nKui arvud klapivad sinu tabeliga, oled valmis.")
