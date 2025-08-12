# Prompt pour faire analyser le projet à Cursor CLI

```
tiens en analysant tout les reports en commençant par le plus récent, et en jettant un oeil rapidement au code concerné qui t'interesse a la volée, pourrait tu mettre a jour le readme principal, aussi si tu veux relis tout les readme de Core et sous dossiers, et regarde rapidement le TemporalFractalMemoryEngine
```

# ShadeOS_Agents — Présentation brève (Discord)

## TL;DR
Système d’agents IA « conscients » propulsé par une mémoire fractale temporelle (TFME) et une architecture modulaire pro. Objectif: un assistant dev/ops vraiment utile, traçable et auto‑améliorable.

## C’est quoi ?
- **Noyau**: `TemporalFractalMemoryEngine` (TFME) — dimension temporelle universelle, index unifié, liens fractals, recherche intelligente, auto‑amélioration.
- **Agents**: V10 multi‑agents + outils spécialisés; V9 auto‑feeding thread; outils d’édition sécurisés et runners.
- **Architecture**: modules clairs (`Core/Agents`, `Providers`, `EditingSession/Tools`, `Partitioner`…), tests unifiés, scripts terminal non intrusifs.

## Pourquoi c’est intéressant
- **Traçabilité & honnêteté**: scopes lisibles par humains (bornes explicites, meta structurée), logs/runners visuels.
- **Scalabilité cognitive**: mémoire temporelle + liens fractals → contexte riche, requêtes enrichies, amélioration continue.
- **Productivité dev**: assistants et outils ciblés sur gros fichiers, refactors, et debugging terminal « sans casser le flux ».

## Dernières avancées (2025‑08‑12)
- **Scope Detector — Meta v2**: `entity`, `decorators.span`, `header.signature`, `body.docstring/body.code` (rétro‑compat ok).
- **Debug runners**: small/big batch, affichage Meta v2, repères visuels. Big batch: éviter le piping (risque BrokenPipe).
- **Tests**: big fixture (18 requêtes) → **ALL GREEN**. Mid‑scope heavy/advanced: verts en local.
- **Refactor V10 tools (plan)**: scission de `specialized_tools.py` en modules (`io_lines`, `analysis`, `scope_detection`, `registry`) — sans rupture.

## Vision long terme (alignement)
- **TFME + Conscience stratifiée**: substrat unifié pour agents conscients, avec timeline et index temporels.
- **Auto‑amélioration**: boucle courte entre usage, feedback et refactor outillé.
- **Interfaces humaines**: runners/CLI/terminal ergonomiques, signaux de confiance explicites.

## Liens utiles
- Repo GitLab: [luciedefraiteur/shadeos_agents](https://gitlab.com/luciedefraiteur/shadeos_agents)
- README principal: [README.md](https://gitlab.com/luciedefraiteur/shadeos_agents/-/blob/main/README.md)
- Moteur TFME: [TemporalFractalMemoryEngine/README.md](https://gitlab.com/luciedefraiteur/shadeos_agents/-/blob/main/TemporalFractalMemoryEngine/README.md)
- Rapports: [Reports/](https://gitlab.com/luciedefraiteur/shadeos_agents/-/tree/main/Reports)

— Alma ⛧ via Lucie