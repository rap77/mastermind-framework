"""
MM-Flow Configuration
Backend limits, token management, and multi-project settings.
"""

from dataclasses import dataclass
from typing import Dict

# ============================================================================
# BACKEND CONFIGURATION
# ============================================================================


@dataclass
class BackendConfig:
    """Backend capability specification."""

    name: str
    token_limit: int
    tokens_per_minute: int
    requests_per_day: int
    reset_cycles_per_day: int
    reset_cycle_hours: float

    @property
    def hours_between_resets(self) -> float:
        """Hours between each reset cycle."""
        return 24.0 / self.reset_cycles_per_day


# Discovered limits (via testing in Phase B, Apr 22-26)
# For now: conservative estimates based on public docs
BACKENDS: Dict[str, BackendConfig] = {
    "claude": BackendConfig(
        name="Claude (Anthropic)",
        token_limit=100_000,  # Conservative; actual may be 200K+ with rate limits
        tokens_per_minute=50_000,
        requests_per_day=10_000,
        reset_cycles_per_day=1,
        reset_cycle_hours=24.0,
    ),
    "openrouter": BackendConfig(
        name="OpenRouter (Multi-model)",
        token_limit=128_000,  # Conservative for routing
        tokens_per_minute=40_000,
        requests_per_day=5_000,
        reset_cycles_per_day=1,
        reset_cycle_hours=24.0,
    ),
    "z_ai": BackendConfig(
        name="z.ai (Fast inference)",
        token_limit=200_000,  # Highest limit
        tokens_per_minute=100_000,  # Fast
        requests_per_day=20_000,  # High throughput
        reset_cycles_per_day=5,  # STRATEGIC: 5 resets/day (~every 4h48m)
        reset_cycle_hours=4.8,  # 24 / 5
    ),
}

# Backend priority (for fallback when current backend depletes)
BACKEND_PRIORITY: list[str] = [
    "z_ai",  # Try z.ai first (most resets, best for long workflows)
    "openrouter",  # Fallback to OpenRouter
    "claude",  # Last resort Claude (slowest reset)
]

# ============================================================================
# ENVIRONMENT VARIABLE MAPPING
# ============================================================================

ENV_VAR_NAMES: Dict[str, str] = {
    "claude": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "z_ai": "ZAI_API_KEY",
}

# ============================================================================
# POSTGRESQL CONFIGURATION
# ============================================================================


@dataclass
class PostgreSQLConfig:
    """PostgreSQL connection details."""

    host: str = "localhost"
    port: int = 5433
    database: str = "mastermind_bd"
    user: str = "postgres"
    password: str = "devpassword"

    @property
    def connection_string(self) -> str:
        """PostgreSQL connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


# Default PostgreSQL (used in Phase A)
POSTGRES_LOCAL = PostgreSQLConfig(
    host="localhost",
    port=5433,
    database="mastermind_bd",
    user="postgres",
    password="devpassword",
)

# ============================================================================
# MULTI-PROJECT SETUP
# ============================================================================

CURRENT_PROJECTS = {
    "RAP-software": {
        "slug": "RAP-software",
        "name": "RAP Software",
        "projects": {
            "mastermind": {
                "name": "MasterMind Framework",
                "type": "software",
            }
        },
    },
    "Prosell-CA": {
        "slug": "Prosell-CA",
        "name": "Prosell C.A.",
        "projects": {
            "prosell-ecommerce": {
                "name": "Prosell E-Commerce Platform (Multi-nicho)",
                "type": "saas",
                "features": [
                    "scraping",
                    "price-evaluation",
                    "market-analysis",
                    "multi-niche",
                ],
            }
        },
    },
}

# Prepared for future expansion (3-4 more projects)
FUTURE_PROJECTS = {
    "project-3": {
        "organization": "unknown",
        "created": False,
    },
    "project-4": {
        "organization": "unknown",
        "created": False,
    },
}

# ============================================================================
# MM-FLOW PHASE ROUTING (which brains are consulted)
# ============================================================================

PHASE_BRAIN_ROUTING = {
    "DISCUSSION": [1, 2, 3, 7],  # Product, UX, UI + Evaluator
    "PLANNING": [4, 5, 6, 7],  # Frontend, Backend, QA + Evaluator
    "EXECUTION": [7],  # Evaluator only (fast verification)
    "VERIFICATION": [7],  # Cross-phase contracts validation
}

# ============================================================================
# TOKEN LIMITS AND SAFEGUARDS
# ============================================================================

MIN_TOKENS_FOR_SWITCH = 5_000  # Switch backends when < 5K tokens available
CONTEXT_CHECKPOINT_INTERVAL = 10_000  # Save state every 10K tokens used
MAX_ITERATIONS_PER_PHASE = 3  # Phase can retry up to 3x before escalating

# ============================================================================
# NICHE-SPECIFIC METRICS (Audit Trail)
# ============================================================================

NICHE_METRICS = {
    "software": {
        "description": "Software development (MasterMind, Paperclip, etc)",
        "metrics": [
            {
                "name": "test_coverage",
                "unit": "%",
                "target": 80,
                "weight": 0.3,
                "description": "Code coverage percentage",
            },
            {
                "name": "code_review_time",
                "unit": "hours",
                "target": 24,
                "weight": 0.2,
                "description": "Average time to complete code review",
            },
            {
                "name": "cyclomatic_complexity",
                "unit": "score",
                "target": 10,
                "weight": 0.2,
                "description": "Average McCabe complexity per function",
            },
            {
                "name": "security_vulnerabilities",
                "unit": "count",
                "target": 0,
                "weight": 0.3,
                "description": "Number of known vulnerabilities (critical+high)",
            },
        ],
    },
    "saas": {
        "description": "SaaS/Web applications (Prosell, etc)",
        "metrics": [
            {
                "name": "deployment_success_rate",
                "unit": "%",
                "target": 99,
                "weight": 0.3,
                "description": "Percentage of successful deployments",
            },
            {
                "name": "uptime",
                "unit": "%",
                "target": 99.9,
                "weight": 0.4,
                "description": "Service availability percentage",
            },
            {
                "name": "mrr_impact",
                "unit": "$",
                "target": 5000,
                "weight": 0.3,
                "description": "Monthly Recurring Revenue impact",
            },
        ],
    },
    "hardware": {
        "description": "Hardware/IoT products",
        "metrics": [
            {
                "name": "manufacturing_yield",
                "unit": "%",
                "target": 95,
                "weight": 0.4,
                "description": "Percentage of units passing QA",
            },
            {
                "name": "defect_rate",
                "unit": "ppm",
                "target": 100,
                "weight": 0.3,
                "description": "Defects per million units",
            },
            {
                "name": "time_to_production",
                "unit": "weeks",
                "target": 8,
                "weight": 0.3,
                "description": "Weeks from design to manufacturing",
            },
        ],
    },
}

# ============================================================================
# AUDIT TRAIL CONFIGURATION
# ============================================================================

# Maximum retries for verification gates before escalation
MAX_GATE_RETRIES = 1

# Email or Slack notification on gate failures
GATE_FAILURE_NOTIFICATION_ENABLED = False
GATE_FAILURE_NOTIFICATION_CHANNEL = "#mm-flow-alerts"

# Engram sync settings
ENGRAM_SYNC_ENABLED = True
ENGRAM_SYNC_BATCH_SIZE = 100  # Sync up to 100 decisions per batch
ENGRAM_SYNC_ON_PHASE_COMPLETION = True  # Auto-sync at phase end
