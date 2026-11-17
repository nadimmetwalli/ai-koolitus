# Sponsoriagent: ehita oma esimene AI-agent

Agent, mis loeb sinu päris sponsoritabeli (Google Sheets'ist alla laetud .xlsx), leiab sinu ettevõtted ja valmistab sulle ette e-kirjade mustandid koos manustega. **Saadad ikka sina.**
Samu samme (kaardista, juhised, tööriistad, jooksuta, inimene kinnitab) kasutad hiljem mis tahes agendi jaoks.

Repo kaasas olev tabel (`data/sponsors_sample.csv`) on väljamõeldud harjutustabel. Päris tabeli ja päris failid paned sa ise oma arvutisse (samm 0.6). **Need ei lähe kunagi GitHubi**: `.gitignore` hoiab neid eemal.

---

## Samm 0: seadistus

### 0.1 Python
Lae alla [python.org/downloads](https://www.python.org/downloads/) ja paigalda.
**Windows: esimesel ekraanil märgi linnuke "Add python.exe to PATH".** Kontrolli uues terminaliaknas:

| Windows | Mac |
|---|---|
| `python --version` | `python3 --version` |

Vaja on 3.10 või uuemat.

### 0.2 Repo
Kõige lihtsam: GitHubis **Code → Download ZIP**, paki lahti ja ava kaust terminalis (või VS Code'is: *File → Open Folder*, siis *Terminal → New Terminal*).
Git'iga: `git clone <repo-aadress>`.

### 0.3 Paketid
| Windows | Mac |
|---|---|
| `python -m pip install -r requirements.txt` | `python3 -m pip install -r requirements.txt` |

Macis vigaga "externally-managed-environment"? Vaata `TORKED.md`.

### 0.4 API võti
1. Ava [aistudio.google.com](https://aistudio.google.com) ja logi sisse Google'i kontoga.
2. Vali **Get API key** ja loo uus võti. Kopeeri see.
3. Tee `.env.example` koopia nimega `.env` (Windows: `copy .env.example .env`, Mac: `cp .env.example .env`).
4. Ava `.env` ja asenda `paste-your-key-here` oma võtmega. Ilma jutumärkide ja tühikuteta.

**Võti on parool.** Ära pane seda GitHubi, vestlusesse, ekraanipildile ega Discordi. Fail `.env` on `.gitignore`'is, nii et git seda ei võta.

### 0.5 Kontroll
| Windows | Mac |
|---|---|
| `python check.py` | `python3 check.py` |

Kui lõpus on **KÕIK OK**, oled valmis. Kui ei, vaata `TORKED.md`.

### 0.6 Oma tabel, manused ja projekti info
1. **Tabel:** ava oma sponsoritabel Google Sheets'is ja vali **File → Download → Microsoft Excel (.xlsx)**. Pane see fail kausta `data/` (nimi pole oluline). Kui seal on oma tabel, loeb agent seda, mitte harjutustabelit.
2. **Manused:** pane failid, mida kirjadele lisada (nt koostööpakett PDF-ina), kausta `attachments/`. Anna neile selged nimed (`koostoopakett.pdf`), sest agent näeb failide nimesid, mitte sisu.
3. **Projekt:** ava `projekt.md` ja kirjuta sinna oma organisatsioon, projekt, lühikirjeldus ja ettepanek. Sõnad "ASENDA" peavad kaduma.
4. **Kontroll:** `python check_sheet.py` (Macis `python3 check_sheet.py`). See näitab, millist faili loetakse, kas veerud leiti ja mitu rida on igal marketeril. Prindib ainult arvud, mitte kontakte.

Tabelis peavad olema veerud **Ettevõte, Marketer, Kas on kontakteerutud?, Kas on reganud?, Meiliaadress** (ka Valdkond, Kuupäev/deadline ja Märkused/kommentaarid kasutatakse). Veidi teised nimed (nt "E-post") tunneb agent ära, vaata `HEADER_ALIASES` failis `tools.py`. Linnukesed (checkbox) sobivad JAH/EI asemel. Kui päis ei ole esimesel real või tabelis on mitu lehte, leiab agent õige koha ise.

**Andmekaitse:** agendile antakse ainult **sinu enda read**, mitte kogu tabel. Ikkagi saadetakse need Google'i Gemini API-le. Tasuta tasemel võib Google sisu kasutada toodete parendamiseks (vaata AI Studio tingimusi). Ära pane tabelisse ega märkustesse midagi, mida ettevõtte kontaktisikud ei tohiks Google'isse sattuda, ja küsi üle, mida sinu organisatsioon lubab.

**Otse lingiga (valikuline):** kui tabel on jagatud lingiga ("Anyone with the link: Viewer"), võid `.env` faili lisada `SHEET_URL=<tabeli link>`. Siis laeb agent selle ise alla. Isiklikuks sponsoritabeliks soovitame pigem alla laadida.

---

## Sammud (ehitame koos)

### Samm 1: kaardista protsess (kaardil, mitte koodis)
Kirjuta paberile: mis on käsitsi töö sammud? *Leia oma read → vaata, mis staatuses firma on → vali õige kiri → vali sobiv manus → täida mall → pane mustandiks.*
Millises kohas peab otsustama inimene? (Meil: iga kiri enne saatmist.)

### Samm 2: kirjuta juhised (`prompt.md`)
Täida failis kõik **TODO** kohad: roll, ülesanne, reeglid, väljund.
Hea reegel on konkreetne ja katab koha, kus midagi võib valesti minna.

### Samm 3: kirjuta tööriist (`tools.py`)
Tööriist on tavaline funktsioon, mille mudel ise valib ja kutsub. Täida `find_rows` TODO.
Teised kolm tööriista (`list_attachments`, `get_template`, `save_draft`) on valmis. Kontrolli ilma API-ta: `python test_tools.py` (Macis `python3 test_tools.py`). See jookseb harjutustabeli peal, ka siis, kui sul on oma tabel.

### Samm 4: jooksuta ja paranda
| Windows | Mac |
|---|---|
| `python agent.py Mari` | `python3 agent.py Mari` |

Vaata terminalis, millal agent mida kutsub. Millal läks midagi valesti? Paranda **juhised** (`prompt.md`) või **tööriist** (`tools.py`) ja jooksuta uuesti.
Oma tabeliga kasuta oma nime nii, nagu see tabeli veerus "Marketer" on. Harjutustabeliga proovi ka Karl, Liis, Jaan.

### Samm 5: inimene kinnitab
Mustandid on kaustas `drafts/`. Iga firma kohta on kaks faili:
- `.eml` on valmis kiri koos manustega. Topeltklõps avab selle e-posti programmis (Outlook avab selle muudetava mustandina). Loe läbi, vajadusel muuda ja saada ise.
- `.txt` on sama kiri tavatekstina, kus on kirjas ka manuste nimed. Kasuta seda, kui `.eml` sinu arvutis ei avane (nt Gmail'i veebis): kopeeri tekst kirja ja lisa manused ise.

Agendil pole tööriista kirja saatmiseks. See on teadlik piire.

---

## Kui jäid maha
- `solution/prompt.md` ja `solution/tools.py` on valmis lahendused. Kopeeri need `prompt.md` ja `tools.py` asemele ja liigu edasi.
- Proovi esmalt ise: sama probleemi lahendad tööl ja hackathonil ka ilma lahenduseta.

## Faili kaart
| Fail | Mis see on |
|---|---|
| `prompt.md` | agendi juhised (sinu kirjutatud) |
| `tools.py` | tööriistad, mida mudel kutsub |
| `agent.py` | käivitab mudeli juhiste ja tööriistadega |
| `templates/` | e-kirja mallid |
| `data/` | siia paned oma tabeli (.xlsx); `sponsors_sample.csv` on harjutustabel |
| `attachments/` | siia paned manused (PDF jne) |
| `projekt.md` | sinu projekti info, mida mallid kasutavad |
| `drafts/` | siia tulevad mustandid |
| `check.py`, `check_sheet.py`, `test_tools.py` | kontrollid (võti, tabel, tööriistad) |

## Edasi: hackathon
Samad viis sammu, sinu enda probleem: mis protsessi sa BEST-is kordad iga nädal?
Mõtteid: koosolekumärkmed → ülesanded, uudiskiri mustand, osalejate meeldetuletused, sponsoritele aruanne.
