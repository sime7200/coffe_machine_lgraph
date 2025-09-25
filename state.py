from typing import TypedDict, Optional, Dict

class CoffeeState(TypedDict, total=False):
    order: str                      # User input
    parsed: Dict[str, str]          # Order interpretated by LLM
    inventory_ok: bool              # Result of inventory check
    message: Optional[str]          # Reply message to user
