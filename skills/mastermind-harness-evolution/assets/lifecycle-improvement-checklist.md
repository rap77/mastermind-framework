# MasterMind Harness Improvement Checklist

## Define

- [ ] Name the exact operational gap
- [ ] Identify the narrowest affected lifecycle step
- [ ] State what another model/operator cannot currently infer

## Eval

- [ ] Define one capability eval
- [ ] Define one regression eval
- [ ] Prefer deterministic graders/commands

## Implement

- [ ] Keep `.mm-flow/commands/mm/*.py` as source of truth
- [ ] Prefer warning-first enforcement
- [ ] Surface exact next command in outputs
- [ ] Preserve compatibility with current objective-package flow

## Verify

- [ ] Validate command output for `not-yet-run`
- [ ] Validate command output for `NEEDS_INPUT`
- [ ] Validate command output for `FAILED`
- [ ] Validate command output for `PASSED`
- [ ] Confirm docs/handoff do not suggest bypassing the gate
