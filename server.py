import os
from typing import Optional
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

port = int(os.environ.get("PORT", 8000))
mcp = FastMCP("Employee Directory", host="0.0.0.0", port=port)

EMPLOYEES = {
    "E001": {
        "name": "Alice Johnson",
        "age": 32,
        "phone": "+1-555-0101",
        "joining_date": "2020-03-15",
        "employment_type": "Full-time",
        "office_location_city": "New York",
    },
    "E002": {
        "name": "Bob Smith",
        "age": 45,
        "phone": "+1-555-0202",
        "joining_date": "2015-07-01",
        "employment_type": "Full-time",
        "office_location_city": "San Francisco",
    },
    "E003": {
        "name": "Carol Davis",
        "age": 28,
        "phone": "+1-555-0303",
        "joining_date": "2023-01-10",
        "employment_type": "Contract",
        "office_location_city": "Austin",
    },
}


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


BUGS_BY_VERSION = {
    "4.2.1": [
        BugItem(id="BUG-1042", title="SSO login fails when session token expires after 8h", severity="critical", status="open", reported_date="2026-06-10", affected_module="Authentication"),
        BugItem(id="BUG-1055", title="Export to CSV truncates rows above 10,000 records", severity="high", status="in_progress", reported_date="2026-06-14", affected_module="Data Export"),
    ],
    "4.1.0": [
        BugItem(id="BUG-987", title="Dashboard charts do not render in Safari 17", severity="high", status="open", reported_date="2026-04-22", affected_module="Dashboard"),
        BugItem(id="BUG-1001", title="Webhook retry logic causes duplicate events on timeout", severity="critical", status="open", reported_date="2026-05-03", affected_module="Integrations"),
    ],
    "3.9.5": [
        BugItem(id="BUG-801", title="PDF report generation fails for accounts with special characters", severity="medium", status="open", reported_date="2025-10-15", affected_module="Reports"),
    ],
}


class EmployeeResult(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    joining_date: Optional[str] = None
    employment_type: Optional[str] = None
    office_location_city: Optional[str] = None
    error: Optional[str] = None


@mcp.tool(structured_output=True)
def get_employee(employee_id: str) -> EmployeeResult:
    """Get employee details by employee ID."""
    employee = EMPLOYEES.get(employee_id.upper())
    if not employee:
        return EmployeeResult(error=f"No employee found with ID '{employee_id}'")
    return EmployeeResult(**employee)


@mcp.tool(structured_output=True)
def get_open_bugs(version: str) -> OpenBugsResult:
    """Returns open and in-progress bugs for a given product version. Use this to understand known issues before talking to a client on that version."""
    bugs = BUGS_BY_VERSION.get(version.strip())
    if bugs is None:
        return OpenBugsResult(version=version, total_open=0, bugs=[], message="No known issues for this version.")
    return OpenBugsResult(version=version, total_open=len(bugs), bugs=bugs)


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
