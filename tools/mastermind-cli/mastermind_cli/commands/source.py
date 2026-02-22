"""Source commands for MasterMind CLI."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from ..utils.yaml import read_yaml_frontmatter, write_yaml_frontmatter, update_yaml_metadata
from ..utils.git import git_commit, is_repo_dirty
from ..utils.validation import validate_source_file, validate_brain_sources, find_sources_by_id

console = Console()


def get_project_root() -> Path:
    """Get the MasterMind project root directory."""
    current = Path.cwd()
    # Look for markers of project root
    markers = ["CLAUDE.md", "docs/design/00-PRD-MasterMind-Framework.md"]
    for parent in [current] + list(current.parents):
        for marker in markers:
            if (parent / marker).exists():
                return parent
    return current


def get_next_source_number(sources_dir: Path) -> int:
    """Get the next available source number."""
    existing_numbers = []
    for file in sources_dir.glob("FUENTE-*.md"):
        match = re.search(r"FUENTE-(\d+)", file.name)
        if match:
            existing_numbers.append(int(match.group(1)))
    return max(existing_numbers) + 1 if existing_numbers else 1


@click.group()
def source():
    """Manage source files for brains."""
    pass


@source.command("new")
@click.argument("source_id")
@click.option("--brain", required=True, help='Brain ID (e.g., "01-product-strategy")')
@click.option("--title", required=True, help="Source title")
@click.option("--author", required=True, help="Author name")
@click.option("--type", type=click.Choice(["book", "video", "article", "course", "documentation"]), default="book")
@click.option("--year", type=int, required=True)
def source_new(source_id: str, brain: str, title: str, author: str, type: str, year: int):
    """Create new source from template."""
    project_root = get_project_root()
    sources_dir = project_root / "docs" / "software-development" / f"{brain}-brain" / "sources"

    if not sources_dir.exists():
        console.print(f"[red]Error: Brain directory not found: {sources_dir}[/red]")
        console.print(f"[yellow]Available brains:[/yellow]")
        for d in (project_root / "docs" / "software-development").iterdir():
            if d.is_dir() and d.name.endswith("-brain"):
                console.print(f"  • {d.name.replace('-brain', '')}")
        raise click.Abort()

    # Check if source_id already exists
    existing_file = sources_dir / f"{source_id}.md"
    if existing_file.exists():
        console.print(f"[red]Error: Source {source_id} already exists at {existing_file}[/red]")
        raise click.Abort()

    # Create source from template
    template = f"""---
source_id: "{source_id}"
brain: "brain-software-{brain}"
niche: "software-development"
title: "{title}"
author: "{author}"
expert_id: "EXP-XXX"
type: "{type}"
language: "es"
year: {year}
skills_covered: []
distillation_date: "{datetime.now().strftime('%Y-%m-%d')}"
distillation_quality: "pending"
loaded_in_notebook: false
---

# {source_id}: {title}

## Datos de la Fuente

| Campo | Valor |
|-------|-------|
| **Autor** | {author} |
| **Tipo** | {type.capitalize()} |
| **Título** | {title} |
| **Año** | {year} |

## Experto Asociado

**{author}** — Especialidad pendiente

## Habilidades que Cubre

| ID | Habilidad | Nivel de Cobertura |
|----|-----------|-------------------|

## Resumen Ejecutivo

TODO: Agregar resumen ejecutivo de 2-3 oraciones.

---

## Conocimiento Destilado

### 1. Principios Fundamentales

> **P1: {{Nombre del principio}}**
> {{Descripción clara y accionable del principio}}
> *Contexto de aplicación: {{cuándo aplica}}*

### 2. Frameworks y Metodologías

#### FM1: {{Nombre del Framework}}

**Propósito:** {{Qué problema resuelve}}
**Cuándo usar:** {{Situación específica}}

### 3. Modelos Mentales

| Modelo | Descripción | Aplicación Práctica |
|--------|-------------|-------------------|

### 4. Criterios de Decisión

| Cuando... | Prioriza... | Sobre... | Porque... |
|-----------|-------------|----------|-----------|

### 5. Anti-patrones (Qué NO Hacer)

