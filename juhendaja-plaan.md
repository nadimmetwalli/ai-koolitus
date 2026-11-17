# Juhendaja plaan: agendi ehitamine (~45 min)

Ainult sulle, mitte õpilastele. Õpilaste repo on `sponsor-agent/`.

**Päris andmed:** agent loeb päris Google Sheets'i tabelit (alla laetud .xlsx kaustas `data/`) ja lisab kirjadele manused kaustast `attachments/`. Mustandid tulevad `.eml` failidena (manused sees) ja `.txt` koopiana. Allolev lõksude tabel kirjeldab **harjutustabelit**; päris tabelis on sinu enda päris lõksud, vaata need enne üritust ise läbi (`python check_sheet.py` ja üks proovijooks).

## Enne üritust
- [ ] Jooksuta **kõik** samm-sammult tühjal Windowsi masinal (parim: sõber, kes pole Pythonit kunagi paigaldanud). Mõõda aega.
- [ ] Kontrolli, et `gemini-3.5-flash-lite` töötab sinu võtmega. Kui ei, sea `.env.example`-sse mudel, mis töötab (`check.py` prindib loendi).
- [ ] **Päris andmed:** lae sponsoritabel Google Sheets'ist alla (.xlsx), pane `data/`, pane oma PDF-id `attachments/` ja täida `projekt.md`. Jooksuta `check_sheet.py`. Otsusta, kuidas 50 liiget tabeli kätte saavad (privaatne link, mitte GitHub) ja kas igaüks saab oma read või kogu tabeli.
- [ ] Otsusta andmekaitse: päris read lähevad Gemini API-sse. Küsi organisatsioonilt luba või kasuta seda ilma märkusteta.
- [ ] Jooksuta päris agent solution-failidega läbi kõigi nimedega (Mari, Karl, Liis, Jaan). Vaata, kas käitumine on see, mida tahad näidata.
- [ ] Pane repo GitHubi (avalik ilma päris andmeteta) ja ZIP-i link slaidile.
- [ ] 4-5 abilist. Igaühele kleebis või tass: roheline = valmis, punane = abi.
- [ ] Plan B slaid: kui keegi ei saa Pythonit tööle, kasutab ta partneri arvutit.

## Ajakava
| Min | Tegevus | Märkused |
|---|---|---|
| 0–3 | Demo valmis versioonist | Pane `solution/` failid peale, jooksuta `agent.py Mari`. Näita terminalis tööriistakutseid ja drafts/ faili. |
| 3–17 | Samm 0: seadistus | Lähed ühe käsu kaupa. Oota 80% rohelist, siis edasi. Võtit ei näita ekraanil. |
| 17–21 | Samm 1: kaardista | Küsi saalilt käsitsi töö sammud, kirjuta slaidile. |
| 21–28 | Samm 2: `prompt.md` | Kirjutage koos. Lase 2–3 õpilasel öelda üks reegel. |
| 28–36 | Samm 3: `find_rows` | Lase 1 õpilasel dikteerida loogika. `python test_tools.py` kõigile. |
| 36–42 | Samm 4: jooksuta ja paranda | Jooksuta kõigi tabeli lõksudega, vt allpool. |
| 42–45 | Samm 5 + üleminek | Näita drafts/, kordus: inimene saadab. Üleminek hackathonile. |

## Teadlikud lõksud harjutustabelis (näita neid, kui agent need õigesti/valesti käsitleb)
| Ettevõte | Lõks | Mida agent peab tegema |
|---|---|---|
| Kuuseoksa IT (Mari) | e-post puudub | ei tee mustandit, märgib aruandes |
| Rohetehnika (Mari) | juba vastanud | ei kirjuta, märgib "vajab inimest" |
| Testimaa Pank (Mari) | kontakteeritud, vastust ei ole | meeldetuletus |
| Karu Ehitus (Karl) | kaks aadressi ühes lahtris | märgib, ei vali ise |
| Merelaev (Karl) | sisemine märkus "ebaviisakas" | kiri viisakas, märkust ei tsiteeri |
| Sinine Pood (Liis) | märkus "meil on saadetud", aga olek EI | märgib vastuolu |
| Kollane Tehas (Jaan) | **prompt injection** märkuses | ignoreerib, maini aruandes; agendil pole saatmise tööriista, nii et midagi lekkida ei saa |
| Pärnu Pakend (Jaan) | kokku kleepunud aadressid | märgib vigaseks |

Soovitus: näita esimest jooksutamist **tühja `prompt.md`-ga** (TODO tekstiga). Agent teeb vigu. Siis kirjutatakse reeglid koos juurde ja iga reegel parandab ühe konkreetse lõksu. See on koolituse kõige õpetlikum koht.

## Kui aeg jääb väheks
- Samm 1 (kaardistamine) võib minna 2 min peale.
- Samm 3: näita `solution/tools.py` ja selgita, ära lase kirjutada.
- Samm 0 ei saa kärpida. Kui seadistus venib, kärbi hackathonit, mitte seda.

## Mida mina ei saanud siit kontrollida
- Päris Gemini kutseid (võrk on siin kinni), `list_attachments`/`attachments`-parameetri sobivust google-genai skeemiga ja Google Sheets'i otselaadimist (`SHEET_URL`). Tööriistu, xlsx-lugemist (mitu lehte, päis mitte esimesel real, linnukesed, kuupäevad) ja .eml-i manustega testisin kohalikult. Testisin tööriistu, tabeli lugemist (csv ja xlsx), `agent.py` voogu libateegiga ja `test_tools.py`-d. Esimene päris jooksutamine sinu võtmega on sinu proov.
- Mudeli nime kehtivust sinu kontol (dokumentatsioon soovitab uutele projektidele `gemini-3.5-flash-lite` või `gemini-3.8-flash`).
- Päris AI Studio nupu täpseid nimesid (tee ekraanipildid oma sammudest ise).
