# Coördinator & chips — Claude Code-plugin

Werken met meerdere Claude-sessies tegelijk aan één repo, zonder dat ze elkaar of `main` in de weg zitten:

- **`/coordinator`** maakt van een sessie in de hoofdcheckout de coördinator (⚡). Die deelt werk uit,
  merget wat klaar is, doet kleine dingen zelf, ruimt worktrees op en pusht of releaset alleen als jij dat vraagt.
- **`/chip`** besteedt een taak uit aan een nieuwe sessie (🔷) in een eigen worktree
  (`.claude/worktrees/<naam>`), met een korte opdracht met één doel. Die commit alleen op de eigen branch;
  omdat de chip een *linked session* is, komt zijn eindrapport vanzelf bij de coördinator binnen.
  Vragen die jij moet beantwoorden lopen ook via de coördinator. Een chip die alleen leest draait
  zonder worktree en kan op een goedkoper model.
- **De hook `worktree-guard.py`** weigert in een worktree-sessie `git push`, `gh pr merge`,
  `gh release …`, het verzetten van main/master en schrijvende git-opdrachten op de hoofdcheckout.
  De coördinator draait in de hoofdcheckout en heeft er dus geen last van.

## Vereisten

- De **Claude desktop-app** (Code-tab). De skills gebruiken tools die alleen daar bestaan: `start_session`
  (linked sessions), sessies hernoemen, `SendMessage` tussen sessies. In de terminal-CLI werkt alleen
  de hook.
- **Python** op het PATH als `python`, voor de hook. Zonder Python laat de hook alles door.

## Installeren

In Claude Code:

```
/plugin marketplace add JansenDevelopment/ClaudeCoordinator
/plugin install coordinator@martijn-coordinator
```

Start daarna een nieuwe sessie. Een update ophalen gaat met `/plugin marketplace update martijn-coordinator`.

Plugin-skills krijgen de pluginnaam als voorvoegsel: `/coordinator:coordinator` en `/coordinator:chip`.
Je kunt ze ook gewoon in woorden aanroepen ("jij bent de coördinator", "zet dit in een chip").

## Gebruik

1. Open een sessie in de hoofdcheckout van je repo en zeg: *jij bent de coördinator*.
2. Vraag de coördinator om een taak in een chip te zetten. De sessie start in een eigen worktree en
   hangt als subsessie onder de coördinator.
3. Is de chip klaar, dan komt zijn rapport vanzelf bij de coördinator binnen. Zeg daar *merge wat klaar is*.
4. Pushen of releasen: vraag het de coördinator.

Tip: zet de afspraak ook in de `CLAUDE.md` van de repo (alleen de coördinator merget naar main en pusht;
andere sessies werken in `.claude/worktrees/` en melden zich klaar bij de coördinator). Dan weet elke
sessie het, ook zonder de skills.
