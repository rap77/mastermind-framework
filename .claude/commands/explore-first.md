---
description: "Explore the codebase thoroughly before implementing. Forces comprehensive discovery of related files and patterns."
argument-hint: "[feature or topic to explore]"
---

You are in **EXPLORE-FIRST MODE**. Your job is to build complete context before writing any code.

## RULES

1. **NO IMPLEMENTATION YET** - Do not write, edit, or modify any files until exploration is complete.
2. **BE AGGRESSIVE** - Explore MORE files than you think necessary. When in doubt, read it.
3. **TREE FIRST** - Start with directory structure to understand the landscape.

## EXPLORATION SEQUENCE

### Step 1: Directory Trees

Run `ls -la` and `find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.next/*'` to map the full project structure.

### Step 2: Related File Discovery

For the topic "$ARGUMENTS", search broadly:

- Glob for potentially related filenames (be generous with patterns)
- Grep for keywords, function names, type names
- Check imports/exports to find connected files
- Look in test files for usage examples
- Read config files that might affect behavior

### Step 3: Deep Read

Read ALL potentially related files, not just the obvious ones. Include:

- Direct matches
- Files that import/export to direct matches
- Similar features for pattern reference
- Type definitions and interfaces
- Test files showing expected behavior
- Any file you're even 20% unsure about

### Step 4: Pattern Summary

After exploring, summarize:

- **Files involved**: List every relevant file with 1-line description
- **Existing patterns**: How similar things are done in this codebase
- **Key types/interfaces**: Core data structures
- **Dependencies**: What this feature touches
- **Test coverage**: Existing tests that relate

## ANTI-PATTERNS TO AVOID

- "I'll just check the main file" - NO. Check everything adjacent.
- "I'm not sure if this is related" - READ IT ANYWAY.
- "I already know how to do this" - VERIFY against this codebase's patterns.
- Stopping exploration early to start coding.

## OUTPUT

After exploration, present your findings and ask: "Ready to proceed with implementation, or should I explore any area deeper?"

---

**Topic to explore:** $ARGUMENTS
