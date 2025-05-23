"""Case management tools for the ServiceNow MCP server."""

import logging
from typing import Optional, Dict, Any

import requests
from pydantic import BaseModel, Field

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig

logger = logging.getLogger(__name__)


class CreateCaseParams(BaseModel):
    """Parameters for creating a case."""

    short_description: str = Field(..., description="Short description of the case")
    description: Optional[str] = Field(None, description="Detailed description of the case")
    contact: Optional[str] = Field(None, description="Contact associated with the case")
    account: Optional[str] = Field(None, description="Account associated with the case")
    priority: Optional[str] = Field(None, description="Priority of the case")
    state: Optional[str] = Field(None, description="State of the case")
    assigned_to: Optional[str] = Field(None, description="User assigned to the case")
    assignment_group: Optional[str] = Field(None, description="Group assigned to the case")


class UpdateCaseParams(BaseModel):
    """Parameters for updating a case."""

    case_id: str = Field(..., description="Case ID or sys_id")
    short_description: Optional[str] = Field(None, description="Short description of the case")
    description: Optional[str] = Field(None, description="Detailed description of the case")
    contact: Optional[str] = Field(None, description="Contact associated with the case")
    account: Optional[str] = Field(None, description="Account associated with the case")
    priority: Optional[str] = Field(None, description="Priority of the case")
    state: Optional[str] = Field(None, description="State of the case")
    assigned_to: Optional[str] = Field(None, description="User assigned to the case")
    assignment_group: Optional[str] = Field(None, description="Group assigned to the case")


class ListCasesParams(BaseModel):
    """Parameters for listing cases."""

    limit: int = Field(10, description="Maximum number of cases to return")
    offset: int = Field(0, description="Offset for pagination")
    state: Optional[str] = Field(None, description="Filter by case state")
    priority: Optional[str] = Field(None, description="Filter by case priority")
    query: Optional[str] = Field(None, description="Search query for cases")


class GetCaseParams(BaseModel):
    """Parameters for getting a case."""

    case_id: str = Field(..., description="Case ID or sys_id")


class CaseResponse(BaseModel):
    """Response from case operations."""

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    case_id: Optional[str] = Field(None, description="ID of the affected case")
    case_number: Optional[str] = Field(None, description="Number of the affected case")


