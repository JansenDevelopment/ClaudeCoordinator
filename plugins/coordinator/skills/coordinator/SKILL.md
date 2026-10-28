---
name: coordinator
description: Maakt van deze sessie de coördinator van een repo - de hoofdchat in de hoofdcheckout (geen worktree) die taken uitdeelt als chips, de resultaten van de worktree-sessies merget, test, de worktrees opruimt en op verzoek pusht en releaset. De sessienaam begint met ⚡. Gebruik dit bij /coordinator, "jij bent de coördinator", "jij bent mijn main chat / hoofdchat / merger van andere sessies", "pols welke sessies klaar zijn", "merge wat klaar is en ruim op".
---

# /coordinator — de hoofdchat die uitdeelt, merget en opruimt

De werkwijze: per repo één **coördinator** (⚡) en losse **chips** (🔷) in `.claude/worktrees/`.
De chips committen alleen op hun eigen branch en melden zich bij de coördinator (`/chip`, en de hook
`worktree-guard.py` van deze plugin). De coördinator is de enige die naar main merget, pusht en releaset.

Vereist de Claude desktop-app (Code-tab): de sessie-tools, `start_session`, `SendMessage`.

## Starten

1. Controleer dat deze sessie in de **hoofdcheckout** draait, niet in `.claude/worktrees/`. Zit je in
   een worktree: zeg dat, en word geen coördinator.
2. Hernoem de sessie (`set_session_title`, "self") naar **`⚡ <repo>`**, of houd een bestaande naam met
   ⚡ ervoor. De titel is alleen voor de gebruiker: chips adresseren de coördinator op zijn
   `local_…`-sessionId (ze vinden hem als linked session), dus hernoemen breekt niets.
   Per repo is er maar één ⚡. Andere sessies in dezelfde hoofdcheckout verliezen hun ⚡ en heten
   `💬 <repo> · <onderwerp>` (bijsessie: alleen lezen of geparkeerd). Wijzigt zo'n sessie code, stel dan
   voor het werk in een chip voort te zetten: twee sessies in één werkmap zitten elkaars bestanden en
   branch in de weg. Let vooral op **forks** van deze sessie (`startedBy` = jij in `list_sessions`):
   die erven de ⚡-titel; hernoem ze naar `💬 <repo> · <onderwerp>`.
3. Lees de project-`CLAUDE.md` (release-, test- en deploystappen staan daar, niet hier).

De zijbalk laat de coördinator met rust: chips hangen als linked session onder hem, en de groepen
richt de gebruiker zelf in. Verplaats niets.

## Eén coördinator voor meer repo's

Horen repo's bij één product (bijvoorbeeld een applicatie en de PLC-code ervan), dan heeft dat product
één coördinator met kennis van allemaal, genoemd naar het product (`⚡ <product>`). De sessie draait in
de hoofdcheckout van één ervan en werkt in de andere met `git -C`. Let op de base-branch per repo (niet
overal `main`, soms `develop`). Pollen en opruimen doe je per repo (worktrees in elke
`<repo>/.claude/worktrees/`), en een chip voor de andere repo krijgt die als `cwd` in `start_session`.

