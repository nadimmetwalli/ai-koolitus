"""Isekontroll sammu 3 jaoks. Ei vaja API võtit ega internetti.

Käivitamine:   python test_tools.py      (Macis: python3 test_tools.py)
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import tools

tools.SHEET = tools.SAMPLE  # testid jooksevad alati harjutustabeli peal, ka siis kui sul on data/ kaustas oma tabel

failed = 0


def check(label: str, ok: bool, hint: str = "") -> None:
    global failed
    print(("  OK    " if ok else "  VIGA  ") + label + ("" if ok else f"   <- {hint}"))
    if not ok:
        failed += 1


print("find_rows (sinu kood):")
for name, expected in [("Mari", 4), ("mari tamm", 4), ("Karl K.", 3), ("Liis", 3), ("Jaan T", 3), ("Tundmatu Tegelane", 0)]:
    got = tools.find_rows(name)["count"]
    check(f"{name!r} -> {expected} rida", got == expected, f"sain {got}")
check("tühja nime puhul ei leita midagi", tools.find_rows("")["count"] == 0, "tühi nimi ei tohi sobida tühja Marketer lahtriga")

print("\nE-posti puhastamine (valmis kood):")
cases = [
    ("info@firma.example", "", ["info@firma.example"]),
    ("", "puudub", []),
    ("a@firma.example; b@firma.example", "mitu aadressi", ["a@firma.example", "b@firma.example"]),
    ("Priit Tamm priit@firma.example,", "", ["priit@firma.example"]),
    ("kontakt@pakend.examplekontakt2@pakend.example", "vigane (kokku kleepunud või poolik aadress)", None),
]
for raw, problem, emails in cases:
    r = tools.clean_emails(raw)
    ok = r["email_probleem"] == problem and (emails is None or r["emails"] == emails)
    check(repr(raw), ok, f"sain {r}")

print("\nExcel ja manused (valmis kood, ajutistel failidel):")
import email
import tempfile
from datetime import datetime
from email import policy
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    try:
        from openpyxl import Workbook

        wb = Workbook()
        wb.active.title = "Märkmed"
        wb.active["A1"] = "see leht pole tabel"
        ws = wb.create_sheet("Sponsorid")
        ws.append(["Sponsorite loend 2026"])  # päis ei ole esimesel real
        ws.append(["Firma", "Vastutaja", "Kontakteeritud", "Reageerinud", "E-post", "Deadline"])
        ws.append(["Test OÜ", "Mari Tamm", True, False, "info@test.example", datetime(2026, 11, 20)])
        ws.append([None, None, None, None, None, None])
        wb.save(tmp / "tabel.xlsx")
        tools.SHEET = tmp / "tabel.xlsx"
        rows = tools._read_rows()
        r = tools._summarise(rows[0]) if rows else {}
        check("xlsx: leiab päise ja õige lehe", len(rows) == 1, f"sain {len(rows)} rida")
        check("xlsx: veerunimed ja linnukesed (TRUE/FALSE)", r.get("kontakteeritud") == "JAH" and r.get("reageerinud") == "EI", f"sain {r}")
        check("xlsx: kuupäev kujul 20/11/2026", r.get("deadline") == "20/11/2026", f"sain {r.get('deadline')!r}")
    except ImportError:
        check("openpyxl on paigaldatud", False, "python -m pip install -r requirements.txt")
    finally:
        tools.SHEET = tools.SAMPLE

    tools.ATTACHMENTS, tools.DRAFTS = tmp / "att", tmp / "drafts"
    tools.ATTACHMENTS.mkdir()
    (tools.ATTACHMENTS / "koostoopakett.pdf").write_bytes(b"%PDF-1.4 test")
    check("list_attachments leiab faili", tools.list_attachments()["count"] == 1)
    res = tools.save_draft("Test OÜ", "info@test.example", "Tere", "Tekst", ["koostoopakett.pdf"])
    saved = tools.DRAFTS / "test-ou.eml"
    ok = saved.exists() and res.get("attached") == ["koostoopakett.pdf"]
    if ok:
        msg = email.message_from_bytes(saved.read_bytes(), policy=policy.default)
        ok = msg["To"] == "info@test.example" and [a.get_filename() for a in msg.iter_attachments()] == ["koostoopakett.pdf"]
    check("save_draft teeb .eml koos manusega", ok, f"sain {res}")
    check("save_draft ei luba olematut faili", "error" in tools.save_draft("X", "a@b.example", "T", "t", ["../secret.pdf"]))
    check("save_draft ei luba vigast aadressi", "error" in tools.save_draft("X", "pole-aadress", "T", "t"))
    tools.save_draft("Ilma OÜ", "a@b.example", "T", "t")
    check("save_draft töötab ka ilma manuseta", (tools.DRAFTS / "ilma-ou.eml").exists())

print()
if failed:
    print(f"{failed} kontrolli ebaõnnestus. Vaata tools.py -> find_rows ja proovi uuesti.")
    sys.exit(1)
print("Kõik korras. Tööriistad töötavad. Edasi: python agent.py <sinu nimi>")