def create_case(config: ServerConfig, auth_manager: AuthManager, params: CreateCaseParams) -> CaseResponse:
    """Create a new case in ServiceNow."""
    api_url = f"{config.api_url}/table/sn_customerservice_case"
    data = {
        "short_description": params.short_description,
    }
    if params.description:
        data["description"] = params.description
    if params.contact:
        data["contact"] = params.contact
    if params.account:
        data["account"] = params.account
    if params.priority:
        data["priority"] = params.priority
    if params.state:
        data["state"] = params.state
    if params.assigned_to:
        data["assigned_to"] = params.assigned_to
    if params.assignment_group:
        data["assignment_group"] = params.assignment_group

    try:
        response = requests.post(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
        result = response.json().get("result", {})
        return CaseResponse(
            success=True,
            message="Case created successfully",
            case_id=result.get("sys_id"),
            case_number=result.get("number"),
        )
    except requests.RequestException as e:
        logger.error(f"Failed to create case: {e}")
        return CaseResponse(success=False, message=f"Failed to create case: {str(e)}")


def update_case(config: ServerConfig, auth_manager: AuthManager, params: UpdateCaseParams) -> CaseResponse:
    """Update an existing case in ServiceNow."""
    case_id = params.case_id
    if len(case_id) == 32 and all(c in "0123456789abcdef" for c in case_id):
        api_url = f"{config.api_url}/table/sn_customerservice_case/{case_id}"
    else:
        try:
            query_url = f"{config.api_url}/table/sn_customerservice_case"
            query_params = {
                "sysparm_query": f"number={case_id}",
                "sysparm_limit": 1,
            }
            response = requests.get(
                query_url,
                params=query_params,
                headers=auth_manager.get_headers(),
                timeout=config.timeout,
            )
            response.raise_for_status()
            result = response.json().get("result", [])
            if not result:
                return CaseResponse(success=False, message=f"Case not found: {case_id}")
            case_id = result[0].get("sys_id")
            api_url = f"{config.api_url}/table/sn_customerservice_case/{case_id}"
        except requests.RequestException as e:
            logger.error(f"Failed to find case: {e}")
            return CaseResponse(success=False, message=f"Failed to find case: {str(e)}")

    data: Dict[str, Any] = {}
    if params.short_description:
        data["short_description"] = params.short_description
    if params.description:
        data["description"] = params.description
    if params.contact:
        data["contact"] = params.contact
    if params.account:
        data["account"] = params.account
    if params.priority:
        data["priority"] = params.priority
    if params.state:
        data["state"] = params.state
    if params.assigned_to:
        data["assigned_to"] = params.assigned_to
    if params.assignment_group:
        data["assignment_group"] = params.assignment_group

    try:
        response = requests.put(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
        result = response.json().get("result", {})
        return CaseResponse(
            success=True,
            message="Case updated successfully",
            case_id=result.get("sys_id"),
            case_number=result.get("number"),
        )
    except requests.RequestException as e:
        logger.error(f"Failed to update case: {e}")
        return CaseResponse(success=False, message=f"Failed to update case: {str(e)}")


def list_cases(config: ServerConfig, auth_manager: AuthManager, params: ListCasesParams) -> Dict[str, Any]:
    """List cases from ServiceNow."""
    api_url = f"{config.api_url}/table/sn_customerservice_case"
    query_params = {
        "sysparm_limit": params.limit,
        "sysparm_offset": params.offset,
        "sysparm_display_value": "true",
        "sysparm_exclude_reference_link": "true",
    }
    filters = []
    if params.state:
        filters.append(f"state={params.state}")
    if params.priority:
        filters.append(f"priority={params.priority}")
    if params.query:
        filters.append(f"short_descriptionLIKE{params.query}^ORdescriptionLIKE{params.query}")
    if filters:
        query_params["sysparm_query"] = "^".join(filters)

    try:
        response = requests.get(
            api_url,
            params=query_params,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
        data = response.json()
        cases = []
        for case_data in data.get("result", []):
            assigned_to = case_data.get("assigned_to")
            if isinstance(assigned_to, dict):
                assigned_to = assigned_to.get("display_value")
            cases.append({
                "sys_id": case_data.get("sys_id"),
                "number": case_data.get("number"),
                "short_description": case_data.get("short_description"),
                "description": case_data.get("description"),
                "state": case_data.get("state"),
                "priority": case_data.get("priority"),
                "assigned_to": assigned_to,
                "created_on": case_data.get("sys_created_on"),
                "updated_on": case_data.get("sys_updated_on"),
            })
        return {
            "success": True,
            "message": f"Found {len(cases)} cases",
            "cases": cases,
        }
    except requests.RequestException as e:
        logger.error(f"Failed to list cases: {e}")
        return {"success": False, "message": f"Failed to list cases: {str(e)}", "cases": []}


def get_case(config: ServerConfig, auth_manager: AuthManager, params: GetCaseParams) -> Dict[str, Any]:
    """Get a specific case by ID or number."""
    case_id = params.case_id
    if len(case_id) == 32 and all(c in "0123456789abcdef" for c in case_id):
        api_url = f"{config.api_url}/table/sn_customerservice_case/{case_id}"
    else:
        query_url = f"{config.api_url}/table/sn_customerservice_case"
        query_params = {
            "sysparm_query": f"number={case_id}",
            "sysparm_limit": 1,
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
        }
        try:
            response = requests.get(
                query_url,
                params=query_params,
                headers=auth_manager.get_headers(),
                timeout=config.timeout,
            )
            response.raise_for_status()
            result = response.json().get("result", [])
            if not result:
                return {"success": False, "message": f"Case not found: {case_id}"}
            case_id = result[0].get("sys_id")
            api_url = f"{config.api_url}/table/sn_customerservice_case/{case_id}"
        except requests.RequestException as e:
            logger.error(f"Failed to find case: {e}")
            return {"success": False, "message": f"Failed to find case: {str(e)}"}

    try:
        response = requests.get(
            api_url,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
        result = response.json().get("result", {})
        if not result:
            return {"success": False, "message": f"Case not found: {case_id}"}
        assigned_to = result.get("assigned_to")
        if isinstance(assigned_to, dict):
            assigned_to = assigned_to.get("display_value")
        case_data = {
            "sys_id": result.get("sys_id"),
            "number": result.get("number"),
            "short_description": result.get("short_description"),
            "description": result.get("description"),
            "state": result.get("state"),
            "priority": result.get("priority"),
            "assigned_to": assigned_to,
            "created_on": result.get("sys_created_on"),
            "updated_on": result.get("sys_updated_on"),
        }
        return {"success": True, "case": case_data}
    except requests.RequestException as e:
        logger.error(f"Failed to get case: {e}")
        return {"success": False, "message": f"Failed to get case: {str(e)}"}

