# 🧭 obsidianread-com — Fil d'Ariane

> 🌐 **CODE SITE WEB** : obsidianread.com (Vercel, HTML/CSS). Entrée du funnel + 3 chapitres gratuits + pages légales.

⬆️ **Parent** : [`../OBSIDIAN_READ_HUB.md`](../OBSIDIAN_READ_HUB.md)
📍 **Source de vérité** : doit lire le **même catalogue Supabase** que l'app (pas de contenu dupliqué en dur).

## ⬇️ Ce qu'il y a dedans
- **`index.html`** — landing Galatea-style (hero, carrousels, Meta Pixel).
- **`privacy.html` / `terms.html` + `/privacy/`, `/terms/`** — pages légales (RGPD/CGU).
- **`.well-known/`** — `apple-app-site-association`, `assetlinks.json` (deep linking app).
- **`contact/`, `delete-account/`, `reset-password/`, `auth/`** — flux Supabase.
- **`mockups/`** — visuels app. **`vercel.json`, `CNAME`** — déploiement / DNS.
- **`CLAUDE.md`** — instructions du dossier.

## 🔗 Liens croisés
- Catalogue / chapitres → Supabase ([`../obsidian-read/backend/`](../obsidian-read/_NAV.md))
- Deep link → renvoie vers l'app [`../obsidian-read/mobile/`](../obsidian-read/_NAV.md)

## ⚠️ Notes / dette (audit 2026-06-26)
- 🔴 **Pages `/livre/[slug]/chapitre/[N]` (3 chapitres gratuits) PAS encore implémentées** → bloque le funnel complet.
- Double structure `privacy.html` + `/privacy/index.html` à clarifier (rewrite Vercel ?).
- Vérifier que les URLs privacy/terms sont **live et liées** dans les 2 stores + in-app (obligatoire).
