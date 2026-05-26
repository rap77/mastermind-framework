---
name: ship-executor
description: Legacy placeholder. Shipping is no longer part of the active objective lifecycle.
model: inherit
permissionMode: askIfDestructive
tools: Read
---

`ship-executor` is retained only as a compatibility placeholder.

The active lifecycle is:

```text
discover roadmap
→ activate next objective
→ contract-check
→ complete-task
→ archive-objective
```

Do not create tags, recreate root `tasks/`, or archive objective work through
the old shipping flow.
