#!/usr/bin/env python3
"""Script de actualización one-time para agregar campos de versioning a todas las fuentes del Cerebro #1.

Campos a agregar:
- version: "1.0.0"
- last_updated: "2026-02-22"
- changelog
- status: "active"
"""

import re
from pathlib import Path
from datetime import date

SOURCES_DIR = Path("/home/rpadron/proy/mastermind/docs/software-development/01-product-strategy-brain/sources")

# Campos de versioning a agregar
VERSIONING_YAML = """version: "1.0.0"
last_updated: "2026-02-22"
changelog:
  - version: "1.0.0"
    date: "2026-02-22"
    changes:
      - "Destilación inicial completa"
status: "active"
"""


def add_versioning_to_source(filepath: Path) -> bool:
    """Agrega campos de versioning al YAML front matter de una fuente."""
    content = filepath.read_text()

    # Verificar si ya tiene version field
    if "version:" in content and "changelog:" in content:
        print(f"✓ {filepath.name}: Ya tiene versioning")
        return False

    # Buscar el patrón de cierre del YAML y agregar versioning antes
    # Patrón: loaded_in_notebook: true/false\n---
    pattern = r'(loaded_in_notebook:\s*(?:true|false)\n)'
    replacement = rf'\1{VERSIONING_YAML}\n'

    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
        print(f"✗ {filepath.name}: No se pudo agregar versioning (patrón no encontrado)")
        return False

    filepath.write_text(new_content)
    print(f"✓ {filepath.name}: Versioning agregado")
    return True


def main():
    """Procesa todas las fuentes FUENTE-*.md"""
    sources = sorted(SOURCES_DIR.glob("FUENTE-*.md"))

    print(f"Encontradas {len(sources)} fuentes")
    print(f"Directorio: {SOURCES_DIR}")
    print()

    modified = 0
    skipped = 0

    for source in sources:
        if add_versioning_to_source(source):
            modified += 1
        else:
            skipped += 1

    print()
    print(f"Resumen:")
    print(f"  Modificadas: {modified}")
    print(f"  Ya tenían versioning: {skipped}")
    print(f"  Total: {len(sources)}")


if __name__ == "__main__":
    main()
