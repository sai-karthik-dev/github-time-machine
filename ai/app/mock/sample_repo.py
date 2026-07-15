"""
Realistic mock data for a sample repository.

This simulates a Python web application ("atlas") with:
- ~20 files across src/auth, src/api, src/models, src/services, src/utils
- ~30 functions with varying complexity
- ~50 commits with realistic messages and patterns
- Edges: CALLS, DEPENDS_ON, MODIFIES, AUTHORED_BY
- Debt scores per file

This data is rich enough to produce meaningful AI responses
without needing a real repository.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from app.models.repository import Repository, File, Function, Commit, Edge, EdgeType, Language
from app.models.heatmap import DebtScore

# ── Helper ──────────────────────────────────────────────────────────────

_BASE = datetime(2024, 1, 15, 10, 0, 0)


def _dt(days: int, hours: int = 0) -> datetime:
    return _BASE + timedelta(days=days, hours=hours)


# ── Repository ──────────────────────────────────────────────────────────

MOCK_REPO = Repository(
    id="demo",
    name="atlas",
    full_name="octo-labs/atlas",
    description="Internal platform API — handles auth, billing, and team management",
    default_branch="main",
    language="Python",
    total_commits=52,
    total_files=18,
    created_at=_dt(0),
    analyzed_at=_dt(180),
)

# ── Files ───────────────────────────────────────────────────────────────

MOCK_FILES: list[File] = [
    # Auth module
    File(id="f01", repo_id="demo", path="src/auth/__init__.py", language=Language.PYTHON, size_bytes=120, line_count=8, last_modified=_dt(170), complexity_score=5.0),
    File(id="f02", repo_id="demo", path="src/auth/oauth.py", language=Language.PYTHON, size_bytes=4800, line_count=142, last_modified=_dt(175), complexity_score=68.0),
    File(id="f03", repo_id="demo", path="src/auth/middleware.py", language=Language.PYTHON, size_bytes=2200, line_count=78, last_modified=_dt(160), complexity_score=42.0),
    File(id="f04", repo_id="demo", path="src/auth/tokens.py", language=Language.PYTHON, size_bytes=1900, line_count=65, last_modified=_dt(155), complexity_score=35.0),

    # API module
    File(id="f05", repo_id="demo", path="src/api/__init__.py", language=Language.PYTHON, size_bytes=90, line_count=5, last_modified=_dt(30), complexity_score=2.0),
    File(id="f06", repo_id="demo", path="src/api/routes.py", language=Language.PYTHON, size_bytes=6200, line_count=210, last_modified=_dt(178), complexity_score=55.0),
    File(id="f07", repo_id="demo", path="src/api/middleware.py", language=Language.PYTHON, size_bytes=1800, line_count=62, last_modified=_dt(140), complexity_score=30.0),
    File(id="f08", repo_id="demo", path="src/api/schemas.py", language=Language.PYTHON, size_bytes=3500, line_count=120, last_modified=_dt(165), complexity_score=18.0),

    # Models
    File(id="f09", repo_id="demo", path="src/models/user.py", language=Language.PYTHON, size_bytes=2100, line_count=85, last_modified=_dt(150), complexity_score=22.0),
    File(id="f10", repo_id="demo", path="src/models/team.py", language=Language.PYTHON, size_bytes=1600, line_count=58, last_modified=_dt(120), complexity_score=15.0),
    File(id="f11", repo_id="demo", path="src/models/billing.py", language=Language.PYTHON, size_bytes=3800, line_count=130, last_modified=_dt(172), complexity_score=62.0),

    # Services
    File(id="f12", repo_id="demo", path="src/services/billing_service.py", language=Language.PYTHON, size_bytes=5200, line_count=185, last_modified=_dt(176), complexity_score=72.0),
    File(id="f13", repo_id="demo", path="src/services/team_service.py", language=Language.PYTHON, size_bytes=2800, line_count=95, last_modified=_dt(145), complexity_score=38.0),
    File(id="f14", repo_id="demo", path="src/services/notification_service.py", language=Language.PYTHON, size_bytes=2400, line_count=82, last_modified=_dt(130), complexity_score=28.0),

    # Utils
    File(id="f15", repo_id="demo", path="src/utils/helpers.py", language=Language.PYTHON, size_bytes=1500, line_count=55, last_modified=_dt(90), complexity_score=12.0),
    File(id="f16", repo_id="demo", path="src/utils/validators.py", language=Language.PYTHON, size_bytes=1800, line_count=68, last_modified=_dt(110), complexity_score=20.0),

    # Config & entry
    File(id="f17", repo_id="demo", path="src/config.py", language=Language.PYTHON, size_bytes=900, line_count=35, last_modified=_dt(60), complexity_score=8.0),
    File(id="f18", repo_id="demo", path="src/main.py", language=Language.PYTHON, size_bytes=1100, line_count=42, last_modified=_dt(168), complexity_score=10.0),
]

# ── Functions ───────────────────────────────────────────────────────────

MOCK_FUNCTIONS: list[Function] = [
    # Auth
    Function(id="fn01", file_id="f02", repo_id="demo", name="authenticate", signature="async def authenticate(request: Request) -> User", start_line=15, end_line=48, complexity=18.0, is_exported=True),
    Function(id="fn02", file_id="f02", repo_id="demo", name="refresh_token", signature="async def refresh_token(token: str) -> TokenPair", start_line=50, end_line=82, complexity=14.0, is_exported=True),
    Function(id="fn03", file_id="f02", repo_id="demo", name="revoke_session", signature="async def revoke_session(session_id: str) -> bool", start_line=84, end_line=105, complexity=8.0, is_exported=True),
    Function(id="fn04", file_id="f02", repo_id="demo", name="_validate_github_token", signature="async def _validate_github_token(code: str) -> dict", start_line=107, end_line=142, complexity=22.0, is_exported=False),
    Function(id="fn05", file_id="f03", repo_id="demo", name="auth_middleware", signature="async def auth_middleware(request: Request, call_next)", start_line=10, end_line=45, complexity=15.0, is_exported=True),
    Function(id="fn06", file_id="f04", repo_id="demo", name="create_jwt", signature="def create_jwt(user_id: str, scopes: list[str]) -> str", start_line=8, end_line=30, complexity=6.0, is_exported=True),
    Function(id="fn07", file_id="f04", repo_id="demo", name="decode_jwt", signature="def decode_jwt(token: str) -> dict", start_line=32, end_line=55, complexity=10.0, is_exported=True),

    # API
    Function(id="fn08", file_id="f06", repo_id="demo", name="create_user", signature="async def create_user(data: UserCreate) -> UserResponse", start_line=20, end_line=55, complexity=12.0, is_exported=True),
    Function(id="fn09", file_id="f06", repo_id="demo", name="update_billing", signature="async def update_billing(user_id: str, plan: BillingPlan) -> BillingResponse", start_line=57, end_line=98, complexity=20.0, is_exported=True),
    Function(id="fn10", file_id="f06", repo_id="demo", name="list_team_members", signature="async def list_team_members(team_id: str) -> list[UserResponse]", start_line=100, end_line=130, complexity=8.0, is_exported=True),
    Function(id="fn11", file_id="f06", repo_id="demo", name="webhook_handler", signature="async def webhook_handler(event: WebhookEvent) -> dict", start_line=132, end_line=185, complexity=25.0, is_exported=True),
    Function(id="fn12", file_id="f06", repo_id="demo", name="_rate_limit_check", signature="async def _rate_limit_check(request: Request) -> None", start_line=187, end_line=210, complexity=10.0, is_exported=False),

    # Models
    Function(id="fn13", file_id="f09", repo_id="demo", name="User.__init__", signature="def __init__(self, email: str, name: str, github_id: str)", start_line=10, end_line=25, complexity=3.0, is_exported=True),
    Function(id="fn14", file_id="f11", repo_id="demo", name="BillingAccount.process_payment", signature="async def process_payment(self, amount: Decimal, currency: str) -> PaymentResult", start_line=45, end_line=95, complexity=28.0, is_exported=True),
    Function(id="fn15", file_id="f11", repo_id="demo", name="BillingAccount.calculate_usage", signature="def calculate_usage(self, period: DateRange) -> UsageReport", start_line=97, end_line=130, complexity=18.0, is_exported=True),

    # Services
    Function(id="fn16", file_id="f12", repo_id="demo", name="BillingService.create_subscription", signature="async def create_subscription(self, user_id: str, plan: str) -> Subscription", start_line=20, end_line=65, complexity=22.0, is_exported=True),
    Function(id="fn17", file_id="f12", repo_id="demo", name="BillingService.cancel_subscription", signature="async def cancel_subscription(self, sub_id: str) -> bool", start_line=67, end_line=95, complexity=15.0, is_exported=True),
    Function(id="fn18", file_id="f12", repo_id="demo", name="BillingService.process_webhook", signature="async def process_webhook(self, event: StripeEvent) -> None", start_line=97, end_line=145, complexity=30.0, is_exported=True),
    Function(id="fn19", file_id="f12", repo_id="demo", name="BillingService._sync_with_stripe", signature="async def _sync_with_stripe(self, account: BillingAccount) -> None", start_line=147, end_line=185, complexity=20.0, is_exported=False),
    Function(id="fn20", file_id="f13", repo_id="demo", name="TeamService.add_member", signature="async def add_member(self, team_id: str, user_id: str, role: str) -> TeamMember", start_line=15, end_line=50, complexity=12.0, is_exported=True),
    Function(id="fn21", file_id="f14", repo_id="demo", name="send_notification", signature="async def send_notification(user_id: str, template: str, context: dict) -> bool", start_line=10, end_line=45, complexity=8.0, is_exported=True),

    # Utils
    Function(id="fn22", file_id="f15", repo_id="demo", name="retry_with_backoff", signature="async def retry_with_backoff(fn, max_retries: int = 3)", start_line=5, end_line=25, complexity=8.0, is_exported=True),
    Function(id="fn23", file_id="f16", repo_id="demo", name="validate_email", signature="def validate_email(email: str) -> bool", start_line=5, end_line=20, complexity=5.0, is_exported=True),
]

# ── Commits ─────────────────────────────────────────────────────────────

MOCK_COMMITS: list[Commit] = [
    # Initial setup
    Commit(id="c01", repo_id="demo", sha="a1b2c3d4e5f6", message="Initial project scaffold with FastAPI", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(0), files_changed=8, additions=450, deletions=0),
    Commit(id="c02", repo_id="demo", sha="b2c3d4e5f6a7", message="Add user model and basic auth flow", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(3), files_changed=4, additions=280, deletions=10),
    Commit(id="c03", repo_id="demo", sha="c3d4e5f6a7b8", message="Implement GitHub OAuth authentication", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(5), files_changed=3, additions=190, deletions=20),

    # Auth evolution
    Commit(id="c04", repo_id="demo", sha="d4e5f6a7b8c9", message="Add JWT token creation and validation", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(7), files_changed=2, additions=120, deletions=5),
    Commit(id="c05", repo_id="demo", sha="e5f6a7b8c9d0", message="Add auth middleware for request authentication", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(10), files_changed=2, additions=85, deletions=0),
    Commit(id="c06", repo_id="demo", sha="f6a7b8c9d0e1", message="Fix auth token expiry not being checked correctly", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(14), files_changed=1, additions=15, deletions=8, is_fix_commit=True),

    # API routes
    Commit(id="c07", repo_id="demo", sha="a7b8c9d0e1f2", message="Add CRUD API routes for user management", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(18), files_changed=3, additions=210, deletions=30),
    Commit(id="c08", repo_id="demo", sha="b8c9d0e1f2a3", message="Add API schemas with Pydantic validation", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(20), files_changed=1, additions=120, deletions=0),

    # Billing — the big feature
    Commit(id="c09", repo_id="demo", sha="c9d0e1f2a3b4", message="Add billing model — initial Stripe integration design", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(30), files_changed=2, additions=180, deletions=0),
    Commit(id="c10", repo_id="demo", sha="d0e1f2a3b4c5", message="Implement billing service with subscription management", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(35), files_changed=3, additions=250, deletions=15),
    Commit(id="c11", repo_id="demo", sha="e1f2a3b4c5d6", message="Add Stripe webhook handler for payment events", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(38), files_changed=2, additions=140, deletions=20),
    Commit(id="c12", repo_id="demo", sha="f2a3b4c5d6e7", message="Fix billing webhook signature verification failing in prod", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(42), files_changed=1, additions=25, deletions=12, is_fix_commit=True),
    Commit(id="c13", repo_id="demo", sha="a3b4c5d6e7f8", message="Fix race condition in concurrent subscription updates", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(45), files_changed=2, additions=40, deletions=18, is_fix_commit=True),

    # Team management
    Commit(id="c14", repo_id="demo", sha="b4c5d6e7f8a9", message="Add team model and team service", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(50), files_changed=3, additions=180, deletions=0),
    Commit(id="c15", repo_id="demo", sha="c5d6e7f8a9b0", message="Add team member management API endpoints", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(53), files_changed=2, additions=90, deletions=10),

    # Auth rework — the important architectural decision
    Commit(id="c16", repo_id="demo", sha="d6e7f8a9b0c1", message="Refactor: separate auth boundary to isolate billing concerns", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(60), files_changed=6, additions=180, deletions=120),
    Commit(id="c17", repo_id="demo", sha="e7f8a9b0c1d2", message="Move token validation into dedicated tokens.py module", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(62), files_changed=3, additions=65, deletions=55),

    # Notification service
    Commit(id="c18", repo_id="demo", sha="f8a9b0c1d2e3", message="Add notification service for email and in-app alerts", author_name="Anmol", author_email="anmol@octo-labs.dev", timestamp=_dt(70), files_changed=2, additions=100, deletions=0),
    Commit(id="c19", repo_id="demo", sha="a9b0c1d2e3f4", message="Fix notification template rendering with missing context", author_name="Anmol", author_email="anmol@octo-labs.dev", timestamp=_dt(75), files_changed=1, additions=12, deletions=5, is_fix_commit=True),

    # Utils
    Commit(id="c20", repo_id="demo", sha="b0c1d2e3f4a5", message="Add retry_with_backoff utility for external API calls", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(80), files_changed=1, additions=55, deletions=0),
    Commit(id="c21", repo_id="demo", sha="c1d2e3f4a5b6", message="Add email and input validators", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(85), files_changed=1, additions=68, deletions=0),

    # Rate limiting
    Commit(id="c22", repo_id="demo", sha="d2e3f4a5b6c7", message="Add rate limiting middleware to API routes", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(95), files_changed=2, additions=75, deletions=10),

    # More billing fixes — showing pattern of instability
    Commit(id="c23", repo_id="demo", sha="e3f4a5b6c7d8", message="Fix billing calculation rounding error for annual plans", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(100), files_changed=2, additions=30, deletions=15, is_fix_commit=True),
    Commit(id="c24", repo_id="demo", sha="f4a5b6c7d8e9", message="Patch: billing service not handling currency conversion edge case", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(105), files_changed=1, additions=20, deletions=8, is_fix_commit=True),
    Commit(id="c25", repo_id="demo", sha="a5b6c7d8e9f0", message="Hotfix: Stripe API timeout not caught in process_webhook", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(108), files_changed=1, additions=15, deletions=3, is_fix_commit=True),

    # More features
    Commit(id="c26", repo_id="demo", sha="b6c7d8e9f0a1", message="Add usage-based billing calculation method", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(115), files_changed=2, additions=85, deletions=10),
    Commit(id="c27", repo_id="demo", sha="c7d8e9f0a1b2", message="Add API endpoint for team billing dashboard", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(120), files_changed=2, additions=60, deletions=5),

    # Auth session management
    Commit(id="c28", repo_id="demo", sha="d8e9f0a1b2c3", message="Add session revocation and multi-device support", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(125), files_changed=2, additions=70, deletions=15),

    # Security fixes
    Commit(id="c29", repo_id="demo", sha="e9f0a1b2c3d4", message="Fix: auth middleware not rejecting expired refresh tokens", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(132), files_changed=2, additions=25, deletions=10, is_fix_commit=True),
    Commit(id="c30", repo_id="demo", sha="f0a1b2c3d4e5", message="Security: add CSRF protection to OAuth callback", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(135), files_changed=1, additions=35, deletions=5),

    # Performance
    Commit(id="c31", repo_id="demo", sha="a1b2c3d4e5f7", message="Optimize user query with database indexes", author_name="Vijay", author_email="vijay@octo-labs.dev", timestamp=_dt(140), files_changed=2, additions=30, deletions=10),
    Commit(id="c32", repo_id="demo", sha="b2c3d4e5f7a8", message="Add connection pooling for database queries", author_name="Vijay", author_email="vijay@octo-labs.dev", timestamp=_dt(142), files_changed=1, additions=25, deletions=8),

    # More billing work
    Commit(id="c33", repo_id="demo", sha="c3d4e5f7a8b9", message="Refactor billing service to use strategy pattern for payment providers", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(148), files_changed=3, additions=120, deletions=80),
    Commit(id="c34", repo_id="demo", sha="d4e5f7a8b9c0", message="Add PayPal as alternative payment provider", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(152), files_changed=2, additions=95, deletions=5),

    # Auth changes
    Commit(id="c35", repo_id="demo", sha="e5f7a8b9c0d1", message="Add scope-based permission checks to auth middleware", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(155), files_changed=3, additions=60, deletions=20),
    Commit(id="c36", repo_id="demo", sha="f7a8b9c0d1e2", message="Fix auth scope validation not matching wildcard patterns", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(158), files_changed=1, additions=18, deletions=8, is_fix_commit=True),

    # Schema updates
    Commit(id="c37", repo_id="demo", sha="a8b9c0d1e2f3", message="Update API schemas for v2 billing endpoints", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(162), files_changed=1, additions=45, deletions=20),
    Commit(id="c38", repo_id="demo", sha="b9c0d1e2f3a4", message="Add webhook event schema validation", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(165), files_changed=2, additions=55, deletions=10),

    # Main app updates
    Commit(id="c39", repo_id="demo", sha="c0d1e2f3a4b5", message="Update main.py startup to initialize all services", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(168), files_changed=1, additions=20, deletions=8),

    # Recent billing fixes (showing ongoing instability)
    Commit(id="c40", repo_id="demo", sha="d1e2f3a4b5c6", message="Fix billing model decimal precision for micro-transactions", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(170), files_changed=2, additions=22, deletions=10, is_fix_commit=True),
    Commit(id="c41", repo_id="demo", sha="e2f3a4b5c6d7", message="Bug fix: billing service double-charging on retry", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(172), files_changed=1, additions=30, deletions=12, is_fix_commit=True),

    # Auth final touches
    Commit(id="c42", repo_id="demo", sha="f3a4b5c6d7e8", message="Add OAuth token refresh with sliding window expiry", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(174), files_changed=2, additions=40, deletions=15),
    Commit(id="c43", repo_id="demo", sha="a4b5c6d7e8f9", message="Improve auth error messages for better debugging", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(175), files_changed=1, additions=20, deletions=10),

    # Billing service hardening
    Commit(id="c44", repo_id="demo", sha="b5c6d7e8f9a0", message="Add idempotency keys to billing service to prevent duplicates", author_name="Foysal", author_email="foysal@octo-labs.dev", timestamp=_dt(176), files_changed=1, additions=45, deletions=10),

    # Recent API work
    Commit(id="c45", repo_id="demo", sha="c6d7e8f9a0b1", message="Add pagination to list endpoints in API routes", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(177), files_changed=1, additions=35, deletions=15),
    Commit(id="c46", repo_id="demo", sha="d7e8f9a0b1c2", message="Fix API rate limiter not resetting counter after window", author_name="Fernando", author_email="fernando@octo-labs.dev", timestamp=_dt(178), files_changed=1, additions=12, deletions=5, is_fix_commit=True),

    # Documentation
    Commit(id="c47", repo_id="demo", sha="e8f9a0b1c2d3", message="Add docstrings to all public API functions", author_name="Sai Karthik", author_email="sai@octo-labs.dev", timestamp=_dt(179), files_changed=4, additions=80, deletions=5),

    # Latest
    Commit(id="c48", repo_id="demo", sha="f9a0b1c2d3e4", message="Update dependencies and fix deprecation warnings", author_name="Vijay", author_email="vijay@octo-labs.dev", timestamp=_dt(180), files_changed=2, additions=15, deletions=15),
]

# ── Edges ───────────────────────────────────────────────────────────────

MOCK_EDGES: list[Edge] = [
    # Auth dependencies
    Edge(id="e01", repo_id="demo", source_id="f02", target_id="f04", edge_type=EdgeType.DEPENDS_ON, weight=0.9),  # oauth → tokens
    Edge(id="e02", repo_id="demo", source_id="f03", target_id="f02", edge_type=EdgeType.CALLS, weight=0.8),  # middleware → oauth
    Edge(id="e03", repo_id="demo", source_id="f03", target_id="f04", edge_type=EdgeType.CALLS, weight=0.7),  # middleware → tokens
    Edge(id="e04", repo_id="demo", source_id="f02", target_id="f09", edge_type=EdgeType.DEPENDS_ON, weight=0.6),  # oauth → user model

    # API dependencies
    Edge(id="e05", repo_id="demo", source_id="f06", target_id="f03", edge_type=EdgeType.DEPENDS_ON, weight=0.9),  # routes → auth middleware
    Edge(id="e06", repo_id="demo", source_id="f06", target_id="f08", edge_type=EdgeType.DEPENDS_ON, weight=0.8),  # routes → schemas
    Edge(id="e07", repo_id="demo", source_id="f06", target_id="f12", edge_type=EdgeType.CALLS, weight=0.7),  # routes → billing service
    Edge(id="e08", repo_id="demo", source_id="f06", target_id="f13", edge_type=EdgeType.CALLS, weight=0.6),  # routes → team service
    Edge(id="e09", repo_id="demo", source_id="f06", target_id="f14", edge_type=EdgeType.CALLS, weight=0.4),  # routes → notification service

    # Service dependencies
    Edge(id="e10", repo_id="demo", source_id="f12", target_id="f11", edge_type=EdgeType.DEPENDS_ON, weight=0.95),  # billing service → billing model
    Edge(id="e11", repo_id="demo", source_id="f12", target_id="f09", edge_type=EdgeType.DEPENDS_ON, weight=0.5),  # billing service → user model
    Edge(id="e12", repo_id="demo", source_id="f12", target_id="f15", edge_type=EdgeType.CALLS, weight=0.3),  # billing service → helpers (retry)
    Edge(id="e13", repo_id="demo", source_id="f13", target_id="f10", edge_type=EdgeType.DEPENDS_ON, weight=0.9),  # team service → team model
    Edge(id="e14", repo_id="demo", source_id="f13", target_id="f09", edge_type=EdgeType.DEPENDS_ON, weight=0.6),  # team service → user model
    Edge(id="e15", repo_id="demo", source_id="f14", target_id="f09", edge_type=EdgeType.DEPENDS_ON, weight=0.4),  # notification → user model

    # Cross-cutting
    Edge(id="e16", repo_id="demo", source_id="f18", target_id="f06", edge_type=EdgeType.CALLS, weight=0.9),  # main → routes
    Edge(id="e17", repo_id="demo", source_id="f18", target_id="f03", edge_type=EdgeType.CALLS, weight=0.8),  # main → auth middleware
    Edge(id="e18", repo_id="demo", source_id="f18", target_id="f17", edge_type=EdgeType.DEPENDS_ON, weight=0.7),  # main → config
    Edge(id="e19", repo_id="demo", source_id="f06", target_id="f16", edge_type=EdgeType.CALLS, weight=0.3),  # routes → validators
    Edge(id="e20", repo_id="demo", source_id="f12", target_id="f14", edge_type=EdgeType.CALLS, weight=0.5),  # billing service → notification

    # Modification relationships (who authored/modified what)
    Edge(id="e21", repo_id="demo", source_id="f02", target_id="c03", edge_type=EdgeType.MODIFIES, weight=1.0, metadata={"author": "Foysal"}),
    Edge(id="e22", repo_id="demo", source_id="f12", target_id="c10", edge_type=EdgeType.MODIFIES, weight=1.0, metadata={"author": "Foysal"}),
    Edge(id="e23", repo_id="demo", source_id="f06", target_id="c07", edge_type=EdgeType.MODIFIES, weight=1.0, metadata={"author": "Fernando"}),
    Edge(id="e24", repo_id="demo", source_id="f11", target_id="c09", edge_type=EdgeType.MODIFIES, weight=1.0, metadata={"author": "Sai Karthik"}),
]

# ── Debt Scores ─────────────────────────────────────────────────────────

MOCK_DEBT_SCORES: list[DebtScore] = [
    # High debt — billing (lots of churn + high complexity + frequent fixes)
    DebtScore(path="src/services/billing_service.py", language="python", churn=14, complexity=72.0, age_days=4, line_count=185, debt_score=88.5, risk_level="high"),
    DebtScore(path="src/models/billing.py", language="python", churn=10, complexity=62.0, age_days=8, line_count=130, debt_score=76.2, risk_level="high"),
    DebtScore(path="src/auth/oauth.py", language="python", churn=12, complexity=68.0, age_days=5, line_count=142, debt_score=82.1, risk_level="high"),

    # Medium debt
    DebtScore(path="src/api/routes.py", language="python", churn=8, complexity=55.0, age_days=2, line_count=210, debt_score=58.3, risk_level="medium"),
    DebtScore(path="src/auth/middleware.py", language="python", churn=6, complexity=42.0, age_days=20, line_count=78, debt_score=45.0, risk_level="medium"),
    DebtScore(path="src/auth/tokens.py", language="python", churn=5, complexity=35.0, age_days=25, line_count=65, debt_score=38.5, risk_level="medium"),
    DebtScore(path="src/api/schemas.py", language="python", churn=4, complexity=18.0, age_days=15, line_count=120, debt_score=22.0, risk_level="medium"),

    # Low debt — stable modules
    DebtScore(path="src/services/team_service.py", language="python", churn=3, complexity=38.0, age_days=35, line_count=95, debt_score=18.5, risk_level="low"),
    DebtScore(path="src/services/notification_service.py", language="python", churn=2, complexity=28.0, age_days=50, line_count=82, debt_score=12.0, risk_level="low"),
    DebtScore(path="src/models/user.py", language="python", churn=3, complexity=22.0, age_days=30, line_count=85, debt_score=14.2, risk_level="low"),
    DebtScore(path="src/models/team.py", language="python", churn=1, complexity=15.0, age_days=60, line_count=58, debt_score=6.0, risk_level="low"),
    DebtScore(path="src/utils/helpers.py", language="python", churn=1, complexity=12.0, age_days=90, line_count=55, debt_score=4.0, risk_level="low"),
    DebtScore(path="src/utils/validators.py", language="python", churn=1, complexity=20.0, age_days=70, line_count=68, debt_score=5.5, risk_level="low"),
    DebtScore(path="src/config.py", language="python", churn=2, complexity=8.0, age_days=120, line_count=35, debt_score=3.0, risk_level="low"),
    DebtScore(path="src/main.py", language="python", churn=3, complexity=10.0, age_days=12, line_count=42, debt_score=8.0, risk_level="low"),
    DebtScore(path="src/api/middleware.py", language="python", churn=2, complexity=30.0, age_days=40, line_count=62, debt_score=15.0, risk_level="low"),
    DebtScore(path="src/auth/__init__.py", language="python", churn=1, complexity=5.0, age_days=10, line_count=8, debt_score=1.5, risk_level="low"),
    DebtScore(path="src/api/__init__.py", language="python", churn=0, complexity=2.0, age_days=150, line_count=5, debt_score=0.5, risk_level="low"),
]
