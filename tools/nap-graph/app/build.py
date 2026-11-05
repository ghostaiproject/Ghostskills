"""Build the Nap Planner artifact page: app/page.html + style.css + calc/dial/ui js -> app/dist/index.html."""
from pathlib import Path

here = Path(__file__).parent
page = (here / "page.html").read_text(encoding="utf-8")
css = (here / "style.css").read_text(encoding="utf-8")
js = "\n".join((here / f).read_text(encoding="utf-8") for f in ("calc.js", "dial.js", "ui.js"))
out = here / "dist" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(page.replace("/*CSS*/", css).replace("/*JS*/", js), encoding="utf-8")
(here / "dist" / "preview.html").write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' + out.read_text(encoding="utf-8"), encoding="utf-8")
print(f"built {out} ({out.stat().st_size // 1024} KB)")
