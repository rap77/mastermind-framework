#!/usr/bin/env python3
"""Cross-platform audio notification system.

Supports:
- Linux: PulseAudio (paplay), ALSA (aplay), espeak, terminal beeps
- macOS: afplay, say
- Windows: SystemSounds, PowerShell beeps
- WSL: Calls Windows host via powershell.exe
"""

import platform
import subprocess
import sys
from pathlib import Path
from typing import List


def play_linux_sound() -> bool:
    """Play sound on Linux using available audio backends."""
    # Try PulseAudio first (most common on modern Linux)
    try:
        sound_files = [
            "/usr/share/sounds/freedesktop/stereo/complete.oga",
            "/usr/share/sounds/freedesktop/stereo/message.oga",
            "/usr/share/sounds/freedesktop/stereo/phone-incoming-call.oga",
        ]

        for sound_file in sound_files:
            if Path(sound_file).exists():
                # Play it 3 times for attention
                for _ in range(3):
                    subprocess.run(
                        ["paplay", sound_file],
                        check=True,
                        capture_output=True,
                        timeout=10,
                    )
                return True
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        pass

    # Try ALSA
    try:
        sound_files = [
            "/usr/share/sounds/alsa/Front_Center.wav",
            "/usr/share/sounds/alsa/Side_Right.wav",
        ]

        for sound_file in sound_files:
            if Path(sound_file).exists():
                for _ in range(3):
                    subprocess.run(
                        ["aplay", "-q", sound_file],
                        check=True,
                        capture_output=True,
                        timeout=10,
                    )
                return True
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        pass

    # Try espeak (text-to-speech)
    try:
        subprocess.run(
            ["espeak", "-ven+f3", "-k5", "-s200", "Task complete"],
            check=True,
            capture_output=True,
            timeout=10,
        )
        return True
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        pass

    # Try spd-say (another TTS)
    try:
        subprocess.run(
            ["spd-say", "Task execution complete"],
            check=True,
            capture_output=True,
            timeout=10,
        )
        return True
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        pass

    # Last resort: terminal beeps
    print("\a\a\a\a\a", end="", flush=True)
    return True


def play_macos_sound() -> bool:
    """Play sound on macOS."""
    try:
        # Try system sounds first
        sound_files = [
            "/System/Library/Sounds/Glass.aiff",
            "/System/Library/Sounds/Ping.aiff",
            "/System/Library/Sounds/Purr.aiff",
            "/System/Library/Sounds/Sosumi.aiff",
        ]

        for sound_file in sound_files:
            if Path(sound_file).exists():
                for _ in range(3):
                    subprocess.run(
                        ["afplay", sound_file],
                        check=True,
                        capture_output=True,
                        timeout=10,
                    )
                return True
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        pass

    # Fallback to voice
    try:
        subprocess.run(
            ["say", "Task execution complete"],
            check=True,
            capture_output=True,
            timeout=10,
        )
        return True
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        pass

    # Terminal bell
    print("\a\a\a\a\a", end="", flush=True)
    return True


def play_windows_sound() -> bool:
    """Play sound on Windows using PowerShell."""
    try:
        # Use Windows SystemSounds
        ps_script = """
        [System.Media.SystemSounds]::Asterisk.Play()
        Start-Sleep -Milliseconds 300
        [System.Media.SystemSounds]::Asterisk.Play()
        Start-Sleep -Milliseconds 300
        [System.Media.SystemSounds]::Asterisk.Play()
        Start-Sleep -Milliseconds 300
        [System.Media.SystemSounds]::Exclamation.Play()
        """

        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def play_wsl_sound() -> bool:
    """Play sound from WSL by calling Windows host."""
    # WSL is Linux but needs to call Windows for audio
    return play_windows_sound()


