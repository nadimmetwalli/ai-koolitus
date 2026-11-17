"""Agendi tööriistad.

Tööriist on tavaline Pythoni funktsioon. Mudel ei näe funktsiooni koodi, vaid ainult:
  * funktsiooni nime,
  * docstringi (tekst kolme jutumärgi vahel, nagu see siin),
  * parameetrite nimesid ja tüüpe.

Kui mudel otsustab tööriista kutsuda, käivitab teek funktsiooni SINU arvutis ja annab
tulemuse mudelile tagasi. Seepärast on docstring tegelikult juhend mudelile: kirjuta see hoolikalt.

Jaotus: kõike, mis on täpne (aadresside puhastamine, failid), teeb kood.
Mudel teeb seda, milles ta on tugev: keelt ja otsustamist.
"""
import csv
import mimetypes
import os
import re
import unicodedata
from datetime import date, datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SAMPLE = DATA / "sponsors_sample.csv"  # väljamõeldud harjutustabel
SHEET = None  # None = leia tabel automaatselt (vaata _sheet_path). Testid panevad siia oma faili.
TEMPLATES = ROOT / "templates"
ATTACHMENTS = ROOT / "attachments"  # siia paned failid, mida kirjale manusena lisada (PDF jne)
DRAFTS = ROOT / "drafts"
PROJECT_FILE = ROOT / "projekt.md"  # sinu projekti päris info; get_template annab selle mudelile

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
KINDS = ("esmakontakt", "meeldetuletus")
MAX_ATTACH_MB = 15  # Gmail ja enamik teisi lubavad kokku umbes 25 MB; jätame varu

# Tabelis võivad veerunimed olla veidi teised kui meil. Siin on "meie nimi -> variandid".
# Kui sinu tabelis on mõni veerg teisiti kirjutatud, lisa see variant siia.
HEADER_ALIASES = {
    "Ettevõte": ["ettevõte", "ettevõtte nimi", "firma", "company"],
    "Valdkond": ["valdkond", "sektor"],
    "Kas on kontakteerutud?": ["kas on kontakteerutud?", "kas on kontakteeritud?", "kontakteerutud", "kontakteeritud"],
    "Kas on reganud?": ["kas on reganud?", "kas on reageerinud?", "reageerinud", "reganud", "vastanud"],
    "Marketer": ["marketer", "vastutaja", "õpilane", "tudeng"],
    "Telefon": ["telefon", "tel", "telefoninumber"],
    "Meiliaadress": ["meiliaadress", "e-post", "epost", "e-mail", "email", "meil"],
    "Kuupäev/deadline": ["kuupäev/deadline", "deadline", "kuupäev"],
    "Veebileht": ["veebileht", "koduleht", "website"],
    "Märkused/kommentaarid": ["märkused/kommentaarid", "märkused", "kommentaarid", "märkus"],
}
REQUIRED = ["Ettevõte", "Marketer", "Kas on kontakteerutud?", "Kas on reganud?", "Meiliaadress"]


def _log(msg: str) -> None:
    """Prindib terminali, mida agent parajasti teeb. Nii näed tsüklit oma silmaga."""
    print(f"  [tööriist] {msg}")


_downloaded = False


def _download_google_sheet(url: str) -> Path:
    """Valikuline: laeb Google Sheets'i tabeli .xlsx-ina alla (kord iga jooksutamise kohta).
    Töötab ainult siis, kui tabel on jagatud lingiga ("Anyone with the link: Viewer").
    Muidu lae tabel ise alla: File -> Download -> Microsoft Excel (.xlsx) ja pane kausta data/."""
    global _downloaded
    target = DATA / "google-sheet.xlsx"
    if _downloaded:
        return target
    import urllib.request

    m = re.search(r"/spreadsheets/d/([\w-]+)", url)
    if not m:
        raise RuntimeError("SHEET_URL ei näe välja nagu Google Sheets'i link (peaks sisaldama /spreadsheets/d/...).")
    export = f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=xlsx"
    _log("laen Google Sheets'i tabelit alla")
    try:
        with urllib.request.urlopen(export, timeout=30) as r:
            content = r.read()
    except Exception as e:
        raise RuntimeError(f"Google Sheets'i allalaadimine ebaõnnestus ({e}). Lae tabel ise alla: File -> Download -> .xlsx")
    if not content.startswith(b"PK"):  # xlsx on zip-fail; HTML tähendab sisselogimislehte
        raise RuntimeError("Tabel ei ole lingiga jagatud, Google küsis sisselogimist. Lae tabel ise alla: File -> Download -> .xlsx ja pane kausta data/.")
    DATA.mkdir(exist_ok=True)
    target.write_bytes(content)
    _downloaded = True
    return target


