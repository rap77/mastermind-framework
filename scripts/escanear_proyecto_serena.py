#!/usr/bin/env python3
"""
MasterMind Framework - Deep Project Scanner with Serena MCP

Analiza profundamente un proyecto usando Serena MCP:
- Lee archivos de documentación
- Analiza estructura de código con símbolos
- Extrae información de arquitectura
- Genera un brief completo
- Evalúa con los 7 cerebros

Requiere: Serena MCP disponible en el entorno
"""
import glob
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Add mastermind-cli to path
MASTERMIND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f"{MASTERMIND_ROOT}/tools/mastermind-cli")


class DeepProjectScanner:
    """Escaneo profundo de proyecto usando análisis de código."""

    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path).resolve()

        if not self.project_path.exists():
            raise ValueError(f"Project path does not exist: {self.project_path}")

        self.findings = {
            "project_name": self.project_path.name,
            "description": "",
            "tech_stack": [],
            "architecture": "",
            "features": [],
            "users": [],
            "apis": [],
            "database_models": [],
            "docs_content": {},
            "metrics_found": [],
            "business_model": "",
        }

    def scan_with_serena_commands(self) -> str:
        """
        Genera comandos Serena para análisis profundo.

        Returns: JSON string con findings
        """
        commands = []

        # 1. List directory structure
        commands.append({
            "tool": "list_dir",
            "params": {
                "relative_path": ".",
                "recursive": True,
                "skip_ignored_files": True
            },
            "purpose": "Get project structure"
        })

        # 2. Find and read key documentation files
        doc_patterns = [
            "README.md",
            "PRD*.md",
            "SPEC*.md",
            "ARCHITECTURE*.md",
            "DESIGN*.md",
            "docs/*.md"
        ]

        for pattern in doc_patterns:
            commands.append({
                "tool": "find_file",
                "params": {
                    "file_mask": pattern,
                    "relative_path": "."
                },
                "purpose": f"Find {pattern}"
            })

        # 3. Get symbols overview for key code files
        code_dirs = ["src", "app", "lib", "frontend", "backend", "api"]
        for code_dir in code_dirs:
            commands.append({
                "tool": "get_symbols_overview",
                "params": {
                    "relative_path": f"{code_dir}/*.py" if self._is_python() else f"{code_dir}/*.ts",
                    "depth": 1
                },
                "purpose": f"Analyze {code_dir} structure"
            })

        # 4. Search for specific patterns
        search_patterns = [
            ("TODO|FIXME", "Find TODOs and FIXMEs"),
            ("API|endpoint|route", "Find API definitions"),
            ("model|schema|entity", "Find data models"),
            ("config|ENV|setting", "Find configuration"),
        ]

        for pattern, purpose in search_patterns:
            commands.append({
                "tool": "search_for_pattern",
                "params": {
                    "substring_pattern": pattern,
                    "restrict_search_to_code_files": True
                },
                "purpose": purpose
            })

        return json.dumps(commands, indent=2)

    def generate_analysis_prompt(self) -> str:
        """Genera el prompt para que Claude analice el proyecto."""
        return f"""
You are a senior product analyst. Analyze the project at: {self.project_path}

TASK: Extract a comprehensive product brief by examining:

1. **Documentation** (read these files first):
   - README.md - What does this project do?
   - Any PRD, SPEC, or DESIGN docs - Product requirements
   - Any ARCHITECTURE docs - Technical decisions

2. **Code Structure** (analyze key directories):
   - src/ or app/ - Main application code
   - frontend/ - UI components
   - backend/ or api/ - Server logic
   - models/ or db/ - Data models

3. **Configuration Files**:
   - package.json / pyproject.toml - Dependencies and stack
   - docker-compose.yml / Dockerfile - Infrastructure
   - .env.example - Configuration needs

4. **Generate a Brief with**:

```markdown
# [Project Name]

## Descripción
[What does this project do? Who is it for?]

## Problema que Resuelve
[What pain point does it address?]

## Solución Propuesta
[How does it solve the problem?]

## Stack Técnico
[Technologies detected]

## Features Principales
[List 3-5 main features based on code/docs]

## Usuario Objetivo
[Who is this for? Be specific]

## Evidencia de Validación
[What validation exists? If none, state "No se detectó evidencia"]

## Métricas
[What metrics are mentioned or tracked?]
```

Use Serena MCP tools to:
- list_dir: See project structure
- find_file: Locate documentation
- read: Read file contents
- get_symbols_overview: Understand code architecture
- search_for_pattern: Find specific implementations

Be thorough. The better the brief, the better the evaluation.
"""

    def generate_brief_from_manual_analysis(self) -> dict:
        """
        Genera un brief basado en análisis manual del proyecto.

        Este método es para usar cuando Serena MCP no está disponible directamente.
        """


        logger.info(f"\n{'='*70}")
        logger.info(f"🔍 DEEP PROJECT SCANNER")
        logger.info(f"{'='*70}")
        logger.info(f"📁 Path: {self.project_path}")

        brief = {
            "project_name": self.project_path.name,
            "description": "",
            "problem": "",
            "solution": "",
            "tech_stack": [],
            "features": [],
            "target_user": "",
            "evidence": "No se detectó evidencia de validación",
            "metrics": [],
        }

        # 1. Buscar y leer README
        readme_path = self.project_path / "README.md"
        if readme_path.exists():
            logger.info(f"\n📖 Leyendo README.md...")
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                brief["description"] = self._extract_description(content)
                brief["features"] = self._extract_features(content)

        # 2. Buscar otros docs
        for doc_file in ["PRD.md", "SPEC.md", "ARCHITECTURE.md", "DESIGN.md"]:
            doc_path = self.project_path / doc_file
            if doc_path.exists():
                logger.info(f"📖 Leyendo {doc_file}...")
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    brief["docs_content"] = brief.get("docs_content", {})
                    brief["docs_content"][doc_file] = content

        # 3. Detectar stack técnico
        brief["tech_stack"] = self._detect_tech_stack()

        # 4. Analizar estructura de código
        brief["code_structure"] = self._analyze_code_structure()

        # 5. Buscar APIs y modelos
        brief["apis"] = self._find_apis()
        brief["models"] = self._find_models()

        return brief

    def _extract_description(self, readme_content: str) -> str:
        """Extrae la descripción del README."""
        lines = readme_content.split('\n')
        descriptions = []

        for i, line in enumerate(lines):
            # Buscar primer párrafo después del título
            if line.strip() and not line.startswith('#'):
                # Capturar hasta las siguientes líneas vacías
                j = i
                while j < len(lines) and lines[j].strip() and not lines[j].startswith('#'):
                    descriptions.append(lines[j].strip())
                    j += 1
                    if len(descriptions) > 3:  # Limitar a 3 líneas
                        break
                break

        return ' '.join(descriptions) if descriptions else "No description found"

    def _extract_features(self, content: str) -> list:
        """Extrae features listadas en el contenido."""
        features = []
        in_features = False

        for line in content.split('\n'):
            if 'feature' in line.lower() and ('##' in line or '###' in line):
                in_features = True
                continue
            if in_features:
                if line.strip().startswith('- ') or line.strip().startswith('* '):
                    features.append(line.strip()[2:].strip())
                elif line.strip().startswith('##'):
                    break

        return features[:10]  # Top 10 features

    def _detect_tech_stack(self) -> list:
        """Detecta el stack técnico."""
        stack = []

        # Check por archivos de configuración
        config_files = {
            "package.json": ["TypeScript/JavaScript"],
            "pyproject.toml": ["Python"],
            "Cargo.toml": ["Rust"],
            "go.mod": ["Go"],
            "Gemfile": ["Ruby"],
        }

        for file, technologies in config_files.items():
            if (self.project_path / file).exists():
                stack.extend(technologies)

        # Leer dependencias específicas
        if (self.project_path / "package.json").exists():
            try:
                with open(self.project_path / "package.json") as f:
                    deps = json.load(f).get("dependencies", {})
                    deps_str = ' '.join(deps.keys()).lower()

                    if 'react' in deps_str: stack.append("React")
                    if 'next' in deps_str: stack.append("Next.js")
                    if 'vue' in deps_str: stack.append("Vue.js")
                    if 'angular' in deps_str: stack.append("Angular")
                    if 'express' in deps_str: stack.append("Express.js")
                    if 'django' in deps_str: stack.append("Django")
            except (json.JSONDecodeError, KeyError, OSError):
                pass

        return list(set(stack))

    def _analyze_code_structure(self) -> dict:
        """Analiza la estructura del código."""


        structure = {
            "frontend_dirs": 0,
            "backend_dirs": 0,
            "test_files": 0,
            "api_files": 0,
        }

        # Directorios frontend
        for pattern in ["src/components/**", "app/components/**", "frontend/**"]:
            if glob.glob(str(self.project_path / pattern), recursive=True):
                structure["frontend_dirs"] += 1

        # Directorios backend
        for pattern in ["src/api/**", "app/api/**", "backend/**", "server/**"]:
            if glob.glob(str(self.project_path / pattern), recursive=True):
                structure["backend_dirs"] += 1

        # Tests
        for pattern in ["**/*test*.py", "**/*test*.ts", "**/*.test.ts"]:
            if glob.glob(str(self.project_path / pattern), recursive=True):
                structure["test_files"] += 1

        # APIs
        for pattern in ["**/routes/**", "**/api/**", "**/controllers/**"]:
            if glob.glob(str(self.project_path / pattern), recursive=True):
                structure["api_files"] += 1

        return structure

    def _find_apis(self) -> list:
        """Busca definiciones de API."""


        apis = []

        # Buscar archivos de routes/controllers
        for pattern in ["**/routes/*.py", "**/routes/*.ts", "**/api/*.py"]:
            for filepath in glob.glob(str(self.project_path / pattern), recursive=True):
                rel_path = os.path.relpath(filepath, self.project_path)
                apis.append(rel_path)

        return apis[:5]  # Top 5

    def _find_models(self) -> list:
        """Busca modelos de datos."""


        models = []

        for pattern in ["**/models/*.py", "**/models/*.ts", "**/entities/*.py"]:
            for filepath in glob.glob(str(self.project_path / pattern), recursive=True):
                rel_path = os.path.relpath(filepath, self.project_path)
                models.append(rel_path)

        return models[:5]  # Top 5

    def _is_python(self) -> bool:
        """Detecta si es un proyecto Python."""
        return ((self.project_path / "pyproject.toml").exists() or
                (self.project_path / "requirements.txt").exists() or
                (self.project_path / "setup.py").exists())


