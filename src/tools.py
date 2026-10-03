"""Tools the agent can call.

Each @tool function becomes something the model can choose to invoke
mid-conversation -- see agent.py for how they're wired into the agent.
This used to live inside agent.py; it moved out here once there were
enough tools to make that file hard to scan.
"""

import ast
import operator

from langchain.tools import tool


# ---------------------------------------------------------------------------
# calculator
# ---------------------------------------------------------------------------

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    """Recursively evaluate an arithmetic AST node, allowing only numbers
    and the operators above -- avoids using Python's real eval()."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("only numbers and + - * / % ** are allowed")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '12 * (3 + 4) / 2'.
    Supports +, -, *, /, %, **, and parentheses."""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_safe_eval(tree.body))
    except Exception as exc:
        return f"Could not evaluate '{expression}': {exc}"