def _sheet_path() -> Path:
    """Millist tabelit loeme? 1) SHEET (testid), 2) SHEET_URL .env-is (Google Sheets'i link),
    3) SHEET_FILE .env-is, 4) uusim .xlsx/.csv kaustas data/ (v.a. harjutustabel), 5) harjutustabel.
    Tavaliselt piisab: lae oma Google Sheets'i tabel .xlsx-ina alla ja pane kausta data/."""
    if SHEET:
        return Path(SHEET)
    url = os.getenv("SHEET_URL", "").strip()
    if url:
        return _download_google_sheet(url)
    chosen = os.getenv("SHEET_FILE", "").strip()
    if chosen:
        return DATA / chosen if not Path(chosen).is_absolute() else Path(chosen)
    real = [
        p for p in DATA.glob("*")
        if p.suffix.lower() in (".xlsx", ".csv") and not p.name.startswith(("sponsors_sample", "~$", "."))
    ]
    if real:
        return max(real, key=lambda p: p.stat().st_mtime)
    return SAMPLE


def using_sample() -> bool:
    return _sheet_path().name.startswith("sponsors_sample")


def _norm(text) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _canonical(header: str) -> str:
    """'  E-post ' -> 'Meiliaadress'. Tundmatu veerg jääb oma nimega."""
    h = _norm(header)
    for name, variants in HEADER_ALIASES.items():
        if h == _norm(name) or h in variants:
            return name
    return str(header or "").strip()


def _cell(value) -> str:
    """Exceli lahter -> tavaline tekst. Kuupäevad kujul 20/11/2026, täisarvud ilma '.0'."""
    if value is None:
        return ""
    if isinstance(value, bool):  # Google Sheets'i linnukesed (checkbox) tulevad Excelisse tõeväärtusena
        return "JAH" if value else "EI"
    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _table_from_rows(raw_rows: list[list[str]]):
    """Leiab päiserea (esimese 15 rea seast) ja tagastab (päis, andmeread) või None."""
    for i, row in enumerate(raw_rows[:15]):
        names = {_canonical(c) for c in row}
        if "Ettevõte" in names and "Marketer" in names:
            return [_canonical(c) for c in row], raw_rows[i + 1:]
    return None


def _read_table(path: Path) -> tuple[list[str], list[list[str]], str]:
    """Loeb faili ja tagastab (päis, andmeread, lehe nimi)."""
    if not path.exists():
        raise RuntimeError(f"Tabelit ei leitud: {path}. Pane oma .xlsx või .csv kausta data/.")
    if path.suffix.lower() == ".xlsx":
        from openpyxl import load_workbook

        try:
            wb = load_workbook(path, read_only=True, data_only=True)
        except PermissionError:
            raise RuntimeError(f"Ei saa faili {path.name} lugeda. Sulge see Excelis või tee koopia.")
        wanted = os.getenv("SHEET_NAME", "").strip()
        sheets = [wb[wanted]] if wanted in wb.sheetnames else [wb.active] + [w for w in wb.worksheets if w is not wb.active]
        for ws in sheets:
            raw = [[_cell(c) for c in row] for row in ws.iter_rows(values_only=True)]
            found = _table_from_rows(raw)
            if found:
                return found[0], found[1], ws.title
        raise RuntimeError(
            f"Ühelgi lehel ei leitud päiserida, kus on veerud 'Ettevõte' ja 'Marketer'. Käivita: python check_sheet.py"
        )
    if path.suffix.lower() == ".csv":
        text = path.read_text(encoding="utf-8-sig")
        first = text.splitlines()[0] if text else ""
        delimiter = ";" if first.count(";") > first.count(",") else ","  # Eesti Excel salvestab csv sageli semikoolonitega
        raw = [[c.strip() for c in row] for row in csv.reader(text.splitlines(), delimiter=delimiter)]
        found = _table_from_rows(raw)
        if found:
            return found[0], found[1], path.name
        raise RuntimeError("CSV-s ei leitud päiserida, kus on veerud 'Ettevõte' ja 'Marketer'. Käivita: python check_sheet.py")
    raise RuntimeError(f"Tundmatu failitüüp {path.suffix!r}. Salvesta tabel kui .xlsx (Excelis: Save As) või .csv.")


