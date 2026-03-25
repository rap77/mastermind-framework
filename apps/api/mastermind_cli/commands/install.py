import logging
import os
import shutil
import yaml
from pathlib import Path
from typing import Any, Optional

from mastermind_cli.brain_registry import BRAIN_REGISTRY

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
logger = logging.getLogger(__name__)


def get_framework_root() -> Optional[Path]:
    """Get the MasterMind Framework root directory."""
    try:
        from mastermind_cli import __file__ as module_file

        module_path = Path(module_file).resolve()
        # Go up from mastermind_cli/ to framework root
        # Structure: tools/mastermind-cli/mastermind_cli/
        if "tools/mastermind-cli" in module_path.parts:
            idx = module_path.parts.index("tools")
            return Path(*module_path.parts[:idx])
        # If installed via pip/uv, find the package location
        if "site-packages" in module_path.parts:
            # Installed globally - need to find the actual framework
            # Try to detect via environment or use a known location
            mastermind_env = os.environ.get("MASTERMIND_FRAMEWORK_PATH")
            if mastermind_env:
                return Path(mastermind_env)
            # Try common locations
            for candidate in [
                Path.home() / "proy" / "mastermind",
                Path.home() / "projects" / "mastermind",
                Path.home() / "mastermind",
            ]:
                if (
                    candidate / "docs" / "design" / "00-PRD-MasterMind-Framework.md"
                ).exists():
                    return candidate
        return None
    except (ImportError, OSError, ValueError) as e:
        logger.warning("Could not determine framework root: %s", e)
        return None


def get_brain_registry() -> dict[str, Any]:
    """Get the brain registry with NotebookLM notebook identifiers.

    Returns:
        Dictionary mapping brain IDs to their configuration.
    """
    return {
        brain_id: {
            "name": brain["name"],
            "id": brain["notebook_id"],
            "expertise": brain["expertise"],
        }
        for brain_id, brain in BRAIN_REGISTRY.items()
    }


@click.group()
def install() -> None:
    """Install MasterMind Framework in the current project."""
    pass


