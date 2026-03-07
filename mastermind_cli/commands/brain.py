"""Brain commands for MasterMind CLI."""

from pathlib import Path
from typing import Dict, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from ..utils.yaml import read_yaml_frontmatter

console = Console()


def get_project_root() -> Path:
    """Get the MasterMind project root directory."""
    current = Path.cwd()
    markers = ["CLAUDE.md", "docs/design/00-PRD-MasterMind-Framework.md"]
    for parent in [current] + list(current.parents):
        for marker in markers:
            if (parent / marker).exists():
                return parent
    return current


@click.group()
def brain():
    """Manage brain configuration."""
    pass


@brain.command("status")
@click.argument("brain_id")
def brain_status(brain_id: str):
    """Show complete brain status."""
    project_root = get_project_root()
    brain_path = project_root / "docs" / "software-development" / f"{brain_id}-brain"

    if not brain_path.exists():
        console.print(f"[red]Error: Brain not found: {brain_id}[/red]")
        console.print(f"\n[yellow]Available brains:[/yellow]")
        for d in (project_root / "docs" / "software-development").iterdir():
            if d.is_dir() and d.name.endswith("-brain"):
                console.print(f"  • {d.name.replace('-brain', '')}")
        raise click.Abort()

    sources_dir = brain_path / "sources"
    sources = list(sources_dir.glob("FUENTE-*.md")) if sources_dir.exists() else []

    # Collect metadata from sources
    all_skills = set()
    quality_stats = {"complete": 0, "partial": 0, "pending": 0}
    loaded_count = 0
    experts = set()

    for source_file in sources:
        try:
            metadata, _ = read_yaml_frontmatter(str(source_file))
            if metadata:
                skills = metadata.get("skills_covered", [])
                all_skills.update(skills)

                quality = metadata.get("distillation_quality", "pending")
                if quality in quality_stats:
                    quality_stats[quality] += 1

                if metadata.get("loaded_in_notebook"):
                    loaded_count += 1

                expert_id = metadata.get("expert_id")
                if expert_id:
                    experts.add(expert_id)
        except Exception:
            pass

    # Display status
    console.print(Panel.fit(
        f"[bold]{brain_id}[/bold]\n\n"
        f"Sources: {len(sources)}\n"
        f"Experts: {len(experts)}\n"
        f"Skills Covered: {len(all_skills)}\n"
        f"Loaded in Notebook: {loaded_count}/{len(sources)}",
        title=f"Brain Status: {brain_id}",
        border_style="blue"
    ))

    # Sources table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Source ID")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Quality")

    for source_file in sources:
        try:
            metadata, _ = read_yaml_frontmatter(str(source_file))
            if metadata:
                quality = metadata.get("distillation_quality", "pending")
                quality_color = "green" if quality == "complete" else "yellow"

                table.add_row(
                    metadata.get("source_id", "—"),
                    metadata.get("title", "—")[:30],
                    metadata.get("author", "—"),
                    f"[{quality_color}]{quality}[/{quality_color}]",
                )
        except Exception:
            pass

    console.print("\n")
    console.print(table)


@brain.command("validate")
@click.argument("brain_id")
def brain_validate(brain_id: str):
    """Validate brain for gaps and completeness."""
    project_root = get_project_root()
    brain_path = project_root / "docs" / "software-development" / f"{brain_id}-brain"

    if not brain_path.exists():
        console.print(f"[red]Error: Brain not found: {brain_id}[/red]")
        raise click.Abort()

    from ..utils.validation import validate_brain_sources

    results = validate_brain_sources(str(brain_path))

    if not results:
        console.print(f"[yellow]No sources found to validate[/yellow]")
        return

    # Count issues
    total_errors = sum(len(r.errors) for r in results.values())
    total_warnings = sum(len(r.warnings) for r in results.values())
    valid_count = sum(1 for r in results.values() if r.is_valid)

    console.print(Panel.fit(
        f"Total Sources: {len(results)}\n"
        f"Valid: [green]{valid_count}[/green]\n"
        f"Errors: [red]{total_errors}[/red]\n"
        f"Warnings: [yellow]{total_warnings}[/yellow]",
        title=f"Validation: {brain_id}",
        border_style="green" if total_errors == 0 else "red"
    ))

    if total_errors > 0:
        console.print("\n[red]Sources with errors:[/red]")
        for filename, result in results.items():
            if result.errors:
                console.print(f"  • {filename}: {len(result.errors)} errors")


