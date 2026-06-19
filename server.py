import os
from typing import Optional
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Universal Software Support", host="0.0.0.0", port=port)

# Simulates an internal licensing/deployment system
CLIENT_VERSIONS = {
    "acme corp": {
        "account_name": "Acme Corp",
        "product": "UniSoft Platform",
        "version": "4.2.1",
        "environment": "production",
        "last_updated": "2026-05-10",
        "license_tier": "Enterprise",
        "license_expiry": "2027-03-31",
    },
    "globex": {
        "account_name": "Globex",
        "product": "UniSoft Platform",
        "version": "4.1.0",
        "environment": "production",
        "last_updated": "2026-02-18",
        "license_tier": "Professional",
        "license_expiry": "2026-12-31",
    },
    "initech": {
        "account_name": "Initech",
        "product": "UniSoft Platform",
        "version": "3.9.5",
        "environment": "staging",
        "last_updated": "2025-11-02",
        "license_tier": "Starter",
        "license_expiry": "2026-09-15",
    },
    "umbrella corp": {
        "account_name": "Umbrella Corp",
        "product": "UniSoft Platform",
        "version": "4.2.1",
        "environment": "production",
        "last_updated": "2026-06-01",
        "license_tier": "Enterprise",
        "license_expiry": "2028-01-01",
    },
}

# Simulates a GitHub/Jira bug tracker
BUGS_BY_VERSION = {
    "4.2.1": [
        {
            "id": "BUG-1042",
            "title": "SSO login fails when session token expires after 8h",
            "severity": "critical",
            "status": "open",
            "reported_date": "2026-06-10",
            "affected_module": "Authentication",
        },
        {
            "id": "BUG-1055",
            "title": "Export to CSV truncates rows above 10,000 records",
            "severity": "high",
            "status": "in_progress",
            "reported_date": "2026-06-14",
            "affected_module": "Data Export",
        },
    ],
    "4.1.0": [
        {
            "id": "BUG-987",
            "title": "Dashboard charts do not render in Safari 17",
            "severity": "high",
            "status": "open",
            "reported_date": "2026-04-22",
            "affected_module": "Dashboard",
        },
        {
            "id": "BUG-1001",
            "title": "Webhook retry logic causes duplicate events on timeout",
            "severity": "critical",
            "status": "open",
            "reported_date": "2026-05-03",
            "affected_module": "Integrations",
        },
    ],
    "3.9.5": [
        {
            "id": "BUG-801",
            "title": "PDF report generation fails for accounts with special characters",
            "severity": "medium",
            "status": "open",
            "reported_date": "2025-10-15",
            "affected_module": "Reports",
        },
    ],
}


class ClientVersionResult(BaseModel):
    account_name: str
    product: str
    version: str
    environment: str
    last_updated: str
    license_tier: str
    license_expiry: str
    error: Optional[str] = None


class BugItem(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    reported_date: str
    affected_module: str


class OpenBugsResult(BaseModel):
    version: str
    total_open: int
    bugs: list[BugItem]
    message: Optional[str] = None


@mcp.tool()
def get_client_version(account_name: str) -> ClientVersionResult:
    """
    Returns the installed product version and license details for a given client account.
    Use this before a support call to know exactly what version the client is running.
    """
    key = account_name.strip().lower()
    client = CLIENT_VERSIONS.get(key)
    if not client:
        return ClientVersionResult(
            account_name=account_name,
            product="",
            version="",
            environment="",
            last_updated="",
            license_tier="",
            license_expiry="",
            error=f"No deployment record found for account '{account_name}'",
        )
    return ClientVersionResult(**client)


@mcp.tool()
def get_open_bugs(version: str) -> OpenBugsResult:
    """
    Returns open and in-progress bugs for a given product version.
    Use this to understand known issues before talking to a client on that version.
    """
    bugs = BUGS_BY_VERSION.get(version.strip())
    if bugs is None:
        return OpenBugsResult(version=version, total_open=0, bugs=[], message="No known issues for this version.")
    return OpenBugsResult(
        version=version,
        total_open=len(bugs),
        bugs=[BugItem(**b) for b in bugs],
    )


app = mcp.streamable_http_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