@install.command()
@click.option(
    "--brains",
    default="all",
    help="Brains to activate (default: all). Example: #1,#4,#7",
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to custom config.yaml",
)
@click.option(
    "--framework-path",
    type=click.Path(exists=True),
    help="Explicit path to MasterMind Framework (auto-detected by default)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Reinstall even if already installed",
)
@click.option(
    "--local",
    "install_local",
    is_flag=True,
    default=False,
    help="Install into the current project's .claude/ only (default: installs globally into ~/.claude/)",
)
def init(
    brains: str,
    config: Optional[str],
    framework_path: Optional[str],
    force: bool,
    install_local: bool,
) -> None:
    """
    Install MasterMind Framework globally (default) or per-project (--local).

    Global install (default):
    - Skills (mm:brain-context, etc.) → ~/.claude/skills/mm/
    - Slash commands (/mm:ask-*) → ~/.claude/commands/mm/
    - Hooks → ~/.claude/hooks/mm/
    - Available in ALL projects automatically

    Local install (--local):
    - Same assets copied to ./.claude/ in the current project only

    In both cases, .mastermind/config.yaml is created in the current project.

    Example:
        mastermind install init                          # global (recommended)
        mastermind install init --local                  # current project only
        mastermind install init --brains #1,#4,#7
        mastermind install init --framework-path ~/projects/mastermind
    """
    project_path = Path.cwd()
    global_claude_dir = Path.home() / ".claude"

    # Target dir for Claude assets: global or local
    target_claude_dir = project_path / ".claude" if install_local else global_claude_dir

    # Detect or use provided framework path
    if framework_path:
        framework_root = Path(framework_path).resolve()
    else:
        root = get_framework_root()
        if root is None:
            framework_root = Path.cwd()
        else:
            framework_root = root

    if not framework_root or not framework_root.exists():
        console.print("[red]❌ Could not find MasterMind Framework directory[/red]")
        console.print("\n[yellow]Solutions:[/yellow]")
        console.print("  1. Set MASTERMIND_FRAMEWORK_PATH environment variable")
        console.print("  2. Use --framework-path option")
        console.print("  3. Clone framework to ~/proy/mastermind")
        console.print(
            "\n[dim]Framework should contain docs/design/00-PRD-MasterMind-Framework.md[/dim]"
        )
        raise click.Abort()

    # Check if already installed (project-level activation file)
    active_file = project_path / ".mastermind-active"
    if active_file.exists() and not force:
        console.print(
            "[yellow]⚠ MasterMind is already installed in this project[/yellow]"
        )
        console.print("   Use --force to reinstall")
        console.print("\n   Run: [cyan]mastermind install status[/cyan]")
        raise click.Abort()

    # Parse brains selection
    registry = get_brain_registry()
    brain_ids = None if brains == "all" else [b.strip() for b in brains.split(",")]
    active_brains = brain_ids if brain_ids else list(registry.keys())

    if brain_ids:
        invalid = [b for b in brain_ids if b not in registry]
        if invalid:
            console.print(f"[red]❌ Invalid brain IDs: {', '.join(invalid)}[/red]")
            console.print(
                f"\n[yellow]Valid brains:[/yellow] {', '.join(registry.keys())}"
            )
            raise click.Abort()

    install_mode = "local (project only)" if install_local else "global (~/.claude/)"

    # Installation progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"Installing MasterMind Framework [{install_mode}]...", total=None
        )

        # 1. Create .mastermind directory (always in current project)
        progress.update(task, description="Creating .mastermind directory...")
        mastermind_dir = project_path / ".mastermind"
        mastermind_dir.mkdir(exist_ok=True)

        # 2. Create config.yaml (always in current project)
        progress.update(task, description="Creating project config...")
        config_file = mastermind_dir / "config.yaml"

        if config and Path(config).exists():
            shutil.copy(Path(config), config_file)
        else:
            active_brains = brain_ids if brain_ids else list(registry.keys())
            config_data = {
                "project": {
                    "name": project_path.name,
                    "path": str(project_path),
                },
                "framework": {
                    "version": "1.0.0",
                    "path": str(framework_root),
                    "install_mode": "local" if install_local else "global",
                },
                "brains": {
                    brain_id.lstrip("#"): {
                        "id": brain_id,
                        "name": registry[brain_id]["name"],
                        "notebook_id": registry[brain_id]["id"],
                        "expertise": registry[brain_id]["expertise"],
                        "active": True,
                    }
                    for brain_id in active_brains
                },
            }
            config_content = (
                "# MasterMind Framework - Project Configuration\n"
                "# Generated by mastermind install init\n\n"
                + yaml.dump(
                    config_data,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
            )
            config_content += """# Usage Notes
# - Brains are queried via NotebookLM MCP
# - Use /mm: commands in Claude Code (e.g., /mm:ask-product, /mm:brain-context)
# - All commands use mm namespace to avoid conflicts
# - Skills (mm:brain-context) available in all projects if globally installed
"""
            config_file.write_text(config_content)

        # 3. Install Claude assets (global or local target)
        progress.update(
            task,
            description=f"Installing Claude assets into {target_claude_dir}...",
        )
        target_hooks = target_claude_dir / "hooks" / "mm"
        target_commands = target_claude_dir / "commands" / "mm"
        target_skills = target_claude_dir / "skills" / "mm"
        target_agents = target_claude_dir / "agents" / "mm"

        target_hooks.mkdir(parents=True, exist_ok=True)
        target_commands.mkdir(parents=True, exist_ok=True)
        target_skills.mkdir(parents=True, exist_ok=True)
        target_agents.mkdir(parents=True, exist_ok=True)

        framework_claude = framework_root / ".claude"
        framework_hooks = framework_claude / "hooks" / "mm"
        framework_commands = framework_claude / "commands" / "mm"
        framework_skills_mm = framework_claude / "skills" / "mm"
        framework_agents = framework_claude / "agents" / "mm"

        def _sync(src: Path, dest: Path, recursive: bool = False) -> None:
            """Copy or symlink src to dest. Replaces if exists."""
            if dest.exists() or dest.is_symlink():
                if dest.is_symlink() or dest.is_file():
                    dest.unlink()
                else:
                    shutil.rmtree(dest)
            if recursive:
                try:
                    dest.symlink_to(src)
                except (OSError, NotImplementedError):
                    shutil.copytree(src, dest)
            else:
                try:
                    dest.symlink_to(src)
                except (OSError, NotImplementedError):
                    shutil.copy2(src, dest)

        # Slash commands (flat .md files)
        if framework_commands.exists():
            for cmd_file in framework_commands.glob("*.md"):
                _sync(cmd_file, target_commands / cmd_file.name)

        # Hooks (flat files)
        if framework_hooks.exists():
            for hook_file in framework_hooks.glob("*"):
                if not hook_file.name.startswith("."):
                    _sync(hook_file, target_hooks / hook_file.name)

        # Skills 2.0 (directory-based — symlink entire skill dir)
        if framework_skills_mm.exists():
            for skill_dir in framework_skills_mm.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                    _sync(skill_dir, target_skills / skill_dir.name, recursive=True)

        # Agents (directory-based — symlink entire agent dir or file)
        if framework_agents.exists():
            for agent_item in framework_agents.iterdir():
                if not agent_item.name.startswith("."):
                    recursive = agent_item.is_dir()
                    _sync(
                        agent_item,
                        target_agents / agent_item.name,
                        recursive=recursive,
                    )

        # 4. Create activation file (always in current project)
        progress.update(task, description="Creating activation file...")
        active_content = (
            "# MasterMind Framework Activation\n"
            "# This file marks this project as MasterMind-enabled\n\n"
            f"framework_path={framework_root}\n"
            f"version=1.0.0\n"
            f"brains={','.join(active_brains) if brain_ids else 'all'}\n"
            f"install_mode={'local' if install_local else 'global'}\n"
            "installed_by=mastermind install init\n"
        )
        active_file.write_text(active_content)

        # 5. Update README (project-level only)
        progress.update(task, description="Updating documentation...")
        readme = project_path / "README.md"
        if readme.exists():
            content = readme.read_text()
            if "MasterMind Framework" not in content:
                appendix = """

---

## 🧠 MasterMind Framework

This project uses [MasterMind Framework](https://github.com/rap77/mastermind-framework) for AI-powered expert consultation.

### Available Slash Commands

All commands use the `/mm:` namespace:

**Consult Brains:**
- `/mm:ask-product` - Product Strategy (what & why)
- `/mm:ask-ux` - UX Research (user experience)
- `/mm:ask-design` - UI Design (visual design)
- `/mm:ask-frontend` - Frontend Architecture
- `/mm:ask-backend` - Backend Architecture
- `/mm:ask-qa` - QA/DevOps (quality & operations)
- `/mm:ask-growth` - Growth/Data (evaluation & metrics)
- `/mm:ask-all` - All 7 brains as a team

**GSD Workflow Integration:**
- `mm:brain-context 1` - Before /gsd:new-milestone (ROADMAP context)
- `mm:brain-context 2` - Before /gsd:plan-phase (phase context)
- `mm:brain-context 3` - After PLAN.md, Brain-07 validation
- `mm:brain-context feed` - Post-phase BRAIN-FEED update

**Project Management:**
- `/mm:project-health-check` - Complete 7-brain project analysis
- `/mm:lite-prd-generator` - Generate PRD from rough idea

Run `mastermind install status` for more information.
"""
                readme.write_text(content + appendix)

        progress.update(task, description="✓ Installation complete!")

    # Success message
    scope_line = (
        f"[cyan]Scope:[/cyan] Global — available in ALL projects\n"
        f"[dim]Assets installed to: {target_claude_dir}[/dim]"
        if not install_local
        else f"[cyan]Scope:[/cyan] Local — this project only\n"
        f"[dim]Assets installed to: {target_claude_dir}[/dim]"
    )
    console.print(
        Panel.fit(
            f"[green bold]✓ MasterMind Framework installed successfully![/green bold]\n\n"
            f"[cyan]Project:[/cyan] {project_path.name}\n"
            f"[cyan]Framework:[/cyan] {framework_root}\n"
            f"[cyan]Active brains:[/cyan] {len(active_brains) if brain_ids else 7}\n"
            f"{scope_line}\n\n"
            f"[yellow]Next steps:[/yellow]\n"
            f"  1. Restart Claude Code (or open any project)\n"
            f"  2. Use [cyan]/mm:ask-product[/cyan] to consult the Product brain\n"
            f"  3. Use [cyan]mm:brain-context 2[/cyan] before /gsd:plan-phase\n"
            f"  4. Run [cyan]mastermind install status[/cyan] to verify\n\n"
            f"[dim]Config: .mastermind/config.yaml[/dim]\n"
            f"[dim]Skills: ~/.claude/skills/mm/ (brain-context, brain-persistence)[/dim]\n"
            f"[dim]Commands: ~/.claude/commands/mm/ (/mm:ask-*, /mm:project-health-check)[/dim]",
            title="Installation Complete",
            border_style="green",
        )
    )


@install.command()
def status() -> None:
    """Show MasterMind installation status in the current project."""
    project_path = Path.cwd()
    active_file = project_path / ".mastermind-active"
    config_file = project_path / ".mastermind" / "config.yaml"

    if not active_file.exists():
        console.print("[red]❌ MasterMind is not installed in this project[/red]")
        console.print("\n[yellow]To install:[/yellow]")
        console.print("  [cyan]mastermind install init[/cyan]")
        raise click.Abort()

    # Read activation file
    active_data: dict[str, str] = {}
    with open(active_file) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                active_data[key] = value

    # Display status
    console.print(
        Panel.fit(
            f"[green bold]✓ MasterMind Framework Active[/green bold]\n\n"
            f"[cyan]Version:[/cyan] {active_data.get('version', 'unknown')}\n"
            f"[cyan]Framework Path:[/cyan] {active_data.get('framework_path', 'unknown')}\n"
            f"[cyan]Active Brains:[/cyan] {active_data.get('brains', 'all')}\n"
            f"[cyan]Install Method:[/cyan] {active_data.get('install_method', 'standard')}\n",
            title="MasterMind Status",
            border_style="green",
        )
    )

    # Show brain status if config exists
    if config_file.exists():
        console.print("\n[bold]Active Brains:[/bold]\n")

        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)

            if config and "brains" in config:
                for brain_id, brain_config in config["brains"].items():
                    if brain_config.get("active"):
                        console.print(
                            f"  [cyan]{brain_id}[/cyan] {brain_config.get('name', 'Unknown')}"
                            f" - [dim]{brain_config.get('expertise', '')}[/dim]"
                        )
        except ImportError:
            console.print("[dim](Install pyyaml to see brain details)[/dim]")

    # Show integration files
    console.print("\n[bold]Integration Files:[/bold]\n")
    console.print("  [cyan].mastermind-active[/cyan] - Activation file")
    console.print("  [cyan].mastermind/config.yaml[/cyan] - Project configuration")
    console.print(
        "  [cyan].claude/commands/mm/[/cyan] - Available commands (mm namespace)"
    )

    # Show available slash commands
    console.print("\n[bold]Available Slash Commands:[/bold]\n")
    console.print("  [cyan]/mm:ask-product[/cyan] - Consult Product Strategy brain")
    console.print("  [cyan]/mm:ask-ux[/cyan] - Consult UX Research brain")
    console.print("  [cyan]/mm:project-audit[/cyan] - Full 7-brain project analysis")
    console.print("  [cyan]/mm:lite-prd-generator[/cyan] - Generate PRD from idea")
    console.print("  [cyan]...and 15 more commands[/cyan]")
    console.print("\n[dim]Run: ls .claude/commands/mm/ to see all commands[/dim]")

    # Show available CLI commands
    console.print("\n[bold]Available CLI Commands:[/bold]\n")
    console.print("  [cyan]mastermind install status[/cyan] - Show this status")
    console.print("  [cyan]mastermind install uninstall[/cyan] - Remove from project")
    console.print("  [cyan]mastermind brain status[/cyan] - Check brain status")


