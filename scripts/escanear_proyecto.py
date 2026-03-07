#!/usr/bin/env python3
"""
MasterMind Framework - Project Scanner

Analiza un proyecto externo, genera un brief automáticamente,
y lo evalúa con los 7 cerebros.

Uso:
    python escanear_proyecto.py /path/to/proyecto          # Escanea y evalúa
    python escanear_proyecto.py /path/to/proyecto --mcp   # Con NotebookLM real
    python escanear_proyecto.py . --depth 2               # Escanea este proyecto
"""
import glob
import json
import logging
import os
import re
import sys
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Add mastermind-cli to path
MASTERMIND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{MASTERMIND_ROOT}/tools/mastermind-cli")


class ProjectScanner:
    """Escanea un proyecto y extrae información para generar un brief."""

    # Archivos clave a buscar
    KEY_FILES = [
        # Documentación de producto
        "README.md", "CONTRIBUTING.md", "docs/README.md",
        "PRD.md", "PRODUCT.md", "SPEC.md", "REQUIREMENTS.md",
        "docs/PRD.md", "docs/SPEC.md", "docs/design/*.md",

        # Documentación técnica
        "ARCHITECTURE.md", "DESIGN.md", "TECHNICAL.md",
        "docs/ARCHITECTURE.md", "docs/DESIGN.md",
        "docs/API.md", "API.md",

        # Roadmap y planes
        "ROADMAP.md", "TIMELINE.md", "docs/ROADMAP.md",
        "CHANGELOG.md",

        # Configuración (da pistas sobre el stack)
        "package.json", "Cargo.toml", "pyproject.toml",
        "requirements.txt", "go.mod", "Gemfile",
    ]

    # Directorios clave a explorar
    KEY_DIRS = [
        "docs", "doc", "documentation",
        "spec", "specs", "design",
        "src", "app", "lib", "server",
        "frontend", "backend", "api",
        ".github", "tests", "__tests__"
    ]

    # Patrones a buscar en el código
    CODE_PATTERNS = {
        "frameworks": [
            ("react", "React"),
            ("vue", "Vue.js"),
            ("angular", "Angular"),
            ("next", "Next.js"),
            ("django", "Django"),
            ("flask", "Flask"),
            ("fastapi", "FastAPI"),
            ("express", "Express.js"),
            ("rails", "Ruby on Rails"),
            ("spring", "Spring Boot"),
        ],
        "databases": [
            ("postgresql", "PostgreSQL"),
            ("mysql", "MySQL"),
            ("mongodb", "MongoDB"),
            ("redis", "Redis"),
            ("sqlite", "SQLite"),
        ],
        "infrastructure": [
            ("docker", "Docker"),
            ("kubernetes", "Kubernetes"),
            ("aws", "AWS"),
            ("gcp", "Google Cloud"),
            ("azure", "Azure"),
            ("vercel", "Vercel"),
            ("heroku", "Heroku"),
        ]
    }

    def __init__(self, project_path: str, max_depth: int = 3) -> None:
        self.project_path = Path(project_path).resolve()
        self.max_depth = max_depth
        self.findings = {
            "name": "",
            "description": "",
            "tech_stack": [],
            "features": [],
            "users_mentioned": [],
            "metrics_mentioned": [],
            "docs_found": [],
            "key_files_content": {},
            "architecture_notes": [],
        }

    def scan(self) -> dict:
        """Ejecuta el escaneo completo del proyecto."""
        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {self.project_path}")

        logger.info(f"\n{'='*70}")
        logger.info(f"🔍 ESCANEANDO PROYECTO")
        logger.info(f"{'='*70}")
        logger.info(f"📁 Path: {self.project_path}")
        logger.info(f"📊 Max depth: {self.max_depth}")

        # 1. Extraer nombre del proyecto
        self._extract_project_name()

        # 2. Buscar archivos clave
        self._find_key_files()

        # 3. Leer contenido de archivos importantes
        self._read_key_files()

        # 4. Analizar estructura de código
        self._analyze_code_structure()

        # 5. Extraer del stack técnico
        self._extract_tech_stack()

        # 6. Generar resumen
        brief = self._generate_brief()

        return brief

    def _extract_project_name(self) -> None:
        """Extrae el nombre del proyecto."""
        # Intentar desde package.json, pyproject.toml, etc.
        config_files = [
            ("package.json", lambda c: c.get("name", "")),
            ("pyproject.toml", lambda c: c.get("project", {}).get("name", "")),
            ("Cargo.toml", lambda c: c.get("package", {}).get("name", "")),
        ]

        for filename, extractor in config_files:
            filepath = self.project_path / filename
            if filepath.exists():
                try:
                    if filename.endswith(".json"):
                        with open(filepath) as f:
                            self.findings["name"] = extractor(json.load(f))
                            break
                    elif filename.endswith(".toml"):
                        # Simple parsing for project name
                        with open(filepath) as f:
                            for line in f:
                                if 'name' in line.lower() and '=' in line:
                                    self.findings["name"] = line.split('=')[1].strip().strip('"')
                                    break
                except (json.JSONDecodeError, KeyError, OSError, ValueError):
                    pass

        # Fallback al nombre del directorio
        if not self.findings["name"]:
            self.findings["name"] = self.project_path.name

        logger.info(f"📦 Nombre: {self.findings['name']}")

    def _find_key_files(self) -> None:
        """Busca archivos de documentación clave."""


        logger.info(f"\n📄 Buscando documentación...")

        for pattern in self.KEY_FILES:
            matches = glob.glob(str(self.project_path / pattern), recursive=True)
            for match in matches[:5]:  # Limitar a 5 por patrón
                rel_path = os.path.relpath(match, self.project_path)
                if rel_path not in self.findings["docs_found"]:
                    self.findings["docs_found"].append(rel_path)

        logger.info(f"   Found {len(self.findings['docs_found'])} documentation files")

    def _read_key_files(self) -> None:
        """Lee el contenido de archivos importantes."""
        logger.info(f"\n📖 Leyendo archivos clave...")

        # Prioridad: README, PRD, SPEC, ARCHITECTURE
        priority_files = ["README.md", "PRD.md", "SPEC.md", "ARCHITECTURE.md",
                         "docs/README.md", "docs/PRD.md", "docs/SPEC.md"]

        for priority in priority_files:
            filepath = self.project_path / priority
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.findings["key_files_content"][priority] = content
                        logger.info(f"   ✓ {priority} ({len(content)} chars)")
                        if len(self.findings["key_files_content"]) >= 3:
                            break
                except (OSError, UnicodeDecodeError) as e:
                    logger.info(f"   ✗ {priority} ({e})")

    def _analyze_code_structure(self) -> None:
        """Analiza la estructura del código para inferir features."""


        logger.info(f"\n🔬 Analizando estructura de código...")

        # Buscar archivos de código principales
        code_patterns = {
            "frontend": ["src/**/*.tsx", "src/**/*.jsx", "app/**/*.tsx", "components/**/*.tsx"],
            "backend": ["src/**/*.py", "src/**/*.js", "app/**/*.py", "lib/**/*.rb"],
            "api": ["api/**/*.py", "api/**/*.js", "routes/**/*.py", "controllers/**/*.py"],
        }

        for category, patterns in code_patterns.items():
            files_found = 0
            for pattern in patterns:
                matches = glob.glob(str(self.project_path / pattern), recursive=True)
                files_found += len(matches[:10])  # Muestrear

            if files_found > 0:
                logger.info(f"   {category}: ~{files_found} files")

    def _extract_tech_stack(self) -> None:
        """Extrae el stack técnico de archivos de configuración."""


        logger.info(f"\n🛠️  Detecting tech stack...")

        stack = set()

        # Leer package.json
        if (self.project_path / "package.json").exists():
            try:
                with open(self.project_path / "package.json") as f:
                    deps = json.load(f).get("dependencies", {})
                    for name in deps.keys():
                        name_lower = name.lower()
                        for category, frameworks in self.CODE_PATTERNS.items():
                            for pattern, friendly in frameworks:
                                if pattern in name_lower:
                                    stack.add(friendly)
            except (json.JSONDecodeError, KeyError, OSError):
                pass

        # Leer requirements.txt
        if (self.project_path / "requirements.txt").exists():
            try:
                with open(self.project_path / "requirements.txt") as f:
                    for line in f:
                        line_lower = line.lower()
                        for pattern, friendly in [("django", "Django"), ("flask", "Flask"),
                                                  ("fastapi", "FastAPI"), ("celery", "Celery")]:
                            if pattern in line_lower:
                                stack.add(friendly)
            except OSError:
                pass

        self.findings["tech_stack"] = sorted(list(stack))

        if self.findings["tech_stack"]:
            logger.info(f"   Detected: {', '.join(self.findings['tech_stack'])}")

    def _generate_brief(self) -> dict:
        """Genera un brief estructurado basado en los findings."""
        logger.info(f"\n📝 Generando brief...")

        # Extraer información de los archivos leídos
        description = ""
        features = []
        users = []

        for filename, content in self.findings["key_files_content"].items():
            # Extraer descripción de README
            if "README" in filename:
                lines = content.split('\n')
                for i, line in enumerate(lines[1:50]):  # Primeras 50 líneas
                    line = line.strip()
                    if line and not line.startswith('#') and len(line) > 20:
                        description = line
                        break

            # Buscar features listadas
            if "## Features" in content or "### Features" in content:
                in_features = False
                for line in content.split('\n'):
                    if "Features" in line and ("##" in line or "###" in line):
                        in_features = True
                        continue
                    if in_features:
                        if line.strip().startswith('- '):
                            features.append(line.strip()[2:])
                        elif line.strip().startswith('##'):
                            break

            # Buscar mención de usuarios/target
            for user_term in ["user", "customer", "developer", "admin", "end-user"]:
                if user_term in content.lower():
                    users.append(user_term)

        # Armar el brief
        brief = {
            "project_name": self.findings["name"],
            "description": description or f"{self.findings['name']} - Software project",
            "tech_stack": self.findings["tech_stack"],
            "features_detected": features[:5],  # Top 5
            "docs_found": self.findings["docs_found"],
            "key_files": list(self.findings["key_files_content"].keys()),
        }

        logger.info(f"   ✓ Brief generado con {len(features)} features detectadas")

        return brief