def format_generated_brief(brief: dict) -> str:
    """Formatea el brief generado para evaluación."""
    return f"""
# Brief Generado: {brief['project_name']}

## Descripción
{brief.get('description', 'No description detected')}

## Stack Técnico
{', '.join(brief.get('tech_stack', ['No detectado']))}

## Features Detectadas
{chr(10).join(f'- {f}' for f in brief.get('features', [])[:10]) if brief.get('features') else '- No se detectaron features explícitas'}

## Estructura de Código
- Frontend dirs: {brief.get('code_structure', {}).get('frontend_dirs', 0)}
- Backend dirs: {brief.get('code_structure', {}).get('backend_dirs', 0)}
- Test files: {brief.get('code_structure', {}).get('test_files', 0)}
- API files: {brief.get('code_structure', {}).get('api_files', 0)}

## APIs Encontradas
{chr(10).join(f'- {api}' for api in brief.get('apis', [])) if brief.get('apis') else '- No se detectaron APIs'}

## Modelos de Datos
{chr(10).join(f'- {model}' for model in brief.get('models', [])) if brief.get('models') else '- No se detectaron modelos'}

## Documentación Analizada
{chr(10).join(f'- {doc}' for doc in brief.get('docs_content', {}).keys())}

---

### ⚠️  Campos Faltantes (Requieren Input Manual)

Para una evaluación completa, AGREGA:

**Problema que Resuelve:**
[¿Qué dolor específico resuelve este producto?]

**Usuario Objetivo:**
[¿Quién específicamente usa este producto?]

**Evidencia de Validación:**
- ¿Cuántas personas entrevistaste?
- ¿Qué datos de mercado tienes?
- ¿Qué comportamiento observaste?

**Métricas Objetivo:**
- D7 retention: >__%
- D30 retention: >__%
- Activation rate: >__%
- NPS: >__

**Modelo de Monetización:**
[Freemium / Pago / Enterprise / Otro]

---

📌 Este brief fue generado automáticamente por Deep Project Scanner.
El análisis de código es automático, pero la información de negocio requiere input manual.
"""