def play_custom_audio_file(status: str = "complete") -> bool:
    """Play custom audio file if exists."""
    # Find project root
    project_root = Path.cwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            project_root = Path(result.stdout.strip())
    except Exception:
        pass

    # Check for custom audio files based on status
    # Formats: WAV (preferred, native), OGG, MP3 (fallback)
    extensions: List[str] = [".wav", ".ogg", ".mp3"]
    custom_locations: List[Path] = []

    for ext in extensions:
        custom_locations.extend(
            [
                project_root / ".notifications" / f"{status}{ext}",
                Path.home() / ".notifications" / f"{status}{ext}",
            ]
        )

    for audio_file in custom_locations:
        if audio_file.exists():
            env = detect_environment()

            try:
                # WSL needs special handling
                if env == "wsl":
                    # Convert WSL path to Windows path
                    result = subprocess.run(
                        ["wslpath", "-w", str(audio_file)],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    if result.returncode == 0:
                        windows_path = result.stdout.strip()

                        # Use Media.SoundPlayer - plays audio WITHOUT opening any window!
                        ps_script = f"""
                        $player = New-Object System.Media.SoundPlayer("{windows_path}")
                        $player.PlaySync()
                        """

                        subprocess.run(
                            ["powershell.exe", "-NoProfile", "-Command", ps_script],
                            capture_output=True,
                            text=True,
                            timeout=60,
                        )
                        print(f"✅ Playing {audio_file.name} (Direct audio, no window)")
                        return True

                # Regular Linux
                elif env == "linux":
                    # Try paplay (PulseAudio)
                    try:
                        subprocess.run(
                            ["paplay", str(audio_file)],
                            check=True,
                            capture_output=True,
                            timeout=60,
                        )
                        print(f"✅ Playing {audio_file.name} (PulseAudio)")
                        return True
                    except (FileNotFoundError, subprocess.CalledProcessError):
                        pass

                    # Try aplay (ALSA)
                    try:
                        subprocess.run(
                            ["aplay", "-q", str(audio_file)],
                            check=True,
                            capture_output=True,
                            timeout=60,
                        )
                        print(f"✅ Playing {audio_file.name} (ALSA)")
                        return True
                    except (FileNotFoundError, subprocess.CalledProcessError):
                        pass

                elif env == "darwin":  # macOS
                    subprocess.run(
                        ["afplay", str(audio_file)],
                        check=True,
                        capture_output=True,
                        timeout=60,
                    )
                    print(f"✅ Playing {audio_file.name} (macOS)")
                    return True

            except Exception as e:
                print(f"⚠️  Error playing {audio_file}: {e}")
                pass

    return False


def detect_environment() -> str:
    """Detect the current environment."""
    # Check if we're in WSL
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower() or "wsl" in f.read().lower():
                return "wsl"
    except Exception:
        pass

    # Regular platform detection
    return platform.system().lower()


def play_notification_sound(status: str = "complete") -> bool:
    """Play notification sound based on platform and environment."""
    # Try custom audio file first (status-based: complete.wav, error.wav, etc.)
    if play_custom_audio_file(status):
        return True

    # Detect environment
    env = detect_environment()

    # Route to appropriate sound handler
    if env == "wsl":
        return play_wsl_sound()
    elif env == "linux":
        return play_linux_sound()
    elif env == "darwin":
        return play_macos_sound()
    elif env == "windows":
        return play_windows_sound()
    else:
        # Unknown platform - try terminal beep
        print("\a\a\a\a\a", end="", flush=True)
        return True


def main():
    """Main entry point."""
    task_id = sys.argv[1] if len(sys.argv) > 1 else "Task"
    status = sys.argv[2] if len(sys.argv) > 2 else "complete"

    env = detect_environment()
    print(f"\n🔔 Playing notification sound for {task_id} ({env})...")

    success = play_notification_sound(status)

    if success:
        print(f"✅ Notification sound played on {env.upper()}")
        print(f"🔔 Task {task_id}: {status.upper()}\n")
    else:
        print(f"⚠️  Could not play notification sound on {env}\n")


if __name__ == "__main__":
    main()