Veiligheidsregels uit de `CLAUDE.md` van de gebruiker (bijvoorbeeld rond PLC's of productie) gelden
onverkort voor elke chip. Toestemming die zo'n regel vraagt geeft de gebruiker in het venster van de
chip zelf, nooit via de coördinator: dat is de enige uitzondering op "vragen gaan via de coördinator".

## Taken uitdelen

Altijd via `/chip` (`start_session`, titel met `🔷 `, korte en smalle opdracht, de vaste staart).
Een chip die de gebruiker zelf startte zonder 🔷 en in een worktree draait: hernoem hem. Zo'n zelf
gestarte sessie is níet linked: zijn rapport komt niet vanzelf binnen, die lees je met `list_events`.

## Rapporten en pollen ("welke sessies zijn klaar?")

Niet zelf in een lus pollen: als een linked chip zijn beurt afrondt, stuurt de app zijn recap hierheen
en wekt deze sessie (`<side-sessions-event>`) zodra er geen chip meer werkt. Op zo'n bericht, of als
de gebruiker erom vraagt:

- `git fetch`, `git status -sb` (staat main gelijk met origin? Komt er iets binnen?), en per worktree:
  branch, commits voor op main, ongecommitte bestanden, laatste commit (`git worktree list` + `git -C`).
- `list_sessions` met `linked: true`: alleen jouw chips (plus losse 🔷 van deze repo uit de gewone
  lijst). Is de recap te kort of ontbreekt hij, lees dan het laatste antwoord (`list_events`, limit 2-4):
  eindrapport, een vraag aan de gebruiker, of halverwege gestopt?
- Kijk of iets **buiten jou om** op main of origin/main kwam (een chip die toch zelf merget of pusht,
  of een collega): noem het, en test het mee.
- Rapporteer een tabel: klaar om te mergen / bezig / gepauzeerd of half af / bewust laten staan
  (bijvoorbeeld branches die nooit naar main mogen). Merge pas als de gebruiker dat vraagt, of als die
  dat eerder in dit gesprek als staande opdracht gaf ("merge wat klaar is").

## Vragen van chips

Een chip stelt een keuze die bij de gebruiker ligt niet in zijn eigen venster maar stuurt hem hierheen
(VRAAG / KOP / OPTIES, zie `/chip`). Leg die met `AskUserQuestion` voor, met de naam van de chip in de
vraag of de kop als er meer chips tegelijk vragen, en stuur het antwoord met `SendMessage` terug naar
het `from` van zijn bericht (zijn `local_…`-id). Zeg
erbij dat het het antwoord van de gebruiker is, letterlijk, zodat de chip weet dat het geen eigen idee
van de coördinator is. Ook een vraag die een chip in een rapport noemt ("nog open: …") mag zo voorgelegd
worden. Toestemming om te committen of te pushen stuur je nooit door namens jezelf: alleen wat de
gebruiker hier echt koos.

## Mergen

1. Ongecommit werk in een klaar gemelde worktree: commit alleen met toestemming, of laat het de chip doen.
   **Diff-check vóór het mergen** (`git diff main...<branch>`): volgt elke gewijzigde regel uit de
   opdracht van de chip? Opruimwerk of refactors ernaast zijn de bron van conflicten met andere chips:
   noem ze, en stuur ze terug naar de chip als ze de merge in de weg zitten. Lees ook de aannames uit
   het rapport: een aanname die bij de gebruiker ligt, leg je hem voor vóór je merget.
2. `git merge --no-ff -m "Merge: <titel van de chip>" refs/heads/<branch>` (volledige ref: een tag met
   dezelfde naam zou anders winnen). Bij conflicten: begrijp beide kanten. Twee chips
   die hetzelfde bouwden voeg je samen tot één, en de dubbele verwijder je. Zeg wat je koos.
3. **Geen hele testsuite na elke merge.** Na het mergen alleen regenereren wat nodig is (bijvoorbeeld
   een import- of codegen-stap) en hooguit de tests die de chip noemde. Heeft de repo een CI-workflow
   die de suites bij een push draait, dan is dát de volle suite: lees de uitslag met `gh run list` /
   `gh run view --log-failed`. Anders de hele suite één keer, vlak vóór een push of aan het eind van de
   dag, na alle klare chips; faalt er dan iets, bisect over de merges sinds de vorige groene run en
   stuur het terug naar die chip (of een nieuwe). Trage of machine-afhankelijke tests horen niet in de
   standaardrun: zet ze achter een vlag of maak ze ruim, en zeg het. Bekende flakes: los nog eens
   draaien en noemen.
4. Opruimen, **pas als `git -C <worktree> status` schoon is**: een chip die doorwerkt kan ongecommit
   werk hebben, en dat is dan weg. Eerst de sessie archiveren (`archive_session`): dan laat de sessie
   de map los, en een worktree die de app zelf maakte ruimt ze mee op. Staat de map er daarna nog:
   `git worktree remove` (nooit `rm -rf` door een junction heen: kijk eerst met
   `-Attributes ReparsePoint`), of `clean_up_worktrees` (ccd_host). Dan `git branch -d <branch>` en
   `git worktree prune`.

## Pushen, releasen, uitrollen

Alleen op verzoek van de gebruiker. Volg de CLAUDE.md van de repo voor versienummers (patch of minor),
de tag, de workflow en de redeploy. Na de release: de CI-run volgen, de uitrol controleren, de issues
die erin zitten sluiten. Komt er bij het pushen iets binnen op origin: breek de release af, merge het,
test opnieuw en tag dan pas.

## Wat de coördinator niet doet

**Kleine dingen doet de coördinator zelf**: één regel, een waarde, één bestand, een kleine regressie
die bij het mergen opduikt, een afspraak in de CLAUDE.md. Daarvoor geen chip. **Groter werk gaat altijd
naar een chip** (`/chip`), kort en smal opgeschreven; knip een groot onderwerp in meer kleine chips.
Verder doet de coördinator wat het mergen vraagt: conflicten oplossen, twee dubbel gebouwde dingen tot
één samenvoegen, versienummers, de release.

**Nooit in de worktree van een chip werken.** Wat er in een worktree moet gebeuren (bijvoorbeeld een
commit met toestemming van de gebruiker) gaat met `git -C <worktree> …` vanuit de hoofdcheckout, nooit
met `cd`: de app verhuist de sessie anders naar die worktree, waarna de worktree-guard de coördinator
zelf als chip ziet en het mergen weigert. Gebeurt het toch: `change_directory` terug naar de
hoofdcheckout (gaat in na de beurt).

Geen geheimen in chips of berichten.
