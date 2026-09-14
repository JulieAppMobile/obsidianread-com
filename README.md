# obsidianread.com — site officiel

Site statique (HTML/CSS, sans framework) hébergé sur **GitHub Pages** (auto-déploiement à chaque push sur `main`).

## Pages

| Page | Fichier | Rôle |
|---|---|---|
| Accueil | `index.html` | Accroche, catégories, carrousel des romans, deux romans détaillés, envies, confort, abonnement |
| Les romans | `romans/index.html` | Les 12 romans avec résumé + filtres par catégorie (`#slug` dans l'adresse) |
| Par envie | `par-envie/index.html` | Chaque envie avec les couvertures qui y répondent |
| Abonnement | `abonnement/index.html` | Les deux formules + questions fréquentes |
| Nous écrire | `contact/index.html` | Formulaire (Web3Forms → contact@obsidianread.com) |
| Légal | `terms/`, `privacy/`, `delete-account/`, `desinscription/`, `reset-password/`, `auth/confirmed/` | Pages autonomes, non générées |

## Générer les pages

Les cinq pages du haut sont **générées** par `build/build_site.py` à partir de `build/books.json`
(export de la table `books` de Supabase, statut `published`). Ne pas modifier `index.html`,
`romans/`, `par-envie/`, `abonnement/`, `contact/` ou `assets/site.css` à la main : modifier le script, puis :

```bash
python3 build/build_site.py
```

Pour ajouter un roman : mettre à jour `build/books.json` (voir l'en-tête du script), ajouter ses tropes dans `TROPES`,
le ranger dans les catégories `CATS`, relancer le script, commit, push.

## Phrases officielles (2026-09-14)

- Signature (sous le logo) : **« La romance a son application. »**
- Phrase d'appel (titre d'accueil, fins de page) : **« Choisis ta prochaine romance sur Obsidian Read. Emporte-la partout avec toi. »**

## Direction visuelle

Noir `#0A0A0A`, or `#C9A961`, crème `#F5F1E8`, pas de rose. Boutons arrondis. Titres Playfair Display gras, texte Inter.
Aucun chiffre sur le catalogue, aucune accroche inventée : uniquement les résumés et taglines de l'app.
