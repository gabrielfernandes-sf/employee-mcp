import os
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

@mcp.tool()
def get_employee(employee_id: str) -> dict:
    """Get employee details by employee ID."""
    employee = EMPLOYEES.get(employee_id.upper())
    if not employee:
        return {"error": f"No employee found with ID '{employee_id}'"}
    return employee

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