| Anti-patrón | Por qué es malo | Qué hacer en su lugar |
|-------------|----------------|----------------------|

### 6. Casos y Ejemplos Reales

#### Caso 1: {{Nombre/Empresa}}

- **Situación:** {{Contexto}}
- **Decisión:** {{Qué hicieron}}
- **Resultado:** {{Qué pasó}}
- **Lección:** {{Qué aprender}}

---

## Notas de Destilación

- **Calidad de la fuente:** {{Alta / Media}}
- **Capítulos/secciones más valiosos:** {{Lista}}
- **Lo que NO se extrajo y por qué:** {{Secciones ignoradas}}
"""

    existing_file.write_text(template, encoding="utf-8")

    console.print(Panel.fit(
        f"[green]✓[/green] Source created: [bold]{source_id}[/bold]\n\n"
        f"Location: {existing_file}\n\n"
        f"[dim]Next steps:[/dim]\n"
        f"  1. Edit the file to add distilled knowledge\n"
        f"  2. Run: [cyan]mastermind source validate --brain {brain}[/cyan]",
        title="Source Created",
        border_style="green"
    ))


@source.command("update")
@click.argument("source_id")
@click.option("--change", required=True, help="Description of changes")
def source_update(source_id: str, change: str):
    """Update source with version bump and git commit."""
    project_root = get_project_root()
    search_paths = [
        project_root / "docs" / "software-development",
    ]

    matches = find_sources_by_id(source_id, [str(p) for p in search_paths])

    if not matches:
        console.print(f"[red]Error: Source {source_id} not found[/red]")
        console.print(f"[yellow]Search paths:[/yellow] {search_paths}")
        raise click.Abort()

    if len(matches) > 1:
        console.print(f"[yellow]Warning: Found multiple sources:[/yellow]")
        for m in matches:
            console.print(f"  • {m}")
        source_file = matches[0]
    else:
        source_file = matches[0]

    # Read current metadata
    metadata, content = read_yaml_frontmatter(source_file)

    if metadata is None:
        console.print(f"[red]Error: No YAML front matter found in {source_file}[/red]")
        raise click.Abort()

    # Get current version or default to 1.0.0
    current_version = metadata.get("version", "1.0.0")

    # Increment patch version
    from semver import VersionInfo
    version = VersionInfo.parse(current_version)
    new_version = str(version.bump_patch())

    # Update metadata
    updates = {
        "version": new_version,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
    }

    # Add changelog entry
    changelog = metadata.get("changelog", [])
    changelog.append({
        "version": new_version,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "changes": [change],
    })
    updates["changelog"] = changelog

    # Write updated metadata
    update_yaml_metadata(source_file, updates)

    # Git commit
    commit_msg = f"update(source): {source_id}: {change}"
    try:
        commit_sha = git_commit(source_file, commit_msg)
        console.print(Panel.fit(
            f"[green]✓[/green] Source updated: [bold]{source_id}[/bold]\n\n"
            f"Version: {current_version} → [green]{new_version}[/green]\n"
            f"Commit: {commit_sha[:7]}\n"
            f"Change: {change}",
            title="Source Updated",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[yellow]Warning: Could not create git commit: {e}[/yellow]")
        console.print(f"[green]✓[/green] Source updated: [bold]{source_id}[/bold] (v{new_version})")


@source.command("validate")
@click.option("--brain", required=True, help='Brain ID (e.g., "01-product-strategy")')
def source_validate(brain: str):
    """Validate all sources in a brain."""
    project_root = get_project_root()
    brain_path = project_root / "docs" / "software-development" / f"{brain}-brain"

    if not brain_path.exists():
        console.print(f"[red]Error: Brain directory not found: {brain_path}[/red]")
        raise click.Abort()

    results = validate_brain_sources(str(brain_path))

    if not results:
        console.print(f"[yellow]No sources found in {brain_path}/sources/[/yellow]")
        return

    # Display results table
    table = Table(title=f"Validation Results: {brain}")
    table.add_column("Source", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Errors", style="red")
    table.add_column("Warnings", style="yellow")

    valid_count = 0
    for filename, result in results.items():
        status = "[green]✓ PASS[/green]" if result.is_valid else "[red]✗ FAIL[/red]"
        errors = ", ".join([e.message for e in result.errors]) or "—"
        warnings = ", ".join([w.message for w in result.warnings]) or "—"

        table.add_row(filename, status, errors, warnings)
        if result.is_valid:
            valid_count += 1

    console.print(table)
    console.print(f"\nSummary: {valid_count}/{len(results)} sources valid")


@source.command("list")
def source_list():
    """List all sources with metadata."""
    project_root = get_project_root()
    sources_dir = project_root / "docs" / "software-development"

    table = Table(title="All Sources")
    table.add_column("Source ID", style="cyan")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Type")
    table.add_column("Year")
    table.add_column("Brain")

    for source_file in sources_dir.rglob("sources/FUENTE-*.md"):
        try:
            metadata, _ = read_yaml_frontmatter(str(source_file))
            if metadata:
                table.add_row(
                    metadata.get("source_id", "—"),
                    metadata.get("title", "—")[:40] + "..." if len(metadata.get("title", "")) > 40 else metadata.get("title", "—"),
                    metadata.get("author", "—"),
                    metadata.get("type", "—"),
                    str(metadata.get("year", "—")),
                    source_file.parent.parent.name.replace("-brain", ""),
                )
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read {source_file}: {e}[/yellow]")

    console.print(table)


@source.command("status")
@click.option("--brain", required=True, help='Brain ID (e.g., "01-product-strategy")')
def source_status(brain: str):
    """Show status of sources in a brain."""
    project_root = get_project_root()
    sources_dir = project_root / "docs" / "software-development" / f"{brain}-brain" / "sources"

    if not sources_dir.exists():
        console.print(f"[red]Error: Sources directory not found: {sources_dir}[/red]")
        raise click.Abort()

    sources = list(sources_dir.glob("FUENTE-*.md"))

    console.print(Panel.fit(
        f"[bold]{brain}[/bold]\n\n"
        f"Total sources: {len(sources)}",
        title=f"Brain Status: {brain}",
        border_style="blue"
    ))

    table = Table()
    table.add_column("Source ID")
    table.add_column("Title")
    table.add_column("Quality")
    table.add_column("In Notebook")

    for source_file in sources:
        try:
            metadata, _ = read_yaml_frontmatter(str(source_file))
            if metadata:
                quality = metadata.get("distillation_quality", "pending")
                quality_color = "green" if quality == "complete" else "yellow" if quality == "partial" else "red"
                loaded = "✓" if metadata.get("loaded_in_notebook") else "✗"

                table.add_row(
                    metadata.get("source_id", "—"),
                    metadata.get("title", "—")[:30],
                    f"[{quality_color}]{quality}[/{quality_color}]",
                    loaded,
                )
        except Exception:
            pass

    console.print(table)


@source.command("export")
@click.option("--brain", required=True, help='Brain ID (e.g., "01-product-strategy")')
@click.option("--output", default="dist/notebooklm", help="Output directory")
def source_export(brain: str, output: str):
    """Export sources for NotebookLM (without YAML front matter)."""
    project_root = get_project_root()
    sources_dir = project_root / "docs" / "software-development" / f"{brain}-brain" / "sources"
    output_dir = project_root / output / brain

    if not sources_dir.exists():
        console.print(f"[red]Error: Sources directory not found: {sources_dir}[/red]")
        raise click.Abort()

    output_dir.mkdir(parents=True, exist_ok=True)

    sources = list(sources_dir.glob("FUENTE-*.md"))
    exported = 0

    for source_file in sources:
        try:
            _, content = read_yaml_frontmatter(str(source_file))
            # Export without YAML front matter
            output_file = output_dir / source_file.name
            output_file.write_text(content, encoding="utf-8")
            exported += 1
        except Exception as e:
            console.print(f"[yellow]Warning: Could not export {source_file}: {e}[/yellow]")

    console.print(Panel.fit(
        f"[green]✓[/green] Exported [bold]{exported}[/bold] sources\n\n"
        f"Output: {output_dir}",
        title="Export Complete",
        border_style="green"
    ))
