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

Vereist de Claude desktop-app (Code-tab): `spawn_task`, de sessie-tools en `SendMessage`.

## Stappen

1. **Wie ben ik?** Roep `ListAgents` aan: de eerste regel zegt "This session is <naam>". Die naam
   is het adres waarnaar de chip zich terugmeldt - **exact**, met de ⚡ ervoor (zie `/coordinator`).
   Is de sessie geen coördinator (zit je zelf in een worktree), maak dan geen chip maar stel het voor
   aan de gebruiker.
2. **Schrijf de opdracht kort en smal** (snellere iteratie): **één doel**, een paar zinnen, met wat er
   moet gebeuren, waar ongeveer, en wat "klaar" is (controleerbaar: bij een bug een test die eerst
   faalt, bij een feature wat je moet zien). Geen lange spec, geen "lees eerst X, Y en Z", geen lijst
   van elk randgeval. Groter werk: knip het in meer kleine chips. Is iets maar één regel, een waarde of
   één bestand, maak dan géén chip: dat doet de coördinator zelf. Heeft de repo een opzetscript voor een
   verse worktree (zie de CLAUDE.md), noem dat als één regel; geen eigen uitleg over installeren.
3. **Plak de vaste staart eronder** (hieronder), met `<coördinator>` ingevuld.
4. `spawn_task` met een **korte titel: `🔷 ` plus twee tot vier woorden**, het onderwerp en geen
   zin, met een hoofdletter en zonder lidwoorden. Bijvoorbeeld `🔷 Rijhouding paard`,
   `🔷 Doodanimatie avonturier` of `🔷 Respawn to town (#74)` (bij een issue het nummer erachter).
   De titel wordt de sessienaam. Aan de 🔷 zie je in de zijbalk dat het een chip in een worktree is,
   en kort lees je hem in één oogopslag. Wat de chip precies doet zet je in de tldr.
5. Meld de gebruiker in één of twee zinnen wat de chip doet.
6. **Geen mapje.** De app hangt een gestarte chip als subsessie onder de coördinator die hem voorstelde.
   Dat is de groepering: verplaats een chip niet naar een groep (`move_sessions`). Is de coördinator
   sinds het maken van de chip hernoemd, stuur de chip dan meteen het nieuwe adres.

## De vaste staart

```
## Afspraken voor deze sessie
- Werk in je eigen worktree en commit op je eigen branch (volg de commitstijl van de repo).
  Merge NIET naar main, push NIET, maak geen release en redeploy niets: dat doet de coördinator.
  Een hook weigert het ook.
- Main nodig (conflicten, nieuwe code)? Merge `main` of `origin/main` in je eigen branch, niet andersom.
- Klein en snel: doe het ene ding, zonder analyse vooraf, refactor of onderzoeksverslag. Proberen en
  testen tot het werkt mag. Een screenshot als het zichtbaar is; metingen alleen als de opdracht over
  snelheid gaat. Docs alleen waar iets door jouw wijziging niet meer klopt. Eén commit, een rapport van
  een paar regels.
- Raak alleen aan wat de opdracht vraagt: elke gewijzigde regel moet daaruit volgen. Geen
  opruimwerk ernaast (andere chips werken tegelijk in dezelfde code, dus dat geeft merge-conflicten).
  Ruim wel op wat jouw eigen wijziging overbodig maakt; andere dode code meld je, je haalt hem niet weg.
- Draai de relevante tests: die van wat je raakt plus wat daarop leunt. NIET de hele suite: die draait
  de coördinator na het mergen, op de echte combinatie van branches (meerdere chips die tegelijk de
  hele suite draaien gaven alleen vals alarm door gelijktijdigheid). Noem in je rapport welke tests je
  draaide.
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
    aannames die je zelf maakte waar de opdracht niets over zei · wat nog open staat (ook gemelde
    dode code) · of er een redeploy, herstart of release nodig is (patch of minor).
  Wordt het bericht tegengehouden (andere permissiemodus), zet hetzelfde rapport dan als je
  laatste antwoord: de coördinator leest het daar.
- Stop daarna; de coördinator merget en archiveert de sessie.
```

## Mergen als coördinator

Komt een rapport binnen: lees het, merge de branch (`--no-ff`, "Merge: <titel>"), en draai de hele suite
pas vlak vóór een push, één keer na alle klare chips (alleen de coördinator doet dat; zie `/coordinator`).
Ruim worktree en branch pas op als `git -C <worktree> status` schoon is, en archiveer dan de sessie.
Pushen en releasen alleen als de gebruiker erom vraagt.
