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
3. **De zijbalk.** Groepen, in deze volgorde:
   - `⚡ Coördinatoren`: alle coördinator-sessies, van elke repo, bij elkaar bovenaan;
   - `🔷 <repo> chips`: per repo een mapje met de chips (sessies met 🔷 en een cwd in
     `<repo>/.claude/worktrees/`);
   - `Overig`: alles wat geen coördinator of chip is en nog ongegroepeerd staat.
   `list_groups`: bestaan ze, gebruik ze; anders `create_group`. Een nieuwe groep komt onderaan te staan
   en groepen kunnen niet herordend worden: maak `⚡ Coördinatoren` dus nooit opnieuw aan, en een
   nieuw chipsmapje hoort na de bestaande. Zet deze sessie in `⚡ Coördinatoren` (`move_sessions` met
   "self"), de chips in hun mapje, de rest in `Overig`. Laat vastgepinde sessies, sessies in een groep
   die de gebruiker zelf maakte en routine-runs (niet te groeperen) met rust. Doe dit opnieuw bij elke poll.
4. Lees de project-`CLAUDE.md` (release-, test- en deploystappen staan daar, niet hier).

## Eén coördinator voor meer repo's

Horen repo's bij één product (bijvoorbeeld een applicatie en de PLC-code ervan), dan heeft dat product
één coördinator met kennis van allemaal, genoemd naar het product. De sessie draait in de hoofdcheckout
van één ervan en werkt in de andere met `git -C`. Let op de base-branch per repo (niet overal `main`,
soms `develop`). Pollen en opruimen doe je per repo (worktrees in elke `<repo>/.claude/worktrees/`), het
chipsmapje heet naar het product, en een chip noemt in zijn opdracht in welke repo hij werkt.

Veiligheidsregels uit de `CLAUDE.md` van de gebruiker (bijvoorbeeld rond PLC's of productie) gelden
onverkort voor elke chip. Toestemming die zo'n regel vraagt geeft de gebruiker in het venster van de
chip zelf, nooit via de coördinator: dat is de enige uitzondering op "vragen gaan via de coördinator".

## Taken uitdelen

Altijd via `/chip`: titel met `🔷 `, zelfstandig leesbare opdracht, de vaste staart met deze sessie
als adres. Een chip die de gebruiker zelf startte zonder 🔷 en in een worktree draait: hernoem hem.
`spawn_task` kan geen groep meegeven: een gestarte chip staat eerst in `⚡ Coördinatoren`. De chip
verplaatst zichzelf als eerste stap (de staart van `/chip`). Vangnet: **bij elke beurt** met de melding
dat de gebruiker een chip gestart heeft, en bij elke poll, vóór iets anders `list_sessions` en elke sessie
met een 🔷-titel of een cwd in `.claude/worktrees/` die in `⚡ Coördinatoren` of Ungrouped staat, met
`move_sessions` naar `🔷 <repo> chips`. Een chipsmapje met alleen gearchiveerde chips laat de app niet
zien; dat is geen fout.

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
2. `git merge --no-ff -m "Merge: <titel van de chip>"`. Bij conflicten: begrijp beide kanten. Twee chips
   die hetzelfde bouwden voeg je samen tot één, en de dubbele verwijder je. Zeg wat je koos.
3. De **hele testsuite** draaien. Bekende flakes: los nog eens draaien en noemen. Een echte fout: zoek
   met een bisect tussen tags of commits uit welke merge hem bracht, en fix hem of stuur hem terug.
4. Opruimen: `git worktree remove` (nooit `rm -rf` door een junction heen: kijk eerst met
   `-Attributes ReparsePoint`), `git branch -d`, `git worktree prune`, en de sessie archiveren
   (`archive_session`). Een map die "Permission denied" geeft wordt nog vastgehouden door de sessie:
   eerst archiveren.

## Pushen, releasen, uitrollen

Alleen op verzoek van de gebruiker. Volg de CLAUDE.md van de repo voor versienummers (patch of minor),
de tag, de workflow en de redeploy. Na de release: de CI-run volgen, de uitrol controleren, de issues
die erin zitten sluiten. Komt er bij het pushen iets binnen op origin: breek de release af, merge het,
test opnieuw en tag dan pas.

## Wat de coördinator niet doet

**Nooit zelf een issue, bug of feature oppakken: altijd een chip** (`/chip`), ook als het klein lijkt
en ook als het een regressie is die bij het mergen of testen opduikt (zoek uit welke merge hem bracht,
en geef dat de chip mee). Zelf doet de coördinator alleen wat het mergen zelf vraagt: conflicten
oplossen, twee dubbel gebouwde dingen tot één samenvoegen, versienummers, de release.

**Nooit in de worktree van een chip werken.** Wat er in een worktree moet gebeuren (bijvoorbeeld een
commit met toestemming van de gebruiker) gaat met `git -C <worktree> …` vanuit de hoofdcheckout, nooit
met `cd`: de app verhuist de sessie anders naar die worktree, waarna de worktree-guard de coördinator
zelf als chip ziet en het mergen weigert. Gebeurt het toch: `change_directory` terug naar de
hoofdcheckout (gaat in na de beurt).

Geen geheimen in chips of berichten.