@install.command()
@click.option(
    "--keep-config",
    is_flag=True,
    help="Keep .mastermind/ directory (removes only activation)",
)
@click.option(
    "--remove-readme",
    is_flag=True,
    help="Also remove MasterMind section from README.md",
)
@click.confirmation_option(
    prompt="Are you sure you want to uninstall MasterMind from this project?"
)
def uninstall(keep_config: bool, remove_readme: bool) -> None:
    """Remove MasterMind Framework from the current project."""
    project_path = Path.cwd()
    active_file = project_path / ".mastermind-active"
    mastermind_dir = project_path / ".mastermind"

    if not active_file.exists():
        console.print("[yellow]⚠ MasterMind is not installed in this project[/yellow]")
        raise click.Abort()

    console.print("\n[yellow]Uninstalling MasterMind Framework...[/yellow]\n")

    # Remove activation file
    if active_file.exists():
        active_file.unlink()
        console.print("[green]✓ Removed .mastermind-active[/green]")

    # Remove mm namespace folders
    claude_dir = project_path / ".claude"
    removed_count = 0

    for ns_folder in ["commands/mm", "hooks/mm", "agents/mm"]:
        ns_path = claude_dir / ns_folder
        if ns_path.exists():
            try:
                shutil.rmtree(ns_path)
                console.print(f"[green]✓ Removed .claude/{ns_folder}/[/green]")
                removed_count += 1
            except OSError as e:
                console.print(
                    f"[yellow]⚠ Could not remove .claude/{ns_folder}/: {e}[/yellow]"
                )

    # Clean up empty parent directories
    for parent_dir in ["commands", "hooks", "agents"]:
        parent_path = claude_dir / parent_dir
        if parent_path.exists() and not list(parent_path.iterdir()):
            try:
                parent_path.rmdir()
                console.print(f"[dim]✓ Removed empty .claude/{parent_dir}/[/dim]")
            except OSError:
                pass

    # Optionally remove config directory
    if not keep_config and mastermind_dir.exists():
        shutil.rmtree(mastermind_dir)
        console.print("[green]✓ Removed .mastermind/ directory[/green]")
    elif keep_config:
        console.print("[dim]Kept .mastermind/ directory (--keep-config)[/dim]")

    # Optionally remove README section
    if remove_readme:
        readme = project_path / "README.md"
        if readme.exists():
            try:
                content = readme.read_text()
                # Remove MasterMind section (from ## 🧠 to next ## or end)
                import re

                pattern = r"\n## 🧠 MasterMind Framework.*(?=\n## |\Z)"
                new_content = re.sub(pattern, "", content, flags=re.DOTALL)
                if new_content != content:
                    readme.write_text(new_content)
                    console.print(
                        "[green]✓ Removed MasterMind section from README.md[/green]"
                    )
            except Exception as e:
                console.print(f"[yellow]⚠ Could not update README.md: {e}[/yellow]")

    console.print(
        Panel.fit(
            f"[green bold]✓ MasterMind Framework uninstalled[/green bold]\n\n"
            f"[cyan]Removed:[/cyan] {removed_count} namespace folder(s)\n"
            f"[cyan]Config kept:[/cyan] {keep_config}\n\n"
            "[yellow]Note: If you want to remove the MasterMind section from README.md, run:[/yellow]\n"
            "[dim]  mastermind install uninstall --remove-readme[/dim]",
            title="Uninstallation Complete",
            border_style="yellow",
        )
    )


@install.command()
@click.option(
    "--uvx",
    is_flag=True,
    help="Use uvx for running (experimental)",
)
def run(uvx: bool) -> None:
    """
    Run MasterMind CLI with uvx (experimental).

    This allows running the framework without installation:

        mastermind install run --uvx

    Equivalent to:
        uvx --from mastermind-framework mastermind
    """
    if uvx:
        console.print("[yellow]Launching MasterMind with uvx...[/yellow]")
        console.print("\n[cyan]This is experimental. For production use:[/cyan]")
        console.print("  [dim]uv add mastermind-framework[/dim]")
        console.print("\n[green]✓ uvx mode ready[/green]")
    else:
        console.print("[yellow]MasterMind is already running![/yellow]")
        console.print("\n[cyan]Available commands:[/cyan]")
        console.print("  mastermind install init")
        console.print("  mastermind install status")
        console.print("  mastermind brain status")
        console.print("  mastermind framework status")