def format_brief_for_evaluation(brief: dict) -> str:
    """Format a scan brief for MasterMind evaluation.

    Args:
        brief: Brief dictionary from ProjectScanner.scan().

    Returns:
        Formatted Markdown string ready for evaluation.
    """
    return f"""
# Brief Generado: {brief['project_name']}

## Descripción Detectada
{brief['description']}

## Stack Técnico
{', '.join(brief['tech_stack']) if brief['tech_stack'] else 'No detectado'}

## Features Detectadas
{chr(10).join(f'- {f}' for f in brief['features_detected']) if brief['features_detected'] else '- No se detectaron features explícitas'}

## Documentación Encontrada
{chr(10).join(f'- {f}' for f in brief['docs_found'][:10])}

## Archivos Clave Analizados
{chr(10).join(f'- {f}' for f in brief['key_files'])}

---
⚠️  Este brief fue generado automáticamente por el Project Scanner.
Para mejores resultados, completa manualmente:
- Evidencia de validación (entrevistas, datos)
- Métricas objetivo (retention, activation)
- Usuario objetivo específico
"""


def evaluate_scanned_project(brief_text: str, use_mcp: bool = False) -> dict:
    """Evalúa el brief generado con el MasterMind Framework.

    Args:
        brief_text: Brief text in Markdown format.
        use_mcp: Whether to use MCP integration for brain queries.

    Returns:
        Dictionary with evaluation results from the framework.
    """
    from mastermind_cli.orchestrator import Coordinator, OutputFormatter

    logger.info(f"\n{'='*70}")
    logger.info(f"🧠 EVALUANDO CON MENTE MAESTRA")
    logger.info(f"{'='*70}")

    formatter = OutputFormatter()
    coordinator = Coordinator(formatter=formatter, use_mcp=use_mcp)

    result = coordinator.orchestrate(
        brief=brief_text.strip(),
        flow='full_product',
        max_iterations=2
    )

    return result


