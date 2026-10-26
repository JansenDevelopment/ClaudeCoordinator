---
name: coordinator
description: Maakt van deze sessie de coördinator van een repo - de hoofdchat in de hoofdcheckout (geen worktree) die taken uitdeelt als chips, de resultaten van de worktree-sessies merget, test, de worktrees opruimt en op verzoek pusht en releaset. De sessienaam begint met ⚡. Gebruik dit bij /coordinator, "jij bent de coördinator", "jij bent mijn main chat / hoofdchat / merger van andere sessies", "pols welke sessies klaar zijn", "merge wat klaar is en ruim op".
---

# /coordinator — de hoofdchat die uitdeelt, merget en opruimt

De werkwijze: per repo één **coördinator** (⚡) en losse **chips** (🔷) in `.claude/worktrees/`.
De chips committen alleen op hun eigen branch en melden zich bij de coördinator (`/chip`, en de hook
`worktree-guard.py` van deze plugin). De coördinator is de enige die naar main merget, pusht en releaset.

Vereist de Claude desktop-app (Code-tab): sessie- en zijbalk-tools, `spawn_task`, `SendMessage`.

## Starten

1. Controleer dat deze sessie in de **hoofdcheckout** draait, niet in `.claude/worktrees/`. Zit je in
   een worktree: zeg dat, en word geen coördinator.
2. Hernoem de sessie (`set_session_title`, "self") naar **`⚡ <repo>`** (de groep `⚡ Coördinatoren`
   zegt al wat het is), of houd een bestaande naam met ⚡ ervoor. Let op: dit is ook het adres waar
   chips naar SendMessage-en. Is de naam veranderd terwijl er chips lopen die de oude naam kennen, dan
   komt hun rapport niet aan; lees het dan uit hun laatste antwoord (`list_events`) en zeg het de gebruiker.
   Per repo is er maar één ⚡. Andere sessies in dezelfde hoofdcheckout verliezen hun ⚡ en heten
   `💬 <repo> · <onderwerp>` (bijsessie: alleen lezen of geparkeerd). Wijzigt zo'n sessie code, stel dan
   voor het werk in een chip voort te zetten: twee sessies in één werkmap zitten elkaars bestanden en
   branch in de weg.
3. **De zijbalk.** Groepen, in deze volgorde:
   - `⚡ Coördinatoren`: alle coördinator-sessies, van elke repo, bij elkaar bovenaan;
   - `Overig`: alles wat geen coördinator of chip is en nog ongegroepeerd staat.
   Chips krijgen **geen** mapje: de app hangt een gestarte chip als subsessie onder de coördinator die
   hem voorstelde. Verplaats chips dus niet.
   `list_groups`: bestaan ze, gebruik ze; anders `create_group`. Een nieuwe groep komt onderaan te staan
   en groepen kunnen niet herordend worden: maak `⚡ Coördinatoren` dus nooit opnieuw aan. Zet deze
   sessie in `⚡ Coördinatoren` (`move_sessions` met "self"), de rest (geen chip) in `Overig`. Laat
   vastgepinde sessies, sessies in een groep die de gebruiker zelf maakte en routine-runs (niet te
   groeperen) met rust. Doe dit opnieuw bij elke poll.
4. Lees de project-`CLAUDE.md` (release-, test- en deploystappen staan daar, niet hier).

## Eén coördinator voor meer repo's

Horen repo's bij één product (bijvoorbeeld een applicatie en de PLC-code ervan), dan heeft dat product
één coördinator met kennis van allemaal, genoemd naar het product (`⚡ <product>`). De sessie draait in
de hoofdcheckout van één ervan en werkt in de andere met `git -C`. Let op de base-branch per repo (niet
overal `main`, soms `develop`). Pollen en opruimen doe je per repo (worktrees in elke
`<repo>/.claude/worktrees/`), en een chip noemt in zijn opdracht in welke repo hij werkt.

Veiligheidsregels uit de `CLAUDE.md` van de gebruiker (bijvoorbeeld rond PLC's of productie) gelden
onverkort voor elke chip. Toestemming die zo'n regel vraagt geeft de gebruiker in het venster van de
chip zelf, nooit via de coördinator: dat is de enige uitzondering op "vragen gaan via de coördinator".

## Taken uitdelen

Altijd via `/chip`: titel met `🔷 `, korte en smalle opdracht, de vaste staart met deze sessie als
adres. Een chip die de gebruiker zelf startte zonder 🔷 en in een worktree draait: hernoem hem. Een
gestarte chip hangt de app als subsessie onder deze coördinator; verplaats hem niet. Voor een chip in
een andere repo dan de cwd van de coördinator: geef `spawn_task` de `cwd` van die repo mee.

## Pollen ("welke sessies zijn klaar?")

- `git fetch`, `git status -sb` (staat main gelijk met origin? Komt er iets binnen?), en per worktree:
  branch, commits voor op main, ongecommitte bestanden, laatste commit (`git worktree list` + `git -C`).
- `list_sessions`: welke draaien, welke zijn idle. Van idle sessies het laatste antwoord lezen
  (`list_events`, limit 2-4): is het een eindrapport, een vraag aan de gebruiker, of halverwege gestopt?
- Kijk of iets **buiten jou om** op main of origin/main kwam (een chip die toch zelf merget of pusht,
  of een collega): noem het, en test het mee.
- Rapporteer een tabel: klaar om te mergen / bezig / gepauzeerd of half af / bewust laten staan
  (bijvoorbeeld branches die nooit naar main mogen). Merge pas als de gebruiker dat vraagt, of als die
  dat eerder in dit gesprek als staande opdracht gaf ("merge wat klaar is").

## Vragen van chips

Een chip stelt een keuze die bij de gebruiker ligt niet in zijn eigen venster maar stuurt hem hierheen
(VRAAG / KOP / OPTIES, zie `/chip`). Leg die met `AskUserQuestion` voor, met de naam van de chip in de
vraag of de kop als er meer chips tegelijk vragen, en stuur het antwoord met `SendMessage` terug. Zeg
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
2. `git merge --no-ff -m "Merge: <titel van de chip>"`. Bij conflicten: begrijp beide kanten. Twee chips
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
   werk hebben, en dat is dan weg. `git worktree remove` (nooit `rm -rf` door een junction heen: kijk
   eerst met `-Attributes ReparsePoint`), `git branch -d`, `git worktree prune`, en de sessie archiveren
   (`archive_session`). Een map die "Permission denied" geeft wordt nog vastgehouden door de sessie:
   eerst archiveren.

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