def _read_rows() -> list[dict]:
    """Loeb tabeli (xlsx või csv) ja tagastab iga rea sõnastikuna: veerunimi -> väärtus.
    Veerunimed on viidud meie nimedele (vt HEADER_ALIASES), tühjad read jäetakse välja."""
    path = _sheet_path()
    header, data, _sheet = _read_table(path)
    _log(f"loen tabelit: {path.name}")
    rows = []
    for values in data:
        if not any(values):
            continue
        row = dict(zip(header, values))
        if row.get("Ettevõte", "").strip():
            rows.append(row)
    return rows


def _first_name(name: str) -> str:
    """'  Mari  Tamm ' -> 'mari'. Võrdluseks: väiketähed, üleliigsed tühikud ära, ainult eesnimi."""
    parts = re.sub(r"\s+", " ", (name or "").strip().lower()).split(" ")
    return parts[0]


def clean_emails(raw: str) -> dict:
    """Võtab tabeli e-posti lahtrist välja päris aadressid ja märgib, kui midagi on valesti.

    Tabelites on sageli prügi: kaks aadressi ühes lahtris, nime eesliide, koma lõpus,
    kokku kleepunud aadressid. Seda ei jäta me mudeli kätte, sest kood on siin täpsem.
    """
    raw = raw or ""
    matches = EMAIL_RE.findall(raw)
    found = []
    for e in matches:
        e = e.lower().rstrip(".")
        if e not in found:
            found.append(e)
    if not raw.strip():
        problem = "puudub"
    elif not found:
        problem = "vigane"
    elif raw.count("@") > len(matches):
        problem = "vigane (kokku kleepunud või poolik aadress)"
    elif len(found) > 1:
        problem = "mitu aadressi"
    else:
        problem = ""
    return {"emails": found, "email_probleem": problem}


def _yes_no(value: str) -> str:
    """'jah', 'TRUE', 'x', '✓' -> 'JAH'; tühi, 'ei', 'FALSE' -> 'EI'. (Google Sheets'i linnukesed on TRUE/FALSE.)"""
    return "JAH" if _norm(value) in ("jah", "true", "yes", "x", "✓", "1", "j") else "EI"


def _summarise(row: dict) -> dict:
    """Teeb tabeli rea mudelile sobivaks: lühike, selged võtmed, puhastatud e-post."""
    out = {
        "ettevõte": row.get("Ettevõte", "").strip(),
        "valdkond": row.get("Valdkond", "").strip(),
        "kontakteeritud": _yes_no(row.get("Kas on kontakteerutud?", "")),
        "reageerinud": _yes_no(row.get("Kas on reganud?", "")),
        "deadline": row.get("Kuupäev/deadline", "").strip(),
        "märkused": row.get("Märkused/kommentaarid", "").strip(),
    }
    out.update(clean_emails(row.get("Meiliaadress", "")))
    return out


# --------------------------------------------------------------------------------------
# TÖÖRIIST 1: tabelist ridade leidmine
# --------------------------------------------------------------------------------------
def find_rows(student_name: str) -> dict:
    """Leia tabelist kõik ettevõtted, mille "Marketer" veerus on see õpilane.

    Args:
        student_name: õpilase nimi nii, nagu ta selle kirjutas (nt "Mari" või "Mari Tamm").

    Returns:
        count: mitu rida leiti.
        rows: ettevõtete read (ettevõte, valdkond, kontakteeritud, reageerinud, deadline,
              märkused, emails, email_probleem). Märkused on sisemised, mitte kirja jaoks.
    """
    _log(f"find_rows(student_name={student_name!r})")
    rows = []

    # TODO (samm 3): käi läbi _read_rows() ja lisa rows-i need read (läbi _summarise),
    # mille "Marketer" veerg vastab student_name'ile.
    # Vihje: võrdle eesnimesid (_first_name), nii et "mari tamm", "Mari" ja "Mari T."
    # annavad kõik sama tulemuse. Tabelis kirjutavad inimesed nime igat moodi.

    _log(f"leidsin {len(rows)} rida")
    return {"count": len(rows), "rows": rows}


# --------------------------------------------------------------------------------------
# TÖÖRIIST 2: e-kirja mall
# --------------------------------------------------------------------------------------
def get_template(kind: str) -> dict:
    """Loe e-kirja mall ja projekti info. Mall näitab, mida kiri peab sisaldama ja millises toonis.

    Args:
        kind: "esmakontakt" (firmaga pole veel ühendust võetud) või
              "meeldetuletus" (kiri on saadetud, aga vastust pole tulnud).

    Returns:
        template: malli tekst. Asenda {{...}} kohad päris väärtustega.
        projekti_info: organisatsiooni ja projekti andmed, mida kirjas kasutada.
    """
    _log(f"get_template(kind={kind!r})")
    if kind not in KINDS:
        return {"error": f"Tundmatu mall {kind!r}. Vali üks: {', '.join(KINDS)}."}
    info = PROJECT_FILE.read_text(encoding="utf-8") if PROJECT_FILE.exists() else ""
    return {"kind": kind, "template": (TEMPLATES / f"{kind}.md").read_text(encoding="utf-8"), "projekti_info": info}


