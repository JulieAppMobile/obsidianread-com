# obsidianread.com — site officiel

Site statique pour héberger les **CGU** + **Politique de confidentialité** + une page d'accueil minimale.

## Contenu

- `index.html` — page d'accueil simple
- `terms.html` — Conditions générales d'utilisation
- `privacy.html` — Politique de confidentialité (RGPD)

## Déployer

### Option 1 — Vercel (recommandé, drag & drop, gratuit)

1. Va sur https://vercel.com → connecte-toi avec GitHub
2. **New Project** → **Import** → choisis ce dossier (ou push-le sur GitHub d'abord)
3. Vercel détecte un site statique → **Deploy**
4. Clique **Domains** → ajoute `obsidianread.com`
5. Vercel te donne 2 enregistrements DNS à configurer chez ton registrar
6. ✅ En ligne sous 5 minutes avec HTTPS automatique

### Option 2 — GitHub Pages (gratuit)

1. Crée un repo public `obsidianread-com` sur GitHub
2. Push tous les fichiers
3. Settings → Pages → Source : `main` branch
4. Custom domain : `obsidianread.com`
5. Configure le DNS chez ton registrar (4 A records pour GitHub Pages)

## Mise à jour des contenus

Les pages HTML sont **autonomes** (CSS inline) — modifie le texte, redéploie, c'est en ligne. Aucun impact sur l'app, aucune mise à jour App Store nécessaire.

## URLs finales

- https://obsidianread.com
- https://obsidianread.com/terms
- https://obsidianread.com/privacy
