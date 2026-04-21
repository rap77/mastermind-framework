# Code Review Rules - MasterMind Framework

## Python Code Standards

### Package Managers (STRICT)
- **Python:** Always use `uv` - NEVER pip, poetry, or conda
- **Node.js:** Always use `pnpm` - NEVER npm or yarn

```bash
# Python commands
uv run <script>        # Execute scripts
uv add <package>       # Add dependencies
uv sync                # Sync dependencies

# Node.js commands
pnpm install           # Install dependencies
pnpm add <package>     # Add dependencies
pnpm run <script>      # Run scripts
```

### Type Safety
- **All code must pass mypy** with zero errors
- Use `Optional[T]` for types that can be None
- Add return type annotations: `-> None`, `-> T`, `-> dict[str, Any]`
- Specify generic type parameters: `dict[str, Any]` not `dict`

### Testing
- **TDD is enabled** - Write tests before code
- Target 70%+ minimum coverage for new code
- All tests must pass before commit
- Use pytest for Python testing

### Git Workflow
- **NEVER use --no-verify** - All commits must pass hooks
- Conventional commits only
- Never add "Co-Authored-By" to commits
- Test suite must be at 0 failures before closing phases

### Code Quality
- **Ruff linter** must pass with no errors
- **Ruff formatter** must be applied
- No trailing whitespace
- YAML/JSON/TOML files must be valid

### Architecture Principles
- **CONCEPTS > CODE** - Don't code without understanding
- **AI IS A TOOL** - Humans direct, AI executes
- **SOLID FOUNDATIONS** - Design patterns before frameworks
- **AGAINST IMMEDIACY** - No shortcuts, real learning takes time

### File Organization
```
apps/api/
├── mastermind_cli/     # Main CLI code
├── tests/              # Test suite (run from apps/api/)
├── routers/            # FastAPI route handlers
├── services/           # Business logic
└── scripts/            # Development/utility scripts
```

### Forbidden Patterns
- NO hardcoded API keys or secrets
- NO print() statements in production code (use logging)
- NO unused imports (ruff will catch)
- NO commented-out code (remove it)
- NO "TODO" or "FIXME" without creating an issue

### Linting Rules
- Max line length: 88 characters (ruff default)
- Use f-strings for string formatting
- Prefer list comprehensions over map/filter
- Use type hints on all function signatures

### Import Order
1. Standard library imports
2. Third-party imports
3. Local application imports
4. Each group separated by blank line

## Error Handling

- **Never swallow exceptions silently**
- Log errors with context (structlog preferred)
- Use specific exception types, not generic Exception
- Validate user input at API boundaries

## Security

- All user input must be validated
- SQL queries must use parameterization (never string concatenation)
- Secrets must be in environment variables, never in code
- External data sources treated as untrusted

## Performance

- No N+1 query patterns
- Use async/await for I/O operations
- Pagination required on list endpoints
- Cache expensive operations when appropriate
