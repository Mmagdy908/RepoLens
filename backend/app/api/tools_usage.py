from fastapi import APIRouter


router = APIRouter(prefix="/api")

_tools_usage_count = {
    "architecture": 0,
    "file_explain": 0,
    "folder_explain": 0,
    "general_qa": 0,
    "overview": 0,
    "tech_stack": 0,
    "diagram_architecture": 0,
    "diagram_sequence": 0,
    "diagram_component": 0,
}


@router.get("/tools-usage")
def get_tools_usage() -> dict[str, int]:
    """Get the usage count of each tool."""
    return _tools_usage_count