# --------------------------------------------------------------------------------------
# TÖÖRIIST 3: manustatavad failid
# --------------------------------------------------------------------------------------
def _attachment_files() -> list[Path]:
    if not ATTACHMENTS.exists():
        return []
    return sorted(p for p in ATTACHMENTS.iterdir() if p.is_file() and not p.name.startswith((".", "~$")) and p.name != "README.md")


def list_attachments() -> dict:
    """Näita, milliseid faile saab kirjale manusena lisada (nt koostööpakett, tutvustus PDF-ina).
    Faili nimi ütleb, mis see on. Lisa manuseks ainult neid faile, mis siin loendis on.

    Returns:
        count: mitu faili on saadaval.
        files: loend {name, size_kb}.
    """
    _log("list_attachments()")
    files = [{"name": p.name, "size_kb": round(p.stat().st_size / 1024)} for p in _attachment_files()]
    _log(f"manuseid saadaval: {len(files)}")
    return {"count": len(files), "files": files}


# --------------------------------------------------------------------------------------
# TÖÖRIIST 4: mustandi salvestamine (EI saada kirja)
# --------------------------------------------------------------------------------------
def save_draft(company: str, to: str, subject: str, body: str, attachments: Optional[list[str]] = None) -> dict:
    """Salvesta e-kirja MUSTAND kausta drafts/ (.eml fail, mille saab e-posti programmis avada,
    koos manustega, ja .txt koopia). See tööriist ei saada midagi.

    Args:
        company: ettevõtte nimi (kasutatakse failinimes).
        to: ühe adressaadi e-posti aadress, mille find_rows tagastas.
        subject: kirja teema.
        body: kirja tekst, mallist täidetud, ilma {{...}} kohtadeta.
        attachments: manuste failinimed täpselt nii, nagu list_attachments need tagastas. Võib puududa.

    Returns:
        saved: failide teed, attached: lisatud manused, või error: mis valesti läks.
    """
    names = list(attachments or [])
    _log(f"save_draft(company={company!r}, to={to!r}, manuseid={len(names)})")
    if not EMAIL_RE.fullmatch(to.strip()):
        return {"error": f"{to!r} ei ole kehtiv e-posti aadress. Kasuta ainult find_rows aadresse."}
    if "{{" in body or "}}" in body:
        return {"error": "Kirjas on veel täitmata {{...}} kohti. Täida need ja proovi uuesti."}

    available = {p.name: p for p in _attachment_files()}
    unknown = [n for n in names if n not in available]
    if unknown:
        return {"error": f"Neid manuseid pole: {unknown}. Saadaval on: {sorted(available)}. Kasuta list_attachments nimesid täpselt."}
    files = [available[n] for n in dict.fromkeys(names)]  # korduvad nimed välja
    if sum(f.stat().st_size for f in files) > MAX_ATTACH_MB * 1024 * 1024:
        return {"error": f"Manused on kokku üle {MAX_ATTACH_MB} MB. Lisa vähem või väiksemaid faile."}

    msg = EmailMessage()
    msg["To"] = to.strip()
    msg["Subject"] = subject.strip()
    msg["X-Unsent"] = "1"  # Outlook avab faili mustandina, mida saab muuta ja saata
    msg.set_content(body.strip() + "\n")
    for f in files:
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        msg.add_attachment(f.read_bytes(), maintype=maintype, subtype=subtype, filename=f.name)

    slug = unicodedata.normalize("NFKD", company).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-") or "mustand"
    DRAFTS.mkdir(exist_ok=True)
    eml = DRAFTS / f"{slug}.eml"
    eml.write_bytes(msg.as_bytes())
    txt = DRAFTS / f"{slug}.txt"  # loetav koopia: kui .eml ei avane, kopeeri tekst ja lisa manused käsitsi
    manused = ", ".join(f.name for f in files) or "(puuduvad)"
    txt.write_text(f"Kellele: {to.strip()}\nTeema: {subject.strip()}\nManused: {manused}\n\n{body.strip()}\n", encoding="utf-8")
    _log(f"salvestatud: {eml.name}")
    return {"saved": [f"drafts/{eml.name}", f"drafts/{txt.name}"], "attached": [f.name for f in files]}
