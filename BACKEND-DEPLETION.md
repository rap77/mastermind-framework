# ⚠️ Backend Depletion Warning

**Backend:** claude-sonnet-4-6
**Status:** 🔴 CRITICAL
**Usage:** 304% (3,040,000 / 1,000,000 tokens)
**Remaining:** 0 tokens

---

## What To Do

### Option 1: Backend Switcheo (Recommended)

Run this to switch to OpenRouter or Z.ai (fallback):

```bash
mm-flow backend set openrouter-claude
/mm:complete-task <task-id> --continue  # Resume current task with new backend
```

### Option 2: Pause & Request More Credits

Contact support to request additional credits for claude-sonnet-4-6.

Then resume:

```bash
/mm:complete-task <task-id> --continue
```

### Option 3: Review Token Usage

See which tools consumed the most tokens:

```bash
cat .planning/BACKEND-USAGE.json | jq '.claude-sonnet-4-6'
```

---

## Multi-Backend Strategy

MM-Flow automatically tries backends in this order:
1. **claude-opus-4-6** (primary) — ~1M tokens
2. **openrouter-claude** (fallback) — ~2M tokens
3. **z-ai-claude** (emergency) — ~500K tokens

If claude-sonnet-4-6 hits 100%, the next phase execution will automatically switch to the next available backend.
