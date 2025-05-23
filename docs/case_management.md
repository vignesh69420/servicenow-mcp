# Case Management

This document describes the case management functionality provided by the ServiceNow MCP server.

## Overview

The case management module allows LLMs to interact with ServiceNow Customer Service cases through the Model Context Protocol (MCP). It provides resources for querying case data and tools for creating and updating cases.

## Resources

### List Cases

Retrieves a list of cases from ServiceNow.

**Resource Name:** `cases`

**Parameters:**
- `limit` (int, default: 10): Maximum number of cases to return
- `offset` (int, default: 0): Offset for pagination
- `state` (string, optional): Filter by case state
- `priority` (string, optional): Filter by case priority
- `query` (string, optional): Search query for cases

**Example:**
```python
cases = await mcp.get_resource("servicenow", "cases", {
    "limit": 5,
    "state": "open",
})
for case in cases:
    print(f"{case['number']}: {case['short_description']}")
```

### Get Case

Retrieves a specific case from ServiceNow by ID or number.

**Resource Name:** `case`

**Parameters:**
- `case_id` (string): Case ID or sys_id

**Example:**
```python
case = await mcp.get_resource("servicenow", "case", {"case_id": "CASE0012345"})
print(case)
```

## Tools

### Create Case

Creates a new case in ServiceNow.

**Tool Name:** `create_case`

**Parameters:**
- `short_description` (string, required): Short description of the case
- `description` (string, optional): Detailed description of the case
- `contact` (string, optional): Contact associated with the case
- `account` (string, optional): Account associated with the case
- `priority` (string, optional): Priority of the case
- `state` (string, optional): State of the case
- `assigned_to` (string, optional): User assigned to the case
- `assignment_group` (string, optional): Group assigned to the case

### Update Case

Updates an existing case in ServiceNow.

**Tool Name:** `update_case`

**Parameters:**
- `case_id` (string, required): Case ID or sys_id
- `short_description` (string, optional): Short description of the case
- `description` (string, optional): Detailed description of the case
- `contact` (string, optional): Contact associated with the case
- `account` (string, optional): Account associated with the case
- `priority` (string, optional): Priority of the case
- `state` (string, optional): State of the case
- `assigned_to` (string, optional): User assigned to the case
- `assignment_group` (string, optional): Group assigned to the case

### List Cases

Lists customer service cases.

**Tool Name:** `list_cases`

Uses the same parameters as the `cases` resource.

### Get Case

Gets details for a specific case.

**Tool Name:** `get_case`

**Parameters:**
- `case_id` (string, required): Case ID or sys_id