def main() -> None:
    """Entry point for the MasterMind deep project scanner."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Escaneo profundo de proyecto con análisis de código",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('project_path', help='Path al proyecto a escanear')
    parser.add_argument('--output', '-o', help='Guardar brief en archivo')
    parser.add_argument('--serena-prompt', action='store_true',
                       help='Generar prompt para análisis con Serena MCP')

    args = parser.parse_args()

    scanner = DeepProjectScanner(args.project_path)

    if args.serena_prompt:
        # Generar prompt para usar con Serena MCP
        prompt = scanner.generate_analysis_prompt()
        logger.info(prompt)
        return

    # Escaneo automático
    brief = scanner.generate_brief_from_manual_analysis()

    # Formatear brief
    brief_text = format_generated_brief(brief)

    # Guardar si se solicita
    if args.output:
        with open(args.output, 'w') as f:
            f.write(brief_text)
        logger.info(f"\n💾 Brief guardado en: {args.output}")

    # Mostrar brief
    logger.info(brief_text)

    # Instrucciones para evaluar
    logger.info(f"\n{'='*70}")
    logger.info(f"📋 PRÓXIMO PASO: Evaluar este brief")
    logger.info(f"{'='*70}")
    logger.info(f"""
Para evaluar este brief con MasterMind Framework:

1. Completa los campos manuales (Problema, Usuario, Evidencia, Métricas)
2. Ejecuta:

   uv run python scripts/evaluar_proyecto.py --brief "[TU BRIEF COMPLETO]" --mcp

3. O guarda el brief en un archivo y usa:

   uv run python scripts/evaluar_proyecto.py --file brief_completo.md --mcp
""")


if __name__ == "__main__":
    main()
