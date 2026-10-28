---
name: chip
description: Maakt een taak-chip (start_session) voor een losse sessie in een eigen worktree, met de vaste afspraak dat die sessie niet zelf merget of pusht maar zich klaar meldt bij de coördinator-sessie. Gebruik dit bij /chip, "maak een chip", "zet dit in een chip", "nieuwe chip voor …", en altijd wanneer de coördinator (de hoofdchat die andere sessies merget) werk uitbesteedt aan een nieuwe sessie.
---

# /chip — werk uitbesteden zonder dat het zelf naar main gaat

De werkwijze: één **coördinator-sessie** (⚡) in de hoofdcheckout van een repo, die merget, pusht en
releaset, en losse sessies (chips, 🔷) in `.claude/worktrees/<naam>`. Als dat alleen een afspraak in tekst
is, mergen en pushen chips toch zelf naar main (en zo kwam er eens een regressie op main). Daarom:

- de hook `worktree-guard.py` van deze plugin weigert in een worktree-sessie elke `git push`,
  `gh pr merge`/`gh release`, het verzetten van main/master en schrijvende git-opdrachten op de
  hoofdcheckout (het slot);
- de project-`CLAUDE.md` zegt het bij voorkeur ook (de afspraak);
- en deze skill zet het in elke chip, met hoe de sessie zich terugmeldt (de werkwijze).

Vereist de Claude desktop-app (Code-tab): `start_session`, de sessie-tools en `SendMessage`.

## Stappen

1. **Ben ik de coördinator?** Alleen een ⚡-sessie in de hoofdcheckout maakt chips. Zit je zelf in een
   worktree, of ben je een 💬-bijsessie, maak dan geen chip: stuur de volledige opdracht met
   `SendMessage` naar de ⚡ van de repo, of stel het voor aan de gebruiker.
2. **Schrijf de opdracht kort en smal** (snellere iteratie): **één doel**, een paar zinnen, met wat er
   moet gebeuren, waar ongeveer, en wat "klaar" is (controleerbaar: bij een bug een test die eerst
   faalt, bij een feature wat je moet zien). Geen lange spec, geen "lees eerst X, Y en Z", geen lijst
   van elk randgeval. Groter werk: knip het in meer kleine chips. Is iets maar één regel, een waarde of
   één bestand, maak dan géén chip: dat doet de coördinator zelf. Heeft de repo een opzetscript voor een
   verse worktree (zie de CLAUDE.md), noem dat als één regel; geen eigen uitleg over installeren.
3. **Plak de vaste staart eronder** (hieronder).
4. **`start_session`**, zodat de chip een *linked session* van de coördinator wordt (de app hangt hem
   als subsessie eronder en meldt zijn eindrapport vanzelf terug):
   - `initiation`: `"user_asked"` als de gebruiker de chip vroeg (`/chip`, "zet dit in een chip"); een
     chip die je zelf bedenkt is `"own_initiative"` (een kaartje dat de gebruiker zelf start).
   - `context: "fresh"`, `prompt` = opdracht + staart, `background` = het grotere doel in een paar zinnen.
   - `title`: **`🔷 ` plus twee tot vier woorden**, het onderwerp en geen zin, met een hoofdletter en
     zonder lidwoorden: `🔷 Rijhouding paard`, `🔷 Respawn to town (#74)` (bij een issue het nummer
     erachter). Aan de 🔷 zie je in de zijbalk dat het een chip is.
   - `name`: korte slug (`rijhouding-paard`); `branch_name` idem.
   - **Wijzigt code** → `use_worktree: true`. **Alleen lezen** (logs doorzoeken, iets uitzoeken,
     een review) → `use_worktree: false` en een goedkoper `model`; geen branch, niets te mergen.
   - **Andere repo** dan de cwd van de coördinator → `cwd` met die repo.
5. Meld de gebruiker in één of twee zinnen wat de chip doet.
6. **Geen mapje.** Verplaats een chip niet naar een groep (`move_sessions`): de linked-session-weergave
   onder de coördinator is de groepering.

## De vaste staart

```
## Afspraken voor deze sessie
- Je bent een chip van de ⚡-coördinator van deze repo: dat is de sessie die jou startte
  (`list_sessions` met `linked: true`; de ⚡-rij). Berichten aan hem gaan met SendMessage naar
  zijn `local_…`-sessionId, nooit naar zijn titel.
- Werk in je eigen worktree en commit op je eigen branch (volg de commitstijl van de repo).
  Merge NIET naar main, push NIET, maak geen release en redeploy niets: dat doet de coördinator.
  Een hook weigert het ook.
- Main nodig (conflicten, nieuwe code)? Gebruik `sync_with_base_branch` (ccd_host); lukt dat niet,
  merge `main` in je eigen branch, nooit andersom.
- Klein en snel: doe het ene ding, zonder analyse vooraf, refactor of onderzoeksverslag. Proberen en
  testen tot het werkt mag. Een screenshot als het zichtbaar is; metingen alleen als de opdracht over
  snelheid gaat. Docs alleen waar iets door jouw wijziging niet meer klopt. Eén commit, een rapport van
  een paar regels.
- Raak alleen aan wat de opdracht vraagt: elke gewijzigde regel moet daaruit volgen. Geen
  opruimwerk ernaast (andere chips werken tegelijk in dezelfde code, dus dat geeft merge-conflicten).
  Ruim wel op wat jouw eigen wijziging overbodig maakt; andere dode code meld je, je haalt hem niet weg.
- Draai de relevante tests: die van wat je raakt plus wat daarop leunt. NIET de hele suite: die draait
  de coördinator of CI na het mergen, op de echte combinatie van branches. Noem in je rapport welke
  tests je draaide.
- Een keuze die bij de gebruiker ligt (ontwerp, wat open blijft, committen)? Vraag het NIET in je eigen
  venster, maar stuur de vraag met SendMessage naar de coördinator, die hem als meerkeuze aan de
  gebruiker voorlegt en het antwoord terugstuurt. Per vraag, hoogstens vier:
    VRAAG: <de vraag, met genoeg context om zonder jouw venster te kiezen>
    KOP: <hoogstens 12 tekens>
    OPTIES: <label> — <wat het betekent>  (2 à 4; je aanbeveling eerst, met "(Recommended)")
  Werk intussen door aan wat niet van het antwoord afhangt.
- Klaar? Rond af met wrap_up; de app stuurt je recap vanzelf naar de coördinator (alleen de eerste
  ~400 tekens komen mee, dus de recap is compact: branch + laatste commit · wat er gedaan is ·
  tests geslaagd/gefaald · redeploy/herstart/release nodig?). Je eindbericht daarna is het volledige
  rapport: daarbij ook aannames die je zelf maakte waar de opdracht niets over zei, en wat nog open
  staat (ook gemelde dode code). Geen apart SendMessage nodig.
- Stop daarna; de coördinator merget en archiveert de sessie.
```
