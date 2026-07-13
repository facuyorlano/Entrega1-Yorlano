from __future__ import annotations

import base64
import gzip
import shutil
import traceback
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
CHUNKS = ROOT / "chunks"
ERROR_FILE = ROOT / "build_error.txt"


def decompress_gzip_tolerant(data: bytes) -> bytes:
    try:
        return gzip.decompress(data)
    except gzip.BadGzipFile as exc:
        print(f"Advertencia: {exc}. Se intentará recuperar el flujo DEFLATE.", flush=True)

    if len(data) < 18 or data[:3] != b"\x1f\x8b\x08":
        raise ValueError("El paquete no contiene un encabezado GZIP compatible")

    flags = data[3]
    pos = 10
    if flags & 0x04:
        xlen = int.from_bytes(data[pos:pos + 2], "little")
        pos += 2 + xlen
    if flags & 0x08:
        pos = data.index(b"\0", pos) + 1
    if flags & 0x10:
        pos = data.index(b"\0", pos) + 1
    if flags & 0x02:
        pos += 2

    if pos >= len(data) - 8:
        raise ValueError("El paquete GZIP está incompleto")

    recovered = zlib.decompress(data[pos:-8], -zlib.MAX_WBITS)
    print(f"Flujo recuperado ignorando el tráiler CRC: {len(recovered):,} bytes", flush=True)
    return recovered


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

    parts: list[str] = []
    for index in range(5):
        path = CHUNKS / f"{index}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Falta {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: {len(text):,} caracteres", flush=True)
        parts.append(text)

    payload = "".join("".join(parts).split())
    print(f"Payload Base64: {len(payload):,} caracteres; inicio={payload[:12]!r}", flush=True)
    if not payload.startswith("H4sI"):
        raise ValueError(f"Encabezado Base64 inesperado: {payload[:16]!r}")

    compressed = base64.b64decode(payload, validate=True)
    print(f"Paquete comprimido: {len(compressed):,} bytes", flush=True)
    html_bytes = decompress_gzip_tolerant(compressed)
    html = html_bytes.decode("utf-8")

    if "<html" not in html.lower() or "</html>" not in html.lower():
        raise ValueError("El contenido reconstruido no es un HTML completo")

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

    if "<head>" not in html:
        raise ValueError("No se encontró la etiqueta <head>")
    html = html.replace("<head>", "<head>\n" + gate, 1)

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
