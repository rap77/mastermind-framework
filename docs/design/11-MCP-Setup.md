# MCP Setup - MasterMind Framework

## Configuración de Servidores MCP

MasterMind Framework utiliza **MCP (Model Context Protocol)** para extender las capacidades de Claude Code con herramientas especializadas.

## Servidores Configurados

### 1. Serena 🧭
**Propósito**: Memoria del proyecto, análisis semántico de código, persistencia de sesión

**Casos de uso en MasterMind**:
- Mantener contexto entre sesiones de trabajo en los 7 cerebros
- Navegación inteligente de la estructura de fuentes y cerebros
- Operaciones de refactorización (rename, extract, move functions)
- Búsqueda semántica de conocimiento destilado

**Instalación**:
```bash
# Ya configurado en .mcp.json
# Requiere: uv, Python 3.9+
```

### 2. Context7 📚
**Propósito**: Documentación oficial de librerías y frameworks

**Casos de uso en MasterMind**:
- Consulta de documentación de Python, Click, Rich
- Patrones de arquitectura (Clean Architecture, Hexagonal)
- Mejores prácticas de YAML y configuración

**Instalación**:
```bash
# Ya configurado en .mcp.json
# Requiere: Node.js 16+
```

### 3. Sequential-Thinking 🧠
**Propósito**: Razonamiento sistemático multi-paso

**Casos de uso en MasterMind**:
- Análisis de requisitos complejos del Orquestador
- Evaluación de outputs del Cerebro #7
- Desglose de tareas en PRPs
- Análisis de trade-offs arquitectónicos

**Instalación**:
```bash
# Ya configurado en .mcp.json
# Requiere: Node.js 16+
```

## Verificación

```bash
# Verificar que Claude Code detecta los servidores
claude mcp list

# En Claude Code, ejecutar:
/mcp
```

## Uso con MasterMind

### Ejemplo 1: Cargar contexto del proyecto
```
/sc:load

# Serena automáticamente:
# - Indexa estructura de 7 cerebros
# - Carga metadata de fuentes
# - Establece símbolos para navegación
```

### Ejemplo 2: Guardar progreso de sesión
```
/sc:save

# Serena guarda:
# - Contexto de cerebros activos
# - Estado de tareas en progreso
# - Decisiones arquitectónicas tomadas
```

### Ejemplo 3: Refactorización de fuentes
```
"Renombrar FUENTE-001 a FUENTE-001-cagan-inspired manteniendo referencias"

# Serena:
# - Renombra el archivo
# - Actualiza todas las referencias
# - Busca imports/referencias en otros cerebros
```

## Arquitectura de Integración

```
┌─────────────────────────────────────────────────────┐
│              Claude Code Session                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │  Orquestador│  │ Cerebro #7  │  │    CLI      ││
│  │  Central    │  │  Evaluador  │  │             ││
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘│
│         │                │                │       │
│         └────────────────┴────────────────┘       │
│                          │                        │
│                   ┌──────▼──────┐                 │
┌───────────────────┤  MCP Layer  ├─────────────────┐
│                   └──────┬──────┘                 │
│         ┌────────────────┼────────────────┐       │
│         │                │                │       │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐│
│  │   Serena    │  │  Context7   │  │ Sequential  ││
│  │  (Memory)   │  │  (Docs)     │  │  (Reason)   ││
│  └─────────────┘  └─────────────┘  └─────────────┘│
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │         MasterMind Filesystem               │   │
│  │  docs/software-development/01-*-brain/      │   │
│  │  agents/brains/  skills/reusable/           │   │
│  └─────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

## Servidores Adicionales (Opcionales)

### Magic ✨
Para generar componentes UI del futuro dashboard de MasterMind:
```bash
export TWENTYFIRST_API_KEY="your-key"

# Agregar a .mcp.json:
"magic": {
  "command": "npx",
  "args": ["@21st-dev/magic"],
  "env": {"API_KEY": "${TWENTYFIRST_API_KEY}"}
}
```

### Tavily 🔍
Para investigación web del Cerebro #7:
```bash
export TAVILY_API_KEY="tvly-your-key"

# Agregar a .mcp.json:
"tavily": {
  "command": "npx",
  "args": ["-y", "tavily-mcp@latest"],
  "env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"}
}
```

## Troubleshooting

**Serena no inicia**:
```bash
# Verificar uv instalado
uv --version

# Instalar Serena manualmente
uv tool install serena-ai
uv tool run serena-ai start-mcp-server --context ide-assistant
```

**Context7 falla**:
```bash
# Limpiar caché de npm
npm cache clean --force

# Verificar Node.js versión
node --version  # debe ser 16+
```

**Servidor no aparece en /mcp**:
```bash
# Reiniciar Claude Code completamente
# Verificar que .mcp.json esté en la raíz del proyecto
cat .mcp.json
```

## Recursos

- [SuperClaude MCP Guide](https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/docs/user-guide/mcp-servers.md)
- [Serena Repository](https://github.com/oraios/serena)
- [MCP Specification](https://modelcontextprotocol.io/)
