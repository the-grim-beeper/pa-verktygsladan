TOOLS = [
    {
        "slug": "media-trainer",
        "name": "Medietr\u00e4ning",
        "desc": "AI-analys av video \u2014 f\u00e5 tidst\u00e4mplad feedback p\u00e5 kroppsspr\u00e5k, r\u00f6st och budskap.",
        "icon": "\U0001f3ac",
    },
    {
        "slug": "lulea",
        "name": "Lule\u00e5-analys",
        "desc": "Strategisk beslutsanalys f\u00f6r Lule\u00e5-klassens ytstridsfartyg.",
        "icon": "\U0001f6a2",
    },
    {
        "slug": "svenska-roster",
        "name": "Syntetisk Fokusgrupp",
        "desc": "Multi-agent fokusgrupp med genuint diversa AI-deltagare.",
        "icon": "\U0001f5e3\ufe0f",
    },
    {
        "slug": "buss49p",
        "name": "Buss 49P",
        "desc": "Beslutst\u00f6d f\u00f6r FMV:s Buss 49P upphandling.",
        "icon": "\U0001f68c",
    },
    {
        "slug": "decision-engine",
        "name": "Beslutsmotor",
        "desc": "Generell AI-st\u00f6dd beslutsmodellering med dokumentanalys.",
        "icon": "\u2696\ufe0f",
    },
]


def landing_page_html() -> str:
    cards = ""
    for t in TOOLS:
        cards += (
            f'<a href="/tools/{t["slug"]}/" class="card">'
            f'<span class="icon">{t["icon"]}</span>'
            f'<h2>{t["name"]}</h2>'
            f'<p>{t["desc"]}</p>'
            f'</a>'
        )

    return (
        '<!DOCTYPE html>\n'
        '<html lang="sv">\n'
        '<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>PA Verktygsl\u00e5dan</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">\n'
        '<style>\n'
        '*{margin:0;padding:0;box-sizing:border-box}\n'
        "body{min-height:100vh;background:#030712;color:#f3f4f6;font-family:'Inter',system-ui,sans-serif}\n"
        'header{border-bottom:1px solid #1f2937;padding:1.5rem 2rem}\n'
        'header h1{font-size:1.5rem;font-weight:700;letter-spacing:-0.02em}\n'
        'header span{color:#6b7280;font-weight:400;font-size:0.9rem;margin-left:0.75rem}\n'
        'main{max-width:72rem;margin:0 auto;padding:3rem 1.5rem}\n'
        '.subtitle{text-align:center;color:#9ca3af;margin-bottom:2.5rem;font-size:1.05rem}\n'
        '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.25rem}\n'
        '.card{display:block;background:#111827;border:1px solid #1f2937;border-radius:1rem;padding:1.75rem;\n'
        '       text-decoration:none;color:inherit;transition:border-color .2s,transform .15s}\n'
        '.card:hover{border-color:#3b82f6;transform:translateY(-2px)}\n'
        '.icon{font-size:2rem;display:block;margin-bottom:0.75rem}\n'
        '.card h2{font-size:1.1rem;font-weight:600;margin-bottom:0.5rem}\n'
        '.card p{color:#9ca3af;font-size:0.875rem;line-height:1.5}\n'
        '</style>\n'
        '</head>\n'
        '<body>\n'
        '<header><h1>PA Verktygsl\u00e5dan<span>Analysverktyg</span></h1></header>\n'
        '<main>\n'
        '  <p class="subtitle">V\u00e4lj ett verktyg nedan f\u00f6r att komma ig\u00e5ng.</p>\n'
        f'  <div class="grid">{cards}</div>\n'
        '</main>\n'
        '</body>\n'
        '</html>'
    )


LOGIN_PAGE = """\
<!DOCTYPE html>
<html lang="sv">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Logga in \u2014 PA Verktygsl\u00e5dan</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{min-height:100vh;display:flex;align-items:center;justify-content:center;
       background:#030712;color:#f3f4f6;font-family:'Inter',system-ui,sans-serif}
  .card{background:#111827;border:1px solid #374151;border-radius:1rem;padding:2.5rem;width:100%;max-width:360px}
  h1{font-size:1.25rem;margin:0 0 1.5rem}
  input{width:100%;padding:.75rem;border-radius:.5rem;border:1px solid #4b5563;
        background:#1f2937;color:#f3f4f6;font-size:1rem;box-sizing:border-box}
  input:focus{outline:none;border-color:#3b82f6}
  button{width:100%;margin-top:1rem;padding:.75rem;border-radius:.5rem;border:none;
         background:#3b82f6;color:#fff;font-size:1rem;cursor:pointer;font-weight:500}
  button:hover{background:#2563eb}
  .err{color:#f87171;font-size:.875rem;margin-top:.75rem;display:none}
</style></head>
<body><div class="card"><h1>PA Verktygsl\u00e5dan</h1>
<form method="POST" action="/login">
  <input type="password" name="password" placeholder="L\u00f6senord" autofocus>
  <button type="submit">Logga in</button>
  %%ERROR%%
</form></div></body></html>"""