@brain.command("package")
@click.argument("brain_id")
@click.option("--output", default="dist/packages", help="Output directory")
def brain_package(brain_id: str, output: str):
    """Package brain for distribution."""
    project_root = get_project_root()
    brain_path = project_root / "docs" / "software-development" / f"{brain_id}-brain"
    output_dir = project_root / output

    if not brain_path.exists():
        console.print(f"[red]Error: Brain not found: {brain_id}[/red]")
        raise click.Abort()

    output_dir.mkdir(parents=True, exist_ok=True)

    # For now, just count files (full packaging in future PRP)
    sources_dir = brain_path / "sources"
    sources = list(sources_dir.glob("FUENTE-*.md")) if sources_dir.exists() else []

    console.print(Panel.fit(
        f"[bold]{brain_id}[/bold]\n\n"
        f"Sources: {len(sources)}\n"
        f"Output: {output_dir}\n\n"
        f"[dim](Full packaging coming in future PRP)[/dim]",
        title="Brain Package",
        border_style="blue"
    ))


@brain.command("compile-radar")
@click.argument("brain_id", default="07")
def brain_compile_radar(brain_id: str):
    """Compile evaluation criteria and anti-patterns from all brains into Brain #7 sources.

    This command generates FUENTE-709 (checklist) and FUENTE-710 (anti-patterns)
    for the Critical Evaluator brain by consolidating evaluation-criteria.md
    and anti-patrones.md files from brains 1-6.
    """
    if brain_id != "07":
        console.print("[yellow]compile-radar only applies to brain 07 (Critical Evaluator)[/yellow]")
        console.print("\n[dim]The evaluator needs consolidated criteria from all other brains.[/dim]")
        raise click.Abort()

    project_root = get_project_root()
    software_dev = project_root / "docs" / "software-development"
    output_dir = software_dev / "07-growth-data-brain" / "sources"
    output_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================================
    # STEP 1: Compile evaluation criteria → FUENTE-709
    # ============================================================================
    console.print("[cyan]Step 1/2: Compiling evaluation criteria...[/cyan]")

    criteria_sections = []
    brains_found = []

    # Brains to scan (01-06)
    brain_patterns = [
        "01-product-strategy-brain",
        "02-*-brain",  # Will match when created
        "03-*-brain",
        "04-*-brain",
        "05-*-brain",
        "06-*-brain",
    ]

    for pattern in brain_patterns:
        matching_dirs = list(software_dev.glob(pattern))
        for brain_path in matching_dirs:
            if not brain_path.is_dir():
                continue

            # Extract brain ID from directory name
            brain_name = brain_path.name
            brain_num = brain_name.split("-")[0]
            brains_found.append(brain_num)

            # Look for evaluation-criteria.md
            criteria_file = brain_path / "evaluation-criteria.md"
            if criteria_file.exists():
                content = criteria_file.read_text(encoding="utf-8")
                criteria_sections.append(f"## From {brain_num}\n\n{content}\n")
                console.print(f"  [green]✓[/green] Found in {brain_name}")
            else:
                console.print(f"  [dim]⊘[/dim] No evaluation-criteria.md in {brain_name}")

    # Generate FUENTE-709
    fuente_709 = """---
source_id: "FUENTE-709"
brain: "brain-software-07-growth-data"
niche: "software-development"
title: "Checklist de Evaluación por Cerebro"
author: "Generated (MasterMind CLI)"
expert_id: "GEN-001"
type: "generated"
language: "es"
year: 2026
distillation_date: "2026-02-23"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-02-23"
changelog:
  - version: "1.0.0"
    date: "2026-02-23"
    changes:
      - "Generated from brains 1-6 evaluation criteria"
status: "active"
---

# FUENTE-709: Checklist de Evaluación por Cerebro

**Generado por:** `mastermind brain compile-radar --brain 07`
**Fecha:** 2026-02-23

Esta fuente consolida los criterios de evaluación de cada cerebro (1-6) para que
el Cerebro #7 (Evaluador Crítico) pueda verificar que cada cerebro aplicó
correctamente sus frameworks y principios.

"""

    if criteria_sections:
        fuente_709 += "\n".join(criteria_sections)
    else:
        fuente_709 += "\n\n*No se encontraron criterios de evaluación en los cerebros 1-6.*\n"
        fuente_709 += "\n**Nota:** A medida que se implementen los cerebros 2-6, agreguen\n"
        fuente_709 += "archivos `evaluation-criteria.md` en sus directorios correspondientes.\n"

    (output_dir / "FUENTE-709-checklist-evaluacion-por-cerebro.md").write_text(
        fuente_709, encoding="utf-8"
    )
    console.print("[green]✓ FUENTE-709 created[/green]")

    # ============================================================================
    # STEP 2: Compile anti-patterns → FUENTE-710
    # ============================================================================
    console.print("\n[cyan]Step 2/2: Compiling anti-patterns...[/cyan]")

    anti_pattern_sections = []

    for pattern in brain_patterns:
        matching_dirs = list(software_dev.glob(pattern))
        for brain_path in matching_dirs:
            if not brain_path.is_dir():
                continue

            brain_name = brain_path.name

            # Look for anti-patrones.md
            anti_file = brain_path / "anti-patrones.md"
            if anti_file.exists():
                content = anti_file.read_text(encoding="utf-8")
                anti_pattern_sections.append(f"## From {brain_name}\n\n{content}\n")
                console.print(f"  [green]✓[/green] Found in {brain_name}")
            else:
                console.print(f"  [dim]⊘[/dim] No anti-patrones.md in {brain_name}")

    # Generate FUENTE-710
    fuente_710 = """---
source_id: "FUENTE-710"
brain: "brain-software-07-growth-data"
niche: "software-development"
title: "Anti-patrones Consolidados"
author: "Generated (MasterMind CLI)"
expert_id: "GEN-001"
type: "generated"
language: "es"
year: 2026
distillation_date: "2026-02-23"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-02-23"
changelog:
  - version: "1.0.0"
    date: "2026-02-23"
    changes:
      - "Generated from brains 1-6 anti-patterns"
status: "active"
---

# FUENTE-710: Anti-patrones Consolidados

**Generado por:** `mastermind brain compile-radar --brain 07`
**Fecha:** 2026-02-23

Esta fuente consolida los anti-patrones identificados en cada cerebro (1-6) para que
el Cerebro #7 (Evaluador Crítico) pueda detectar errores comunes y patrones de
falla en los outputs.

"""

    if anti_pattern_sections:
        fuente_710 += "\n".join(anti_pattern_sections)
    else:
        fuente_710 += "\n\n*No se encontraron anti-patrones en los cerebros 1-6.*\n"
        fuente_710 += "\n**Nota:** A medida que se implementen los cerebros 2-6, agreguen\n"
        fuente_710 += "archivos `anti-patrones.md` en sus directorios correspondientes.\n"

    (output_dir / "FUENTE-710-antipatrones-consolidados.md").write_text(
        fuente_710, encoding="utf-8"
    )
    console.print("[green]✓ FUENTE-710 created[/green]")

    # ============================================================================
    # SUMMARY
    # ============================================================================
    console.print("\n")
    console.print(Panel.fit(
        f"[bold green]✓ Radar compiled for brain 07[/bold green]\n\n"
        f"Brains scanned: {len(set(brains_found))}\n"
        f"Fuentes generated: 2\n"
        f"Output directory: {output_dir.relative_to(project_root)}\n\n"
        f"[dim]Run 'mm source status --brain 07' to verify.[/dim]",
        title="Compile-Radar Complete",
        border_style="green"
    ))
