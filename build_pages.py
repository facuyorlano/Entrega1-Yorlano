from __future__ import annotations

import base64
import gzip
import shutil
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
CHUNKS = ROOT / "chunks"
ERROR_FILE = ROOT / "build_error.txt"


def main() -> None:
    if ERROR_FILE.exists():
        ERROR_FILE.unlink()
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    for name in ("index.html", "supabase-config.json", ".nojekyll"):
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, DIST / name)

    inner_parts: list[str] = []
    for index in range(5):
        path = CHUNKS / f"{index}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Falta {path.relative_to(ROOT)}")
        outer = "".join(path.read_text(encoding="utf-8").split())
        decoded = base64.b64decode(outer, validate=True).decode("ascii")
        print(
            f"{path.relative_to(ROOT)}: {len(outer):,} caracteres externos; "
            f"{len(decoded):,} internos",
            flush=True,
        )
        inner_parts.append(decoded)

    payload = "".join(inner_parts)
    print(f"Payload GZIP Base64: {len(payload):,}; inicio={payload[:12]!r}", flush=True)
    if not payload.startswith("H4sI"):
        raise ValueError(f"Encabezado Base64 inesperado: {payload[:16]!r}")

    compressed = base64.b64decode(payload, validate=True)
    html = gzip.decompress(compressed).decode("utf-8")

    if "<html" not in html.lower() or "</html>" not in html.lower():
        raise ValueError("El contenido reconstruido no es un HTML completo")
    if "const RESOURCES=" not in html or "const UNITS=" not in html:
        raise ValueError("El HTML no contiene el programa dinámico completo")

    gate = r'''<script>
(() => {
  try {
    const state = JSON.parse(localStorage.getItem('ia360-advanced') || '{}');
    const session = state?.cloud?.session;
    const email = String(session?.user?.email || '').toLowerCase();
    const expired = session?.expires_at && Date.now() >= session.expires_at * 1000;
    if (!session?.access_token || email !== 'efacundoyorlano@gmail.com' || expired) {
      location.replace('./');
    }
  } catch (_) {
    location.replace('./');
  }
})();
</script>'''

    lower = html.lower()
    head_index = lower.find("<head>")
    if head_index < 0:
        raise ValueError("No se encontró la etiqueta <head>")
    insert_at = head_index + len("<head>")
    html = html[:insert_at] + "\n" + gate + html[insert_at:]

    output = DIST / "app.html"
    output.write_text(html, encoding="utf-8")
    print(f"Generado {output.relative_to(ROOT)}: {output.stat().st_size:,} bytes", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        details = traceback.format_exc()
        ERROR_FILE.write_text(details, encoding="utf-8")
        print(details, flush=True)
        raise
