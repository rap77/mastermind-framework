---
description: Run mm brain consultation at the right moment. Auto-detects moment from project state or pass explicit arg.
argument-hint: [1|2|3|feed] — optional, auto-detects if omitted
---

<objective>
Run the mm:brain-context workflow at the correct moment in the GSD cycle.

Auto-detects which moment you're at based on project state:
- No ROADMAP.md → Moment 1 (before new-milestone)
- ROADMAP exists, no CONTEXT.md for current phase → Moment 2 (before plan-phase)
- PLAN.md exists without SUMMARY.md → Moment 3 (validate + iterate until Brain #7 approves)
- SUMMARY.md just created, no BRAIN-FEED update → feed (update BRAIN-FEED post-phase)

Pass an explicit argument to override auto-detection: `/mm:brain-context 3`
Use `--force` to re-run even if already completed: `/mm:brain-context 3 --force`
</objective>

<context>
Project: ! `pwd`
State: @ .planning/STATE.md
</context>

<detection>
! `
ROADMAP=".planning/ROADMAP.md"
PHASES_DIR=".planning/phases"
ARG="${1:-}"

# Explicit argument → use it directly
if [ -n "$ARG" ] && [[ "$ARG" =~ ^[123]$|^feed$ ]]; then
  echo "moment=$ARG"
  echo "reason=Argumento explícito"
  exit 0
fi

# Auto-detect from project state
if [ ! -f "$ROADMAP" ]; then
  echo "moment=1"
  echo "reason=No existe ROADMAP.md — antes de new-milestone"
  exit 0
fi

# Read current phase number from STATE.md
CURRENT_PHASE=$(grep -oP 'Phase: \K\d+' .planning/STATE.md 2>/dev/null | head -1)

if [ -n "$CURRENT_PHASE" ]; then
  PHASE_PAD=$(printf "%02d" "$CURRENT_PHASE")
  PHASE_DIR=$(ls -d "$PHASES_DIR"/${PHASE_PAD}-* 2>/dev/null | head -1)

  if [ -n "$PHASE_DIR" ]; then
    PLAN_FILE=$(ls "$PHASE_DIR"/*-PLAN.md 2>/dev/null | head -1)
    SUMMARY_FILE=$(ls "$PHASE_DIR"/*-SUMMARY.md 2>/dev/null | head -1)
    CONTEXT_FILE=$(ls "$PHASE_DIR"/*-CONTEXT.md 2>/dev/null | head -1)

    if [ -n "$SUMMARY_FILE" ]; then
      echo "moment=feed"
      echo "reason=SUMMARY.md encontrado — post-fase, actualizar BRAIN-FEED"
      echo "phase_dir=$PHASE_DIR"
      exit 0
    fi

    if [ -n "$PLAN_FILE" ]; then
      echo "moment=3"
      echo "reason=PLAN.md existe sin SUMMARY — validar con Brain #7 antes de ejecutar"
      echo "phase_dir=$PHASE_DIR"
      exit 0
    fi

    if [ -z "$CONTEXT_FILE" ]; then
      echo "moment=2"
      echo "reason=No existe CONTEXT.md para la fase actual — antes de plan-phase"
      echo "phase_dir=$PHASE_DIR"
      exit 0
    fi
  fi
fi

# Default fallback
echo "moment=2"
echo "reason=No se pudo determinar estado exacto — asumiendo Momento 2"
`
</detection>

<confirmation>
Parse the detection output above.

Show to user:
```
Detecté: Momento [N] — [reason]
Fase: [phase_dir if available]

¿Continuar? Presioná Enter para confirmar, o escribí el número para cambiar (1/2/3/feed):
```

Wait for user input before proceeding.
If user enters a number, override moment with that value.
</confirmation>

<execution>
After confirmation, read and follow the skill:

@ ~/.claude/skills/mm/brain-context/SKILL.md

Pass the detected/confirmed moment as the answer to the intake question.
The skill will route to the correct workflow automatically.
</execution>