def main() -> dict:
    """Entry point for the MasterMind project scanner."""
    parser = argparse.ArgumentParser(
        description="Escanea un proyecto y lo evalúa con MasterMind Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'project_path',
        type=str,
        help='Path al proyecto a escanear'
    )
    parser.add_argument(
        '--mcp',
        action='store_true',
        help='Usar MCP (NotebookLM real)'
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='Profundidad de escaneo (default: 3)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Guardar brief generado en archivo'
    )

    args = parser.parse_args()

    # Escanear proyecto
    scanner = ProjectScanner(args.project_path, max_depth=args.depth)
    brief_data = scanner.scan()

    # Generar brief formateado
    brief_text = format_brief_for_evaluation(brief_data)

    # Guardar si se solicita
    if args.output:
        with open(args.output, 'w') as f:
            f.write(brief_text)
        logger.info(f"\n💾 Brief guardado en: {args.output}")

    # Mostrar brief generado
    logger.info(f"\n{'='*70}")
    logger.info(f"📋 BRIEF GENERADO")
    logger.info(f"{'='*70}")
    logger.info(brief_text)

    # Evaluar con MasterMind
    logger.info(f"\n⏳ Evaluando con MasterMind Framework...")
    result = evaluate_scanned_project(brief_text, use_mcp=args.mcp)

    # Mostrar resultado
    logger.info(f"\n{'='*70}")
    logger.info(f"📊 RESULTADO DE LA EVALUACIÓN")
    logger.info(f"{'='*70}")
    logger.info(f"Status: {result.get('status')}")
    logger.info(f"Veredicto: {result.get('veredict')}")

    if result.get('evaluations'):
        logger.info(f"\nEvaluaciones por cerebro:")
        for i, eval_result in enumerate(result['evaluations'][:3], 1):
            logger.info(f"  Cerebro #{i}: {eval_result.get('score', 'N/A')}")

    return result


if __name__ == "__main__":
    main()
