"""Tool registry - all available tools for the agent."""

from anycoder.tools.bash import BashTool
from anycoder.tools.read_file import ReadFileTool
from anycoder.tools.write_file import WriteFileTool
from anycoder.tools.edit_file import EditFileTool
from anycoder.tools.glob_tool import GlobTool
from anycoder.tools.grep_tool import GrepTool

ALL_TOOLS = [
    BashTool(),
    ReadFileTool(),
    WriteFileTool(),
    EditFileTool(),
    GlobTool(),
    GrepTool(),
]

TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}


def get_tool_schemas() -> list[dict]:
    """Get OpenAI-format tool schemas for all tools."""
    return [tool.to_schema() for tool in ALL_TOOLS]
