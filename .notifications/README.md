# Sistema de Notificaciones de Audio - Multi-Plataforma 🎵

## Entornos Soportados

### Linux (Nativo)
- **PulseAudio** (`paplay`) - Sonido del sistema
- **ALSA** (`aplay`) - Sonido hardware directo
- **espeak** - Text-to-speech "Task complete"
- **spd-say** - TTS alternativo
- **Beep terminal** - Último recurso (`\a`)

### macOS
- **afplay** - Sonidos del sistema (`/System/Library/Sounds/`)
- **say** - Voz del sistema "Task complete"
- **Beep terminal** - Fallback

### Windows
- **SystemSounds** - Sonidos del sistema .NET
  - Asterisk (notificación)
  - Exclamation (alerta)
- **PowerShell beeps** - Alternative

### WSL (Windows Subsystem for Linux)
- **Llama a Windows host** vía `powershell.exe`
- Reproduce en los altavoces de Windows
- Detección automática via `/proc/version`

## Audio Personalizado

### Archivos soportados:
- `complete.mp3`
- `complete.wav`
- `complete.ogg`

### Ubicación:
1. **Del proyecto**: `.notifications/complete.mp3`
2. **Del usuario**: `~/.notifications/complete.mp3`

### Ejemplo de uso:
```bash
# Descargar sonido de notificación
wget https://notificationsounds.com/notification-sounds/definite-555.mp3 \
  -O .notifications/complete.mp3

# O copiar tu propio archivo
cp ~/Downloads/mi-sonido.mp3 .notifications/complete.mp3
```

## Fuentes de Sonidos Gratuitos

### Sitios recomendados:
- **[Notification Sounds](https://notificationsounds.com/)** - MP3 gratis
- **[Zapsplat](https://www.zapsplat.com/sound-effect/category/notification)** - Variados formatos
- **[Freesound](https://freesound.org/)** - Sonidos de la comunidad

### Búsqueda recomendada:
- "notification complete"
- "success chime"
- "task done"
- "achievement"

## Prueba

```bash
# Test del sonido
python3 .claude/commands/mm/notify-complete.py TEST complete

# Test con audio personalizado (si existe)
python3 .claude/commands/mm/notify-complete.py TEST complete
```

## Integración Automática

El `task-executor` llama automáticamente:
```bash
python3 .claude/commands/mm/notify-complete.py {task_id} complete
```

Cuando todas las subtareas terminan.

## Nota Importante

**WSL**: Aunque estás en Linux, el audio se reproduce en Windows. Esto es normal y permite escuchar las notificaciones en toda la casa.
