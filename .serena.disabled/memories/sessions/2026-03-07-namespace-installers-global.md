# Session 2026-03-07 - Namespace + Installers + Global MM

## Fecha
2026-03-07

## Objetivo Principal

Implementar namespace `mm:` para todos los recursos de MasterMind y crear instaladores universales para usuarios sin Python.

## Lo que se Logró

### 1. Namespace Implementation ✅
**Commit:** daf6b7f

Estructura de carpetas con namespace:
```
.claude/
├── commands/mm/     # 19 comandos → /mm:ask-product, etc.
├── hooks/mm/        # Lista para hooks futuros
└── agents/mm/       # Lista para agentes futuros
```

**Archivos movidos:** 18 comandos renombrados con git mv
**Documentación:** .claude/README.md con guía de namespace

**Comandos ahora accesibles:**
- `/mm:ask-product` - Consulta cerebro Producto
- `/mm:project-audit` - Análisis completo de 7 cerebros
- `/mm:lite-prd-generator` - Genera PRD
- Y 16 comandos más...

### 2. Installer Updates ✅
**Commits:** 00155b2, 4aec37c, 21e2ef7

**Cambios en `mastermind install init`:**
- Ahora copia `.claude/commands/mm/` en lugar de estructura plana
- Soporta hooks/mm/ y agents/mm/
- Actualiza README con comandos `/mm:`
- Desinstalador mejorado con `--remove-readme` flag

**Desinstalador mejorado:**
- Elimina carpetas namespace completas
- Limpia directorios padre vacíos
- Opción de limpiar README

### 3. Universal Installers ✅
**Commits:** f95b41f (created), 4aec37c (fixed), 21e2ef7 (uv tool)

**Linux/macOS (`install.sh`):**
- Auto-detecta OS y dependencias
- Instala uv si no existe
- Descarga Python 3.14 vía uv
- Instala MasterMind con `uv tool install`
- Configura PATH automáticamente

**Windows (`install.ps1`):**
- PowerShell installer con mismas características
- Checks para Git
- Agrega a PATH de usuario

**Uso:**
```bash
curl -fsSL https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.sh | bash
```

### 4. Global MM Command ✅

**Problema:** `mm` no funcionaba globalmente
**Causa:** Paquete instalado solo en venv local
**Solución:** Ejecutar instalador universal

**Resultado:**
```bash
mm --version  # Ahora funciona desde cualquier lugar
mm info
mm brain status
```

### 5. Zsh History Corruption Fix

**Problema:** Mensaje "zsh: corrupt history file" en cada sesión
**Causa raíz:** `INC_APPEND_HISTORY` + 5 instancias de zsh simultáneas

**Solución aplicada:**
1. Eliminar `INC_APPEND_HISTORY` de ~/.zshrc
2. Recrear archivo de historial con formato correcto
3. Usar SHARE_HISTORY (escribe al salir, no inmediatamente)

**Cambio en ~/.zshrc:**
```bash
# INC_APPEND_HISTORY deshabilitado - causa corrupción con múltiples instancias
# setopt INC_APPEND_HISTORY
```

## Commits Importantes

| Hash | Descripción |
|------|-------------|
| daf6b7f | feat: implement mm namespace for all Claude Code resources |
| 00155b2 | feat: update installer for mm namespace and improve uninstall |
| f95b41f | feat: add universal installers for users without Python |
| 4aec37c | fix: use uv --global instead of --system for installation |
| 21e2ef7 | feat: use uv tool install instead of uv pip install |

## Archivos Clave Modificados

**Framework:**
- `install.sh` - Installer Linux/macOS (374 líneas)
- `install.ps1` - Installer Windows (178 líneas)
- `README.md` - Instalación universal como método principal
- `.claude/README.md` - Documentación de namespace
- `mastermind_cli/commands/install.py` - Actualizado para namespace

**Usuario (no en repo):**
- `~/.zshrc` - INC_APPEND_HISTORY deshabilitado
- `~/.mastermind-framework/` - instalación via installer

## Decisones Técnicas

### ¿Por qué `uv tool install` en lugar de `uv pip install`?

`uv pip install` no tiene flag `--global`. La forma correcta de instalar herramientas CLI globalmente con uv es:

```bash
uv tool install -e /path/to/package
```

Esto crea entry points en `~/.local/share/uv/bin/` y asegura que `~/.local/bin/` esté en PATH.

### ¿Por qué namespace mm/ y no prefijo mm-?

**Elegido:** `.claude/commands/mm/archivo.md` → `/mm:archivo`
**Descartado:** `.claude/commands/mm-archivo.md` → `/mm:mm-archivo`

**Razón:** La carpeta provee el namespace, el archivo queda limpio. Permite:

```bash
# Fácil filtrar recursos de MasterMind
ls .claude/commands/mm/
ls .claude/hooks/mm/
ls .claude/agents/mm/

# Fácil copiar todo un namespace
cp -r .claude/commands/mm /path/to/project/.claude/commands/
```

### ¿Por qué deshabilitar INC_APPEND_HISTORY?

**Problema:** Con `INC_APPEND_HISTORY`, zsh escribe al archivo después de cada comando. Con múltiples instancias (5 en este caso), todas escriben simultáneamente sin coordinación → corrupción.

**Solución:** SHARE_HISTORY sin INC_APPEND_HISTORY
- Historial se comparte entre sesiones
- Se escribe al cerrar cada sesión (no inmediatamente)
- Evita condiciones de carrera

## Estado del Framework

**Versión:** 1.0.0
**Estado:** Production Ready con namespace `mm:`

**Instalación universal:**
```bash
curl -fsSL https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.sh | bash
```

**Comandos globales:**
```bash
mm info
mm install status
mm brain status
```

**Slash commands (en cualquier proyecto):**
```bash
/mm:ask-product
/mm:project-audit
/mm:lite-prd-generator
```

## Próximos Pasos Sugeridos

1. **Testing:** Probar instaladores en VM limpia (Ubuntu, macOS, Windows)
2. **Docs:** Actualizar guía de contribución con namespace convention
3. **Release:** Considerar v1.1.0 con estos cambios
4. **Distribución:** Promocionar instalador universal en README

## Issues Resueltos

| Issue | Solución |
|-------|----------|
| Conflicto de nombres con otros proyectos | Namespace mm: |
| Instalación complicada sin Python | Installer universal |
| `mm` no funciona globalmente | `uv tool install` |
| Zsh history corruption | Deshabilitar INC_APPEND_HISTORY |
| Desinstalación incompleta | Limpiar carpetas mm/ y README |

## Testing Pendiente

- [ ] Installer en Ubuntu limpio
- [ ] Installer en macOS limpio
- [ ] Installer en Windows limpio
- [ ] Desinstalador completo
- [ ] Comandos /mm: en proyecto externo
