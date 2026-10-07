---
name: chip
description: Maakt een taak-chip (spawn_task) voor een losse sessie in een eigen worktree, met de vaste afspraak dat die sessie niet zelf merget of pusht maar zich klaar meldt bij de coördinator-sessie. Gebruik dit bij /chip, "maak een chip", "zet dit in een chip", "nieuwe chip voor …", en altijd wanneer de coördinator (de hoofdchat die andere sessies merget) werk uitbesteedt aan een nieuwe sessie.
---

# /chip — werk uitbesteden zonder dat het zelf naar main gaat

De werkwijze: één **coördinator-sessie** in de hoofdcheckout van een repo, die merget, pusht en
releaset, en losse sessies (chips) in `.claude/worktrees/<naam>`. Als dat alleen een afspraak in tekst
is, mergen en pushen chips toch zelf naar main (en zo kwam er eens een regressie op main). Daarom:

- de hook `worktree-guard.py` van deze plugin weigert in een worktree-sessie elke `git push`,
  `gh pr merge`/`gh release`, het verzetten van main/master en schrijvende git-opdrachten op de
  hoofdcheckout (het slot);
- de project-`CLAUDE.md` zegt het bij voorkeur ook (de afspraak);
- en deze skill zet het in elke chip, met hoe de sessie zich terugmeldt (de werkwijze).

Vereist de Claude desktop-app (Code-tab): `spawn_task`, de zijbalk-tools en `SendMessage`.

## Stappen

1. **Wie ben ik?** Roep `ListAgents` aan: de eerste regel zegt "This session is <naam>". Die naam
   is het adres waarnaar de chip zich terugmeldt - **exact**, met de ⚡ ervoor (zie `/coordinator`).
   Is de sessie geen coördinator (zit je zelf in een worktree), maak dan geen chip maar stel het voor
   aan de gebruiker.
2. **Schrijf de opdracht** zoals altijd: zelfstandig leesbaar, met repo-pad, bestanden, context uit
   dit gesprek, wat "klaar" is, welke tests. Volg de bestaande gewoontes van de repo (CLAUDE.md,
   plannenmap, taal van commits).
3. **Plak de vaste staart eronder** (hieronder), met `<coördinator>` ingevuld.
4. `spawn_task` met een **korte titel: `🔷 ` plus twee tot vier woorden**, het onderwerp en geen
   zin, met een hoofdletter en zonder lidwoorden. Bijvoorbeeld `🔷 Rijhouding paard`,
   `🔷 Doodanimatie avonturier` of `🔷 Respawn to town (#74)` (bij een issue het nummer erachter).
   De titel wordt de sessienaam. Aan de 🔷 zie je in de zijbalk dat het een chip in een worktree is,
   en kort lees je hem in één oogopslag. Wat de chip precies doet zet je in de tldr.
5. Meld de gebruiker in één of twee zinnen wat de chip doet.
6. **De chip in zijn mapje.** `spawn_task` kan geen groep meegeven, dus een gestarte chip staat eerst in
   de groep van de coördinator (`⚡ Coördinatoren`). De coördinator hoort pas dat hij gestart is bij het
   volgende bericht van de gebruiker; daarom verplaatst de chip **zichzelf** als eerste stap (zie de
   staart: `move_sessions` met "self" vraagt niets). Vangnet aan de kant van de coördinator, **bij elke
   beurt** waarin de melding "The user started your suggested background task" staat, en bij elke poll,
   vóór iets anders:
   - `list_sessions`: zoek de sessie met de 🔷-titel van de chip en een cwd in `<repo>/.claude/worktrees/`.
   - `list_groups`: zoek `🔷 <repo> chips`. Bestaat die niet, dan `create_group` (zie `/coordinator`
     over de volgorde).
   - `move_sessions` met dat session-id en group-id. Meld het niet apart; het hoort bij het starten.
   Is de coördinator sinds het maken van de chip hernoemd, stuur de chip dan meteen het nieuwe adres.

## De vaste staart

```
## Afspraken voor deze sessie
- Eerste stap, vóór het werk: zet jezelf in het chipsmapje van de zijbalk. `list_groups` (ccd_sidebar),
  zoek `🔷 <repo> chips` en roep `move_sessions` aan met ["self"] en dat group-id. Bestaat het mapje
  niet of heb je die tools niet, sla het over: de coördinator doet het dan.
- Werk in je eigen worktree en commit op je eigen branch (volg de commitstijl van de repo).
  Merge NIET naar main, push NIET, maak geen release en redeploy niets: dat doet de coördinator.
  Een hook weigert het ook.
- Main nodig (conflicten, nieuwe code)? Merge `main` of `origin/main` in je eigen branch, niet andersom.
- Draai de relevante tests, en vóór je klaar meldt de hele suite (zie de CLAUDE.md van de repo).
- Een keuze die bij de gebruiker ligt (ontwerp, wat open blijft, committen)? Vraag het NIET in je eigen
  venster, maar stuur de vraag naar de coördinator, die hem als meerkeuze aan de gebruiker voorlegt
  en het antwoord terugstuurt. Per vraag, hoogstens vier:
    VRAAG: <de vraag, met genoeg context om zonder jouw venster te kiezen>
    KOP: <hoogstens 12 tekens>
    OPTIES: <label> — <wat het betekent>  (2 à 4; je aanbeveling eerst, met "(Recommended)")
  Werk intussen door aan wat niet van het antwoord afhangt.
- Klaar, of vastgelopen op een keuze die bij de gebruiker ligt? Meld je bij de coördinator met
  SendMessage aan "<coördinator>":
    branch + laatste commit · wat er gedaan is · tests (aantal geslaagd/gefaald, en welke) ·
    wat nog open staat · of er een redeploy, herstart of release nodig is (patch of minor).
  Wordt het bericht tegengehouden (andere permissiemodus), zet hetzelfde rapport dan als je
  laatste antwoord: de coördinator leest het daar.
- Stop daarna; de coördinator merget en archiveert de sessie.
```

## Mergen als coördinator

Komt een rapport binnen: lees het, merge de branch (`--no-ff`, "Merge: <titel>"), draai de suite,
ruim worktree en branch op en archiveer de sessie (zie `/coordinator`). Pushen en releasen alleen als
de gebruiker erom vraagt.
