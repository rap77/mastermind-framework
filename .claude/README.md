# MasterMind Framework - Claude Code Resources

## Namespace Convention

Todos los recursos de MasterMind usan el namespace `mm:` para evitar conflictos con otros proyectos y habilidades.

```
/mm:command    - Comandos de slash
mm:hook        - Hooks de pre-commit
mm:agent       - Agentes especializados
```

## Estructura de Carpetas

```
.claude/
├── commands/
│   └── mm/                    # Namespace para slash commands
│       ├── ask-product.md     # → /mm:ask-product
│       ├── ask-ux.md          # → /mm:ask-ux
│       ├── project-audit.md   # → /mm:project-audit
│       └── ...
│
├── hooks/
│   └── mm/                    # Namespace para hooks
│   ├── pr-validation.md       # Valida PRs antes de commitear
│   └── eval-log.md            # Loguea evaluaciones
│
└── agents/
    └── mm/                    # Namespace para agentes
        ├── product-validator.md
        └── ux-reviewer.md
```

## Comandos Disponibles

### Consulta de Cerebros

- `/mm:ask-product` - Consulta cerebro Producto (qué y por qué)
- `/mm:ask-ux` - Consulta cerebro UX Research (experiencia)
- `/mm:ask-design` - Consulta cerebro UI Design (visual)
- `/mm:ask-frontend` - Consulta cerebro Frontend (interfaz)
- `/mm:ask-backend` - Consulta cerebro Backend (lógica)
- `/mm:ask-qa` - Consulta cerebro QA/DevOps (estabilidad)
- `/mm:ask-growth` - Consulta cerebro Growth/Data (evolución)
- `/mm:ask-all` - Consulta TODOS los cerebros como equipo
- `/mm:ask-ui-docs` - Genera documentación de design system

### Gestión de Proyectos

- `/mm:project-health-check` - Análisis completo de 7 cerebros
- `/mm:audit` - Alias rápido de project-health-check

### PRDs y Especificaciones

- `/mm:lite-prd-generator` - Convierte idea rough en PRD demo-grade
- `/mm:prd-clarifier` - Refina y clarifica PRD existente
- `/mm:generate-prp` - Crea PRP (Project Requirements Plan)
- `/mm:execute-prp` - Ejecuta PRP existente

### Mejora de Prompts

- `/mm:improve-prompt` - Transforma prompts genéricos en detallados
- `/mm:ux-spec-to-prompt` - Convierte specs UX en prompts de construcción

### Desarrollo

- `/mm:explore-first` - Explora código antes de implementar

## Instalación en Proyectos Externos

Para usar estos recursos en otros proyectos:

```bash
# Copiar la carpeta .claude completa
cp -r /path/to/mastermind/.claude /path/to/your-project/

# O solo comandos específicos
cp -r /path/to/mastermind/.claude/commands/mm /path/to/your-project/.claude/commands/
```

## Convención de Nombres

Al crear nuevos recursos:

1. **Usar nombres limpios** sin prefijo en el archivo
   - ✅ `ask-product.md` → `/mm:ask-product`
   - ❌ `mm-ask-product.md` → `/mm:mm-ask-product` (redundante)

2. **El namespace viene de la carpeta contenedora**
   - `.claude/commands/mm/archivo.md` → `/mm:archivo`
   - `.claude/hooks/mm/archivo.md` → hook `mm:archivo`

3. **Ser descriptivo pero conciso**
   - ✅ `ask-product.md`
   - ✅ `project-audit.md`
   - ❌ `ask-to-the-product-brain-about-something.md`

## Notas

- Los archivos `Zone.Identifier` son artefactos de Windows y pueden eliminarse
- Git tracking mantiene el historial de movimientos de archivos
- Los comandos son discoverables via `/help` en Claude Code
