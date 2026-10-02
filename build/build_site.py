#!/usr/bin/env python3
"""Génère les pages du site obsidianread.com à partir de build/books.json.

Usage : python3 build/build_site.py   (depuis la racine du dépôt)

books.json = export de la table `books` de Supabase (status = published).
Pour le rafraîchir :
  curl -sS "$SUPABASE_URL/rest/v1/books?select=*&status=eq.published&order=created_at.desc" \
       -H "apikey: $KEY" -H "Authorization: Bearer $KEY" > build/books.json
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS = [b for b in json.load(open(os.path.join(ROOT, 'build', 'books.json'))) if b.get('status') == 'published']
BY = {b['slug']: b for b in BOOKS}

# ─── Phrases officielles (2026-09-14) ───────────────────────────────────────
SIGNATURE = "La romance a son application."
APPEL = "Choisis ta prochaine romance sur Obsidian Read. Emporte-la partout avec toi."

STORE_IOS = 'https://apps.apple.com/fr/app/obsidian-read/id6770984110'
STORE_ANDROID = 'https://play.google.com/store/apps/details?id=com.obsidianread.app'
PIXEL_ID = '988007563929955'

# Deux tropes affichés sur chaque carte (le « 18+ » est ajouté d'après content_rating)
TROPES = {
    'la-case-accompagnee': 'Faux couple · Enemies to lovers',
    'reste': 'Huis clos · Grumpy × Sunshine',
    'sang-et-serment': 'Dark romance · Mariage arrangé',
    'off-limits': 'Amour interdit · Hockey',
    'noublie-pas-mon-prenom': 'Milliardaire · Assistante',
    'le-colosse-et-l-etoile': "Sport · Les opposés s'attirent",
    'a-charge-a-coeur': 'Prof · Étudiante',
    'sous-le-masque': 'Garde du corps · Seconde chance',
    'hors-antenne': 'Hockey · Enemies to lovers',
    'la-cible': 'Dark romance · Tueur à gages',
    'une-nouvelle-partition': 'Père veuf · Amour interdit',
    'pour-de-faux': 'Faux couple · Huis clos',
    'six-ans-de-silence': 'Dark romance · Enemies to lovers',
    'a-armes-inegales': 'Enemies to lovers · Université',
}
# Ordre d'affichage : les deux premiers = cartes détaillées de l'accueil
ORDER = ['la-case-accompagnee', 'reste', 'sang-et-serment', 'off-limits', 'noublie-pas-mon-prenom',
         'le-colosse-et-l-etoile', 'a-charge-a-coeur', 'sous-le-masque', 'hors-antenne', 'la-cible',
         'une-nouvelle-partition', 'pour-de-faux']
ORDER += [s for s in BY if s not in ORDER]  # nouveaux romans à la fin, sans rien casser

# Catégories populaires : (slug, emoji, libellé, romans)
CATS = [
    ('enemies-to-lovers', '⚔️', 'Enemies to lovers', ['six-ans-de-silence', 'a-armes-inegales', 'a-charge-a-coeur', 'hors-antenne', 'la-cible', 'sang-et-serment', 'la-case-accompagnee']),
    ('faux-couple', '💍', 'Faux couple', ['la-case-accompagnee', 'pour-de-faux']),
    ('amour-interdit', '🚫', 'Amour interdit', ['off-limits', 'a-charge-a-coeur', 'une-nouvelle-partition']),
    ('slow-burn', '🔥', 'Slow burn', ['six-ans-de-silence', 'a-armes-inegales', 'reste', 'off-limits', 'pour-de-faux', 'noublie-pas-mon-prenom', 'une-nouvelle-partition', 'la-cible', 'hors-antenne', 'a-charge-a-coeur', 'sous-le-masque', 'le-colosse-et-l-etoile']),
    ('huis-clos', '🚪', 'Huis clos', ['reste', 'noublie-pas-mon-prenom', 'hors-antenne', 'la-cible', 'pour-de-faux']),
    ('milliardaires', '💰', 'Romances de milliardaires', ['a-armes-inegales', 'noublie-pas-mon-prenom', 'une-nouvelle-partition']),
    ('prof-etudiante', '🎓', 'Prof et étudiante', ['a-charge-a-coeur']),
    ('hockey', '🏒', 'Hockey', ['off-limits', 'hors-antenne']),
    ('football-americain', '🏈', 'Football américain', ['le-colosse-et-l-etoile']),
    ('dark-romance', '🖤', 'Dark romance', ['six-ans-de-silence', 'sang-et-serment', 'la-cible']),
    ('mafia', '🕴️', 'Mafia', ['six-ans-de-silence', 'sang-et-serment', 'la-cible']),
    ('garde-du-corps', '🛡️', 'Garde du corps', ['sous-le-masque']),
    ('mariage-arrange', '💒', 'Mariage arrangé', ['sang-et-serment']),
    ('pere-celibataire', '👨‍👧', 'Père célibataire', ['une-nouvelle-partition']),
    ('ecart-d-age', '⏳', "Écart d'âge", ['a-charge-a-coeur', 'une-nouvelle-partition']),
    ('hommes-alpha', '💪', 'Les hommes alpha', ['six-ans-de-silence', 'a-armes-inegales', 'la-case-accompagnee', 'le-colosse-et-l-etoile', 'off-limits', 'a-charge-a-coeur', 'sous-le-masque']),
    ('seconde-chance', '🔁', 'Seconde chance', ['sous-le-masque', 'une-nouvelle-partition']),
    ('grumpy-sunshine', '☀️', 'Grumpy × Sunshine', ['reste']),
]
CAT_BY_SLUG = {c[0]: c for c in CATS}

# Page « Par envie » : (phrase, slug de catégorie)
ENVIES = [
    ('Quand ils se détestent.', 'enemies-to-lovers'),
    ('Quand ils font semblant.', 'faux-couple'),
    ("Quand ils n'ont pas le droit.", 'amour-interdit'),
    ('Quand ils se retrouvent.', 'seconde-chance'),
    ('Quand ils sont coincés ensemble.', 'huis-clos'),
    ("Quand c'est le patron.", 'milliardaires'),
    ("Quand c'est le prof.", 'prof-etudiante'),
    ('Quand il est dangereux.', 'dark-romance'),
]


def E(s):
    return html.escape(s or '', quote=True)


def tagline(slug):
    t = BY[slug].get('tagline') or ''
    t = re.split(r'\s[—-]\s', t, 1)[-1]
    return t.replace(' vs ', ' contre ')


def trope_label(slug):
    base = TROPES.get(slug) or (BY[slug].get('trope') or '').split(' · ')[0].split(' / ')[0]
    if BY[slug].get('rating') == '18+':
        base += ' · 18+'
    return base


def tags_of(slug):
    return ' '.join(c[0] for c in CATS if slug in c[3])


# ─── Icônes (SVG inline) ────────────────────────────────────────────────────
APPLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.05 20.28c-.98.95-2.05.88-3.08.41-1.09-.47-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.41C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>'
GOOGLE = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3.609 1.814L13.792 12 3.61 22.186a.996.996 0 01-.61-.92V2.734a1 1 0 01.609-.92zm10.89 10.893l2.302 2.302-10.937 6.333 8.635-8.635zm3.736-4.061a.99.99 0 010 1.736l-2.732 1.583-2.605-2.605 2.605-2.605 2.732 1.891zM5.232 1.5l10.937 6.333-2.302 2.302L5.232 1.5z"/></svg>'
TIKTOK = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5.8 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1.84-.1z"/></svg>'
INSTA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>'


def badges(cls=''):
    return f'''<div class="badges {cls}">
      <a class="badge" href="{STORE_IOS}" target="_blank" rel="noopener" onclick="trackDownload('ios')" aria-label="Télécharger Obsidian Read dans l'App Store">{APPLE}<span><small>Télécharger dans l'</small><strong>App Store</strong></span></a>
      <a class="badge" href="{STORE_ANDROID}" target="_blank" rel="noopener" onclick="trackDownload('android')" aria-label="Télécharger Obsidian Read sur Google Play">{GOOGLE}<span><small>Disponible sur</small><strong>Google Play</strong></span></a>
    </div>'''


# ─── Gabarit de page ────────────────────────────────────────────────────────
def head(title, description, path, extra=''):
    canonical = f'https://obsidianread.com{path}'
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{E(title)}</title>
<meta name="description" content="{E(description)}" />
<link rel="canonical" href="{canonical}" />
<meta name="theme-color" content="#0A0A0A" />
<meta name="apple-itunes-app" content="app-id=6770984110" />
<meta property="al:ios:url" content="obsidianread://" />
<meta property="al:ios:app_store_id" content="6770984110" />
<meta property="al:ios:app_name" content="Obsidian Read" />
<meta property="al:android:url" content="obsidianread://" />
<meta property="al:android:package" content="com.obsidianread.app" />
<meta property="al:android:app_name" content="Obsidian Read" />
<meta property="og:title" content="{E(title)}" />
<meta property="og:description" content="{E(description)}" />
<meta property="og:image" content="https://obsidianread.com/favicon.png" />
<meta property="og:url" content="{canonical}" />
<meta property="og:type" content="website" />
<meta property="og:locale" content="fr_FR" />
<link rel="icon" type="image/png" href="/favicon.png" />
<link rel="apple-touch-icon" href="/favicon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v=2" />
{extra}
<meta name="facebook-domain-verification" content="xnh7aa6yw7c30az1rn6q7ctvkrt1t9" />
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{PIXEL_ID}');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={PIXEL_ID}&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->
</head>
<body>
'''


def topbar(active=''):
    def L(name, href):
        on = ' class="on"' if name == active else ''
        return f'<a href="{href}"{on}>{name}</a>'
    return f'''<header class="topbar">
  <div class="row">
    <a class="brand" href="/"><img src="/favicon.png" alt="" width="34" height="34" /><span>Obsidian Read</span></a>
    <nav>
      {L('Les romans', '/romans/')}
      {L('Par envie', '/par-envie/')}
      {L('Abonnement', '/abonnement/')}
      {L('Nous écrire', '/contact/')}
      <a href="#" class="btn btn-nav" onclick="smartDownload();return false;">Télécharger<span class="nav-long"> l'application</span></a>
    </nav>
  </div>
</header>
'''


def final_cta():
    return f'''<section class="final">
  <div class="wrap">
    <h2>Tu as repéré une histoire ?</h2>
    <p>{E(APPEL)}</p>
    {badges('center')}
  </div>
</section>
'''


def footer():
    return f'''<footer class="foot">
  <div class="wrap">
    <div class="foot-row">
      <div class="foot-brand">
        <div class="brand"><img src="/favicon.png" alt="" width="28" height="28" /><span>Obsidian Read</span></div>
        <div class="foot-sign">{E(SIGNATURE)}</div>
        <div class="socials">
          <a href="https://www.tiktok.com/@obsidianread" target="_blank" rel="noopener" aria-label="TikTok">{TIKTOK}</a>
          <a href="https://www.instagram.com/obsidianread" target="_blank" rel="noopener" aria-label="Instagram">{INSTA}</a>
        </div>
      </div>
      <div class="foot-cols">
        <div class="foot-col">
          <div class="foot-h">Navigation</div>
          <a href="/romans/">Les romans</a><a href="/par-envie/">Par envie</a><a href="/abonnement/">Abonnement</a><a href="/contact/">Nous écrire</a>
        </div>
        <div class="foot-col">
          <div class="foot-h">Légal</div>
          <a href="/terms">Conditions générales</a><a href="/privacy">Confidentialité</a><a href="/delete-account/">Supprimer mon compte</a>
        </div>
      </div>
    </div>
    <div class="hair"></div>
    <div class="copyright">© 2026 Obsidian Read · Tous droits réservés</div>
  </div>
</footer>

<!-- Choix du store quand on ne détecte pas le téléphone (ordinateur) -->
<div class="modal-overlay" id="modal-overlay" onclick="closeModalOnBackdrop(event)">
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <button class="close" onclick="closeModal()" aria-label="Fermer">×</button>
    <h3 id="modal-title">Télécharge Obsidian Read</h3>
    <p>Disponible sur iPhone et Android.</p>
    {badges('column')}
  </div>
</div>

<script>
  const STORE_IOS = '{STORE_IOS}';
  const STORE_ANDROID = '{STORE_ANDROID}';
  function trackDownload(platform) {{
    try {{ if (window.fbq) fbq('trackCustom', 'DownloadClick', {{ platform: platform }}); }} catch (e) {{}}
  }}
  // Bouton générique : on envoie vers le store de l'appareil ; sur ordinateur, on propose les deux.
  function smartDownload() {{
    const ua = navigator.userAgent || '';
    const isIOS = /iPad|iPhone|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
    const isAndroid = /Android/.test(ua);
    if (isIOS) {{ trackDownload('ios'); window.location.href = STORE_IOS; return; }}
    if (isAndroid) {{ trackDownload('android'); window.location.href = STORE_ANDROID; return; }}
    openModal();
  }}
  function openModal() {{ document.getElementById('modal-overlay').classList.add('show'); document.body.style.overflow = 'hidden'; }}
  function closeModal() {{ document.getElementById('modal-overlay').classList.remove('show'); document.body.style.overflow = ''; }}
  function closeModalOnBackdrop(e) {{ if (e.target.id === 'modal-overlay') closeModal(); }}
  document.addEventListener('keydown', (e) => {{ if (e.key === 'Escape') closeModal(); }});
  // Flèches des carrousels
  document.querySelectorAll('[data-carousel]').forEach((btn) => {{
    btn.addEventListener('click', () => {{
      const track = document.getElementById(btn.getAttribute('data-carousel'));
      track.scrollBy({{ left: track.clientWidth * 0.8 * Number(btn.getAttribute('data-dir')), behavior: 'smooth' }});
    }});
  }});
</script>
</body>
</html>
'''


# ─── Composants catalogue ───────────────────────────────────────────────────
def book_card(slug):
    b = BY[slug]
    return f'''<article class="book" data-tags="{tags_of(slug)}">
  <a class="book-cover" href="#" onclick="smartDownload();return false;" aria-label="{E(b['title'])}"><img src="{E(b['cover_image_url'])}" alt="" loading="lazy" /></a>
  <div class="book-head">
    <div class="label">{E(trope_label(slug))}</div>
    <h3 class="book-title">{E(b['title'])}</h3>
  </div>
  <p class="book-summary">{E(b['summary'])}</p>
  <a class="link book-link" href="#" onclick="smartDownload();return false;">Lire sur l'application</a>
</article>'''


def car_item(slug):
    b = BY[slug]
    return f'''<div class="car-item">
      <a class="cover" href="#" onclick="smartDownload();return false;" aria-label="{E(b['title'])}"><img src="{E(b['cover_image_url'])}" alt="" loading="lazy" /></a>
      <div class="car-title">{E(b['title'])}</div>
      <div class="car-tag">{E(tagline(slug))}</div>
      <a class="link" href="#" onclick="smartDownload();return false;">Lire sur l'application</a>
    </div>'''


def carousel(slugs, cid='histoires'):
    return f'''<section class="carousel-wrap" id="{cid}">
  <div class="wrap">
    <div class="carousel-head">
      <h2>Découvre les histoires sur l'application</h2>
      <div class="arrows">
        <button type="button" class="arrow" data-carousel="track-{cid}" data-dir="-1" aria-label="Précédent"><svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></svg></button>
        <button type="button" class="arrow" data-carousel="track-{cid}" data-dir="1" aria-label="Suivant"><svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg></button>
      </div>
    </div>
    <div class="carousel" id="track-{cid}">
      {''.join(car_item(s) for s in slugs)}
    </div>
  </div>
</section>
'''


def chip(slug, on=False, href=None):
    _, em, label, _ = CAT_BY_SLUG[slug]
    href = href or f'/romans/#{slug}'
    return f'<a class="chip{" on" if on else ""}" href="{href}" data-cat="{slug}"><span class="em">{em}</span>{E(label)}</a>'


def chips_all():
    return '<div class="chips">' + ''.join(chip(c[0]) for c in CATS) + '</div>'


# ─── Pages ──────────────────────────────────────────────────────────────────
def page_index():
    body = topbar() + f'''
<section class="hero">
  <div class="wrap">
    <div class="label">{E(SIGNATURE)}</div>
    <h1>{E(APPEL)}</h1>
    <p class="hero-lede">Un faux couple qui devient jaloux. Des ennemis obligés de se côtoyer. Un premier amour qui revient au mauvais moment. Et bien d'autres.</p>
    <div class="hero-btns">
      <a href="#" class="btn" onclick="smartDownload();return false;">Télécharger l'application</a>
      <a href="#histoires" class="btn btn-ghost">Découvrir les romans</a>
    </div>
    <div class="muted">Disponible sur iPhone et Android.</div>
  </div>
</section>

<section class="cats">
  <div class="wrap">
    <div class="cats-head"><h2>Catégories populaires</h2><a class="link" href="/par-envie/">Afficher tout</a></div>
    {chips_all()}
  </div>
</section>

{carousel(ORDER)}

<section class="start">
  <div class="wrap">
    <h2>Par quelle histoire tu commences ?</h2>
    <div class="books">
      {book_card(ORDER[0])}
      {book_card(ORDER[1])}
    </div>
    <div class="center"><a href="/romans/" class="btn btn-ghost">Voir toutes les histoires</a></div>
  </div>
</section>

<section class="prefs">
  <div class="wrap prefs-row">
    <div class="prefs-left">
      <h2>Tu les préfères comment ?</h2>
      <p>Explore les romances selon ce que tu aimes lire.</p>
      {chips_all()}
    </div>
    <div class="prefs-lines">
      <div>Quand ils se détestent.</div>
      <div>Quand ils font semblant.</div>
      <div>Quand ils n'ont pas le droit.</div>
      <div>Quand ils se retrouvent.</div>
      <div class="gold">Et bien d'autres.</div>
    </div>
  </div>
</section>

<section class="comfort">
  <div class="wrap">
    <h2>Installe-toi. On s'occupe du confort.</h2>
    <p>Agrandis le texte, choisis ton fond de lecture et reprends ton histoire là où tu l'as laissée.</p>
    <p class="serif-line">À toi de choisir comment tu lis.</p>
  </div>
</section>

<section class="abo-band">
  <div class="wrap abo-row">
    <div>
      <div class="abo-title">Tout le catalogue avec un seul abonnement.</div>
      <div class="abo-sub">1,99 € la semaine ou 49,99 € l'année. Résiliable à tout moment depuis ton téléphone.</div>
    </div>
    <a href="#" class="btn" onclick="smartDownload();return false;">Télécharger l'application</a>
  </div>
</section>
''' + final_cta() + footer()
    return head('Obsidian Read — La romance a son application.',
                "Choisis ta prochaine romance sur Obsidian Read. Des romans écrits en français, à lire sur ton téléphone, avec un seul abonnement.",
                '/') + body


def page_romans():
    body = topbar('Les romans') + f'''
<section class="page-head">
  <div class="wrap">
    <div class="label">{E(SIGNATURE)}</div>
    <h1>Les romans</h1>
    <p>Tous les romans se lisent dans l'application, en entier, avec un seul abonnement.</p>
    <div class="chips" id="filters"><a class="chip on" href="#" data-cat="all"><span class="em">📚</span>Tous</a>{''.join(chip(c[0], href='#' + c[0]) for c in CATS)}</div>
  </div>
</section>
<section class="catalog">
  <div class="wrap">
    <div class="books" id="books">
      {''.join(book_card(s) for s in ORDER)}
    </div>
    <p class="muted empty" id="empty" hidden>Aucun roman dans cette catégorie pour l'instant.</p>
  </div>
</section>
''' + final_cta() + footer()
    body = body.replace('</body>', '''<script>
  // Filtre par catégorie : #slug dans l'adresse ou clic sur une pastille
  (function () {
    const chips = document.querySelectorAll('#filters .chip');
    const books = document.querySelectorAll('#books .book');
    const empty = document.getElementById('empty');
    function apply(cat) {
      let n = 0;
      books.forEach((b) => {
        const show = cat === 'all' || (' ' + b.getAttribute('data-tags') + ' ').indexOf(' ' + cat + ' ') !== -1;
        b.hidden = !show; if (show) n++;
      });
      chips.forEach((c) => c.classList.toggle('on', c.getAttribute('data-cat') === cat));
      empty.hidden = n > 0;
    }
    chips.forEach((c) => c.addEventListener('click', (e) => {
      e.preventDefault();
      const cat = c.getAttribute('data-cat');
      apply(cat);
      history.replaceState(null, '', cat === 'all' ? location.pathname : '#' + cat);
    }));
    const h = location.hash.replace('#', '');
    if (h && document.querySelector('#filters .chip[data-cat="' + h + '"]')) apply(h);
  })();
</script>
</body>''')
    return head('Les romans — Obsidian Read',
                "Tous les romans Obsidian Read : enemies to lovers, faux couple, huis clos, dark romance… écrits en français, à lire dans l'application.",
                '/romans/') + body


def page_envie():
    rows = ''
    for line, cslug in ENVIES:
        _, em, label, slugs = CAT_BY_SLUG[cslug]
        covers = ''.join(
            f'<a class="mini" href="#" onclick="smartDownload();return false;"><span class="cover"><img src="{E(BY[s]["cover_image_url"])}" alt="" loading="lazy" /></span><span class="mini-title">{E(BY[s]["title"])}</span></a>'
            for s in slugs)
        rows += f'''<div class="envie" id="{cslug}">
      <div class="envie-left">
        <div class="envie-line">{E(line)}</div>
        {chip(cslug)}
      </div>
      <div class="envie-covers">{covers}</div>
    </div>'''
    body = topbar('Par envie') + f'''
<section class="page-head">
  <div class="wrap">
    <div class="label">Par envie</div>
    <h1>Tu les préfères comment ?</h1>
    <p>Explore les romances selon ce que tu aimes lire. Chaque envie renvoie aux romans qui y répondent.</p>
  </div>
</section>
<section class="envies">
  <div class="wrap">{rows}</div>
</section>
''' + final_cta() + footer()
    return head('Par envie — Obsidian Read',
                "Quand ils se détestent, quand ils font semblant, quand ils n'ont pas le droit… Trouve la romance Obsidian Read qui te ressemble.",
                '/par-envie/') + body


def offer(name, price, per, sub, best=False):
    tag = '<span class="tag">Meilleur prix</span>' if best else ''
    return f'''<div class="offer{' best' if best else ''}">
      <div class="offer-head"><span class="offer-name">{name}</span>{tag}</div>
      <div class="offer-price"><span class="amount">{price}</span><span class="per">{per}</span></div>
      <div class="offer-sub">{sub}</div>
      <div class="hair"></div>
      <ul class="offer-list">
        <li>Tous les romans, en entier</li>
        <li>Les nouveautés dès leur sortie</li>
        <li>Sur iPhone et Android</li>
        <li>Résiliable à tout moment</li>
      </ul>
      <a href="#" class="btn{'' if best else ' btn-ghost'}" onclick="smartDownload();return false;">Télécharger l'application</a>
    </div>'''


def page_abonnement():
    faq = [
        ("Où est-ce que je m'abonne ?", "Dans l'application, après l'avoir téléchargée. Le paiement passe par ton compte App Store ou Google Play."),
        ("Est-ce que je peux arrêter quand je veux ?", "Oui. Tu résilies depuis les réglages de ton téléphone, à tout moment. Tu gardes l'accès jusqu'à la fin de la période déjà payée."),
        ("Est-ce que je retrouve mes lectures sur un autre téléphone ?", "Oui. Ta bibliothèque et ta progression sont liées à ton compte, pas à ton appareil."),
    ]
    faq_html = ''.join(f'<div class="faq"><h3>{E(q)}</h3><p>{E(a)}</p></div>' for q, a in faq)
    body = topbar('Abonnement') + f'''
<section class="page-head center">
  <div class="wrap">
    <div class="label">Abonnement</div>
    <h1>Tout le catalogue avec un seul abonnement.</h1>
    <p>Chaque roman, chaque chapitre, et tous ceux qui arrivent. Tu choisis la durée, tu arrêtes quand tu veux.</p>
  </div>
</section>
<section class="offers">
  <div class="wrap">
    <div class="offers-grid">
      {offer('Annuel', '49,99 €', 'par an', 'Soit 4,17 € par mois', True)}
      {offer('Hebdomadaire', '1,99 €', 'par semaine', "Pour essayer sans t'engager")}
    </div>
    <div class="faqs">
      <h2>Questions fréquentes</h2>
      {faq_html}
      <p class="muted small">Tarifs affichés pour la France. Le prix exact est indiqué dans l'application avant tout paiement. L'abonnement se renouvelle automatiquement, sauf résiliation avant la fin de la période en cours.</p>
    </div>
  </div>
</section>
''' + final_cta() + footer()
    return head('Abonnement — Obsidian Read',
                "Un seul abonnement pour tout le catalogue Obsidian Read : 1,99 € la semaine ou 49,99 € l'année, résiliable à tout moment.",
                '/abonnement/') + body


def page_contact():
    body = topbar('Nous écrire') + '''
<section class="contact">
  <div class="wrap contact-row">
    <div class="contact-intro">
      <div class="label">Nous écrire</div>
      <h1>On te lit.</h1>
      <p class="lede">Une question sur l'application, sur ton abonnement, ou juste envie de dire ce que tu as pensé d'un roman ? Écris-nous, on répond sous 24 à 48 h ouvrées.</p>
      <div class="contact-alt alt-contact">
        <div>Par e-mail : <a class="link" href="mailto:contact@obsidianread.com">contact@obsidianread.com</a></div>
        <div>Sur <a class="link" href="https://www.instagram.com/obsidianread" target="_blank" rel="noopener">Instagram</a> et <a class="link" href="https://www.tiktok.com/@obsidianread" target="_blank" rel="noopener">TikTok</a> : @obsidianread</div>
      </div>
      <p class="muted small">Pour résilier ton abonnement, passe par les réglages de ton téléphone. Pour supprimer ton compte, <a class="link" href="/delete-account/">c'est ici</a>.</p>
    </div>

    <div class="card form-card">
      <form id="contact-form" action="https://api.web3forms.com/submit" method="POST">
        <!-- Clé Web3Forms publique — formulaire envoie vers contact@obsidianread.com -->
        <input type="hidden" name="access_key" value="d0144669-c9e5-4540-8702-c9d43152ee20">
        <input type="hidden" name="from_name" value="Formulaire Obsidian Read">
        <input type="hidden" name="subject" value="[obsidianread.com/contact] Nouveau message">
        <input type="checkbox" name="botcheck" style="display:none;">
        <div class="two">
          <div class="field">
            <label for="name">Ton prénom</label>
            <input type="text" id="name" name="name" required placeholder="Ex : Camille">
          </div>
          <div class="field">
            <label for="email">Ton e-mail</label>
            <input type="email" id="email" name="email" required placeholder="ton.email@exemple.com">
          </div>
        </div>
        <div class="field">
          <label for="reason">De quoi veux-tu parler ?</label>
          <select id="reason" name="reason" required>
            <option value="" disabled selected>Choisis un sujet…</option>
            <option value="Bug ou problème technique">Bug ou problème technique</option>
            <option value="Question sur mon abonnement">Question sur mon abonnement</option>
            <option value="Question sur les Frissons">Question sur les Frissons</option>
            <option value="Suggestion ou idée">Suggestion ou idée</option>
            <option value="Donnees personnelles / RGPD">Données personnelles / RGPD</option>
            <option value="Collaboration / partenariat">Collaboration / partenariat</option>
            <option value="Autre">Autre</option>
          </select>
        </div>
        <div class="field">
          <label for="message">Ton message</label>
          <textarea id="message" name="message" required placeholder="Raconte-nous tout…"></textarea>
        </div>
        <button type="submit" class="btn" id="submit-btn">Envoyer</button>
        <div id="status" class="status" hidden></div>
      </form>
      <div id="success-screen" class="success" hidden>
        <div class="check">✓</div>
        <h2>Message envoyé !</h2>
        <p>On a bien reçu ton message. On te répond sous 24 à 48 h ouvrées sur l'e-mail que tu nous as donné.</p>
        <button type="button" class="btn btn-ghost" onclick="resetForm()">Envoyer un autre message</button>
      </div>
    </div>
  </div>
</section>
''' + footer()
    body = body.replace('</body>', '''<script>
  const form = document.getElementById('contact-form');
  const status = document.getElementById('status');
  const submitBtn = document.getElementById('submit-btn');
  const successScreen = document.getElementById('success-screen');
  function showSuccess() { form.hidden = true; successScreen.hidden = false; window.scrollTo({ top: 0, behavior: 'smooth' }); }
  function resetForm() { form.reset(); form.hidden = false; successScreen.hidden = true; status.hidden = true; }
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitBtn.disabled = true; submitBtn.textContent = 'Envoi en cours…'; status.hidden = true;
    try {
      const response = await fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
      const data = await response.json();
      if (data.success) { showSuccess(); }
      else { status.hidden = false; status.textContent = "Erreur lors de l'envoi. Écris-nous directement à contact@obsidianread.com."; }
    } catch (err) {
      status.hidden = false; status.textContent = "Erreur de connexion. Écris-nous directement à contact@obsidianread.com.";
    }
    submitBtn.disabled = false; submitBtn.textContent = 'Envoyer';
  });
</script>
</body>''')
    return head('Nous écrire — Obsidian Read',
                "Une question sur l'application ou ton abonnement Obsidian Read ? Écris-nous, on répond sous 24 à 48 h.",
                '/contact/') + body


# ─── Feuille de style ───────────────────────────────────────────────────────
CSS = r'''/* obsidianread.com — généré par build/build_site.py. Direction validée le 2026-09-14 : noir, or, crème. */
:root{--bg:#0A0A0A;--bg2:#0E0A0C;--surface:#120E10;--chip:#221C1E;--line:#1E181B;--line2:#2A2326;--text:#F5F1E8;--text2:#C9C4BC;--muted:#6B6368;--gold:#C9A961;--gold2:#E8D5C0}
*{box-sizing:border-box;margin:0;padding:0}
[hidden]{display:none!important}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font-family:'Inter','Helvetica Neue',Arial,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
button{font-family:inherit;cursor:pointer;border:0;background:none;color:inherit}
h1,h2,h3,.serif{font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-weight:700;line-height:1.1}
h1{font-size:clamp(34px,5vw,66px);letter-spacing:-0.01em}
h2{font-size:clamp(30px,3.4vw,46px)}
h3{font-size:26px;line-height:1.15}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.center{text-align:center}
.label{font-size:12px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--gold)}
.muted{color:var(--muted);font-size:14px}
.small{font-size:13px;line-height:1.6}
.link{color:var(--gold);font-weight:600;font-size:14px}
.link:hover{color:var(--gold2)}
.hair{height:1px;background:var(--line2)}
.btn{display:inline-flex;align-items:center;justify-content:center;height:52px;padding:0 30px;border-radius:999px;background:var(--gold);color:#0A0A0A;font-weight:600;font-size:15px;transition:background .15s,transform .15s}
.btn:hover{background:var(--gold2);transform:translateY(-1px)}
.btn-ghost{background:transparent;border:1px solid var(--text);color:var(--text)}
.btn-ghost:hover{background:var(--text);color:#0A0A0A}
.btn-nav{height:42px;padding:0 22px;font-size:14px}
/* topbar */
.topbar{position:sticky;top:0;z-index:100;background:rgba(10,10,10,.88);backdrop-filter:blur(18px) saturate(180%);-webkit-backdrop-filter:blur(18px) saturate(180%);border-bottom:1px solid var(--line)}
.topbar .row{max-width:1180px;margin:0 auto;padding:0 20px;height:72px;display:flex;align-items:center;justify-content:space-between;gap:20px}
.brand{display:flex;align-items:center;gap:12px;font-family:'Playfair Display',serif;font-weight:700;font-size:20px;white-space:nowrap}
.btn{white-space:nowrap}
.brand img{width:34px;height:34px;border-radius:8px}
.topbar nav{display:flex;align-items:center;gap:32px}
.topbar nav a:not(.btn){color:var(--text2);font-size:14px;font-weight:500}
.topbar nav a:not(.btn):hover,.topbar nav a.on{color:var(--text)}
/* hero */
.hero{position:relative;overflow:hidden;text-align:center;padding:96px 0 80px}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 700px 420px at 50% 100%,rgba(201,169,97,.12),transparent 70%);pointer-events:none}
.hero .wrap{position:relative;display:flex;flex-direction:column;align-items:center;gap:24px}
.hero h1{max-width:980px}
.hero-lede{font-family:'Playfair Display',Georgia,serif;font-size:clamp(18px,1.6vw,22px);line-height:1.5;color:var(--gold2);max-width:720px;margin-top:-4px}
.hero-btns{display:flex;gap:14px;flex-wrap:wrap;justify-content:center;margin-top:8px}
/* catégories */
.cats{padding:8px 0 24px}
.cats-head{display:flex;align-items:baseline;gap:18px;margin-bottom:20px}
.cats-head h2{font-size:30px}
.chips{display:flex;flex-wrap:wrap;gap:12px}
.chip{display:inline-flex;align-items:center;gap:8px;height:46px;padding:0 20px;border-radius:999px;background:var(--chip);border:1px solid var(--line2);color:var(--text);font-size:15px;font-weight:600;transition:background .15s,color .15s}
.chip .em{font-size:17px;line-height:1}
.chip:hover,.chip.on{background:var(--gold);border-color:var(--gold);color:#0A0A0A}
/* carrousel */
.carousel-wrap{padding:40px 0 24px}
.carousel-head{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:22px}
.carousel-head h2{font-size:clamp(26px,2.4vw,30px)}
.arrows{display:flex;gap:10px;flex:none}
.arrow{width:44px;height:44px;border-radius:999px;border:1px solid var(--line2);display:flex;align-items:center;justify-content:center}
.arrow:hover{border-color:var(--gold)}
.arrow svg{width:18px;height:18px;stroke:var(--text);fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.carousel{display:flex;gap:22px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:8px}
.carousel::-webkit-scrollbar{display:none}
.car-item{flex:0 0 218px;scroll-snap-align:start;display:flex;flex-direction:column;gap:10px}
.cover{display:block;border-radius:8px;overflow:hidden;background:#211A1D;box-shadow:0 14px 30px rgba(0,0,0,.55);aspect-ratio:9/16}
.cover img{width:100%;height:100%;object-fit:cover}
.car-title{font-family:'Playfair Display',serif;font-weight:700;font-size:18px;line-height:1.2}
.car-tag{font-size:13px;line-height:1.5;color:var(--text2)}
/* cartes romans */
.start{padding:40px 0 64px}
.start h2{margin-bottom:32px}
.start .center{margin-top:32px}
.books{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px}
.book{background:var(--surface);border:1px solid var(--line2);border-radius:16px;padding:24px;display:grid;grid-template-columns:156px minmax(0,1fr);grid-template-areas:"cover head" "cover summary" "cover link";column-gap:24px;row-gap:12px;align-content:start}
.book[hidden]{display:none}
.book-cover{grid-area:cover;align-self:start}
.book-cover{display:block;border-radius:8px;overflow:hidden;background:#211A1D;box-shadow:0 14px 30px rgba(0,0,0,.55);aspect-ratio:9/16}
.book-cover img{width:100%;height:100%;object-fit:cover}
.book-head{grid-area:head;display:flex;flex-direction:column;gap:10px}
.book-head .label{font-size:11px}
.book-summary{grid-area:summary;font-size:14px;line-height:1.6;color:var(--text2)}
.book-link{grid-area:link;align-self:end}
/* préférences */
.prefs{background:var(--bg2);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:88px 0}
.prefs-row{display:flex;align-items:center;justify-content:space-between;gap:60px}
.prefs-left{max-width:600px;display:flex;flex-direction:column;gap:22px}
.prefs-left p{font-size:17px;color:var(--text2)}
.prefs-lines{font-family:'Playfair Display',serif;font-size:clamp(26px,2.8vw,38px);line-height:1.3;color:var(--gold2);display:flex;flex-direction:column;gap:8px;flex:none}
.prefs-lines .gold{color:var(--gold)}
/* confort */
.comfort{padding:88px 0;text-align:center}
.comfort .wrap{display:flex;flex-direction:column;align-items:center;gap:18px;max-width:760px}
.comfort p{font-size:18px;color:var(--text2)}
.serif-line{font-family:'Playfair Display',serif;font-size:22px;color:var(--gold2)}
/* bandeau abonnement */
.abo-band{background:var(--bg2);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:56px 0}
.abo-row{display:flex;align-items:center;justify-content:space-between;gap:40px}
.abo-title{font-family:'Playfair Display',serif;font-weight:700;font-size:28px;line-height:1.2;margin-bottom:8px}
.abo-sub{font-size:16px;color:var(--text2)}
/* fin de page */
.final{position:relative;overflow:hidden;padding:96px 0;text-align:center}
.final::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 700px 400px at 50% 100%,rgba(201,169,97,.12),transparent 70%);pointer-events:none}
.final .wrap{position:relative;display:flex;flex-direction:column;align-items:center;gap:22px}
.final h2{font-size:clamp(34px,4vw,54px)}
.final p{font-size:18px;color:var(--text2);max-width:640px}
.badges{display:flex;gap:12px;flex-wrap:wrap}
.badges.center{justify-content:center}
.badges.column{flex-direction:column}
.badge{display:flex;align-items:center;justify-content:center;gap:12px;height:56px;padding:0 22px 0 18px;border:1px solid var(--gold);border-radius:14px;color:var(--text);transition:background .15s}
.badge:hover{background:rgba(201,169,97,.12)}
.badge svg{width:24px;height:24px;flex:none}
.badge small{display:block;font-size:10px;font-weight:500;line-height:1;color:var(--gold)}
.badge strong{display:block;font-size:17px;font-weight:600;line-height:1.15}
/* footer */
.foot{border-top:1px solid var(--line);padding:56px 0 40px}
.foot-row{display:flex;justify-content:space-between;gap:60px;margin-bottom:40px}
.foot-brand{display:flex;flex-direction:column;gap:14px;max-width:320px}
.foot-brand .brand{font-size:18px}.foot-brand .brand img{width:28px;height:28px;border-radius:7px}
.foot-sign{font-size:14px;color:var(--text2)}
.socials{display:flex;gap:14px}.socials a{color:var(--text2)}.socials a:hover{color:var(--text)}.socials svg{width:20px;height:20px}
.foot-cols{display:flex;gap:80px}
.foot-col{display:flex;flex-direction:column;gap:12px}
.foot-col a{color:var(--text2);font-size:14px}.foot-col a:hover{color:var(--text)}
.foot-h{font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.copyright{font-size:13px;color:var(--muted);margin-top:40px}
/* modale */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);display:none;align-items:center;justify-content:center;z-index:1000;padding:20px}
.modal-overlay.show{display:flex}
.modal{background:var(--surface);border:1px solid var(--line2);border-radius:20px;padding:36px;max-width:420px;width:100%;position:relative;text-align:center;display:flex;flex-direction:column;gap:14px}
.modal h3{font-size:26px}.modal p{color:var(--text2);font-size:14px}
.modal .close{position:absolute;top:12px;right:16px;font-size:28px;color:var(--muted)}
/* pages intérieures */
.page-head{padding:80px 0 32px}
.page-head .wrap{display:flex;flex-direction:column;gap:18px}
.page-head p{font-size:18px;color:var(--text2);max-width:720px}
.page-head.center{text-align:center}.page-head.center .wrap{align-items:center}
.catalog{padding:24px 0 80px}
.empty{margin-top:24px}
.envies{padding:16px 0 80px}
.envie{display:flex;gap:60px;align-items:flex-start;padding:36px 0;border-top:1px solid var(--line)}
.envie-left{width:420px;flex:none;display:flex;flex-direction:column;gap:12px;align-items:flex-start}
.envie-line{font-family:'Playfair Display',serif;font-size:32px;line-height:1.2;color:var(--gold2)}
.envie-covers{display:flex;gap:18px;flex-wrap:wrap}
.mini{width:108px;display:flex;flex-direction:column;gap:8px}
.mini-title{font-size:12px;line-height:1.35;color:var(--text2)}
.offers{padding:24px 0 96px}
.offers-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;max-width:840px;margin:0 auto}
.offer{background:var(--surface);border:1px solid var(--line2);border-radius:16px;padding:36px;display:flex;flex-direction:column;gap:18px}
.offer.best{border-color:var(--gold)}
.offer-head{display:flex;justify-content:space-between;align-items:center}
.offer-name{font-size:16px;font-weight:600}
.tag{font-size:11px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#0A0A0A;background:var(--gold);padding:6px 10px;border-radius:999px}
.offer-price{display:flex;align-items:baseline;gap:8px}
.amount{font-family:'Playfair Display',serif;font-weight:700;font-size:48px;line-height:1}
.per{font-size:16px;color:var(--text2)}
.offer-sub{font-size:14px;color:var(--gold)}
.offer-list{list-style:none;display:flex;flex-direction:column;gap:10px;font-size:15px;color:var(--text2)}
.faqs{max-width:840px;margin:64px auto 0;display:flex;flex-direction:column}
.faqs h2{font-size:36px;margin-bottom:16px}
.faq{padding:26px 0;border-top:1px solid var(--line)}
.faq h3{font-size:22px;margin-bottom:8px}.faq p{font-size:15px;color:var(--text2)}
.faqs .muted{padding-top:22px;border-top:1px solid var(--line)}
.contact{padding:80px 0 96px}
.contact-row{display:flex;gap:80px;align-items:flex-start}
.contact-intro{max-width:440px;display:flex;flex-direction:column;gap:20px}
.contact-intro h1{font-size:clamp(40px,4vw,56px)}
.contact-intro .lede{font-size:18px;color:var(--text2)}
.contact-alt{display:flex;flex-direction:column;gap:10px;font-size:15px;color:var(--text2)}
.card{background:var(--surface);border:1px solid var(--line2);border-radius:16px}
.form-card{flex:1;padding:40px}
.form-card form{display:flex;flex-direction:column;gap:22px}
.two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.field{display:flex;flex-direction:column;gap:8px}
.field label{font-size:13px;font-weight:600;color:var(--text2)}
.field input,.field select,.field textarea{height:52px;border-radius:12px;border:1px solid var(--line2);background:var(--bg);padding:0 16px;color:var(--text);font-size:15px;font-family:inherit;width:100%}
.field textarea{height:160px;padding:14px 16px;resize:vertical}
.field input:focus,.field select:focus,.field textarea:focus{outline:none;border-color:var(--gold)}
.field select{appearance:none;-webkit-appearance:none}
.form-card .btn{align-self:flex-start}
.status{color:#E84570;font-size:14px}
.success{text-align:center;display:flex;flex-direction:column;align-items:center;gap:14px;padding:20px 0}
.success .check{width:56px;height:56px;border-radius:999px;border:1px solid var(--gold);color:var(--gold);display:flex;align-items:center;justify-content:center;font-size:26px}
.success p{color:var(--text2)}
/* ─── Téléphone / tablette ─── */
@media (max-width:900px){
  .topbar nav{gap:16px}.topbar nav a:not(.btn){display:none}
  .btn-nav{height:38px;padding:0 16px;font-size:13px}.nav-long{display:none}
  .topbar .row{height:60px}.brand{font-size:18px;gap:10px}.brand img{width:30px;height:30px}
  .hero-lede{font-size:17px}
  .hero{padding:52px 0 40px}.hero .wrap{gap:18px}
  .hero-btns{flex-direction:column;align-self:stretch}.hero-btns .btn{width:100%}
  .cats-head h2{font-size:24px}
  .chip{height:42px;padding:0 15px;font-size:14px;gap:7px}
  .chips{gap:10px}
  .carousel-head h2{font-size:22px}
  .carousel{gap:14px}.car-item{flex-basis:150px}
  .car-title{font-size:15px}.car-tag{font-size:12px}
  .books{grid-template-columns:1fr;gap:18px}
  .book{padding:18px;grid-template-columns:104px minmax(0,1fr);grid-template-areas:"cover head" "summary summary" "link link";column-gap:16px}
  .book-head{padding-top:2px}.book-head h3{font-size:22px}
  .start .center .btn{width:100%}
  .prefs{padding:56px 0}.prefs-row{flex-direction:column-reverse;align-items:flex-start;gap:24px}
  .comfort{padding:56px 0}
  .abo-band{padding:44px 0}.abo-row{flex-direction:column;align-items:flex-start}.abo-title{font-size:26px}
  .final{padding:60px 0}.badges{flex-direction:column;align-self:stretch}.badges.center{align-items:stretch}
  .foot{padding:40px 0 32px}.foot-row{flex-direction:column;gap:28px}.foot-cols{gap:40px}
  .page-head{padding:44px 0 24px}
  .envie{flex-direction:column;gap:20px;padding:28px 0}.envie-left{width:auto}.envie-line{font-size:26px}
  .mini{width:96px}
  .offers-grid{grid-template-columns:1fr}.offer{padding:24px}.amount{font-size:38px}
  .faqs{margin-top:44px}.faqs h2{font-size:30px}
  .contact{padding:44px 0 64px}.contact-row{flex-direction:column;gap:32px}
  .form-card{padding:22px;width:100%}.two{grid-template-columns:1fr}.form-card .btn{align-self:stretch}
}
'''


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print('écrit', path, f'({len(content) // 1024} Ko)')


if __name__ == '__main__':
    write('assets/site.css', CSS)
    write('index.html', page_index())
    write('romans/index.html', page_romans())
    write('par-envie/index.html', page_envie())
    write('abonnement/index.html', page_abonnement())
    write('contact/index.html', page_contact())
