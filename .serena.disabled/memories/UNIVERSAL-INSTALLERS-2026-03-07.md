# Universal Installers - 2026-03-07

## Fecha
2026-03-07

## Problema Resuelto

**Problema:** Usuarios sin Python 3.14+ no podían instalar MasterMind.

**Solución:** Instaladores universales que descargan e instalan Python automáticamente.

## Instaladores Creados

### 1. Linux/macOS (`install.sh`)

**Ubicación:** `/install.sh` en el repo

**Uso:**
```bash
curl -fsSL https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.sh | bash
```

**Características:**
- Detecta OS (Linux/macOS/WSL)
- Verifica dependencias (git, curl)
- Instala uv si no existe
- Descarga Python 3.14 vía uv
- Clona repositorio en `~/.mastermind-framework`
- Instala MasterMind globalmente
- Crea symlinks en `~/.local/bin/`
- Configura PATH automáticamente
- Agrega a `~/.bashrc` o `~/.zshrc`

**Salida coloreada:**
- Cyan: Headers
- Blue: Steps
- Green: Success
- Yellow: Warnings
- Red: Errors

### 2. Windows (`install.ps1`)

**Ubicación:** `/install.ps1` en el repo

**Uso:**
```powershell
irm https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.ps1 | iex
```

**Características:**
- Verifica Git instalado
- Instala uv vía PowerShell
- Descarga Python 3.14 vía uv
- Clona repositorio en `%USERPROFILE%\.mastermind-framework`
- Instala MasterMind globalmente
- Agrega a PATH de usuario
- Prompt para reiniciar PowerShell

## Flujo de Instalación

```
Usuario ejecuta comando
    ↓
1. Detectar OS y dependencias
    ↓
2. Instalar uv (si no existe)
    ↓
3. Descargar Python 3.14+ (si no existe)
    ↓
4. Clonar repositorio
    ↓
5. Instalar MasterMind globalmente
    ↓
6. Configurar PATH
    ↓
7. Verificar instalación
    ↓
Listo: mm y mastermind disponibles desde cualquier lugar
```

## Lo que Instala

### Archivos creados

**Linux/macOS:**
```
~/.mastermind-framework/     # Repositorio clonado
~/.local/bin/mastermind      # Symlink al comando
~/.local/bin/mm              # Symlink al alias
~/.bashrc o ~/.zshrc         # PATH actualizado
```

**Windows:**
```
%USERPROFILE%\.mastermind-framework\
%USERPROFILE%\.mastermind-framework\.venv\Scripts\
PATH actualizado con .venv\Scripts
```

### Dependencias instaladas

- **uv** (package manager) - si no existía
- **Python 3.14** - via uv, si no existía
- **mastermind-framework** - el paquete en sí

## Verificación

```bash
# Verificar instalación
mm info
mm --version
mastermind --version

# Ver estado
mm install status

# Usar en un proyecto
cd /path/to/project
mm install init
```

## Casos de Uso

### Usuario sin Python

**Antes:** Necesitaba instalar Python 3.14 manualmente
**Ahora:** Ejecuta un comando, todo automático

### Usuario con Python 3.12

**Antes:** Error de versión
**Ahora:** Instalador descarga Python 3.14 automáticamente

### Usuario con Python 3.14+

**Antes:** Instalar manual
**Ahora:** Instalador detecta y usa versión existente

### Windows sin Python

**Antes:** Manual, complicado
**Ahora:** Script PowerShell que hace todo

## Errores Comunes y Soluciones

### Error: "Missing required dependencies: git curl"

**Solución:**
```bash
# Ubuntu/Debian
sudo apt install git curl

# Fedora/RHEL
sudo yum install git curl

# macOS
brew install git curl
```

### Error: "uv not found in PATH"

**Solución:** Instalador ya lo maneja agregando a PATH

### Error: "mm command not found"

**Solución:**
```bash
# Recargar shell
source ~/.bashrc  # o source ~/.zshrc

# O iniciar nueva terminal
```

### Windows: "Restart PowerShell"

**Solución:** Cerrar y abrir PowerShell nuevamente

## Testing

### Test en Linux

```bash
# Crear VM limpia (Ubuntu)
vagrant init ubuntu/jammy64
vagrant up
vagrant ssh

# Ejecutar instalador
curl -fsSL https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.sh | bash

# Verificar
mm info
```

### Test en macOS

```bash
# Ejecutar instalador
curl -fsSL https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.sh | bash

# Verificar
mm info
```

### Test en Windows

```powershell
# Ejecutar instalador
irm https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.ps1 | iex

# Verificar
mm info
```

## README Actualizado

**Sección Quick Start renovada:**

```markdown
## Quick Start

### Instalación Universal (Recomendado)

¡No necesitas Python instalado! El instalador lo hace todo por vos.

#### Linux / macOS
curl -fsSL https://.../install.sh | bash

#### Windows
irm https://.../install.ps1 | iex
```

## Archivos Modificados/Creados

- `install.sh` (nuevo) - Installer Linux/macOS
- `install.ps1` (nuevo) - Installer Windows
- `README.md` (modificado) - Nueva sección Quick Start

## Commit

**Hash:** f95b41f
**Mensaje:** feat: add universal installers for users without Python

## Próximas Mejoras (Opcionales)

1. **Desinstalador universal** (`uninstall.sh`, `uninstall.ps1`)
2. **Updater automático** (`mm self-update`)
3. **Docker image** para usuarios que prefieren contenedores
4. **Homebrew formula** para macOS
5. **Snap package** para Linux
6. **Chocolatey package** para Windows

## Beneficios

1. **Zero-config** para usuarios sin Python
2. **Instalación en 1 comando**
3. **Cross-platform** (Linux, macOS, Windows)
4. **Actualizaciones fáciles** (git pull)
5. **Desinstalación limpia** (borrar carpeta)
6. **Aislado** del sistema Python del usuario
