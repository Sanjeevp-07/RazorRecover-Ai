import ast
import os

"""
Automated AST Architectural Import Rule Linter (§5 of Specification & ADR 0001).

Mandatory Layering Rule:
  routers -> services -> {repositories, integrations, policy, ai, tools}

Reverse imports or cross-layer violations strictly fail the test build in CI.
"""

# Map of layer directory relative to app/ -> forbidden imported modules
FORBIDDEN_IMPORTS = {
    "api": ["app.repositories", "app.integrations", "app.policy", "app.ai", "app.tools", "app.workers"],
    "repositories": ["app.services", "app.api", "app.policy", "app.ai", "app.tools", "app.integrations", "app.workers"],
    "policy": ["app.services", "app.api", "app.repositories", "app.integrations", "app.tools", "app.workers"],
    "ai": ["app.services", "app.api", "app.tools", "app.integrations", "app.repositories", "app.workers"],
    "integrations": ["app.services", "app.api", "app.repositories", "app.policy", "app.ai", "app.tools", "app.workers"],
    "tools": ["app.services", "app.api", "app.policy", "app.ai", "app.repositories", "app.workers"],
    "services": ["app.api"],
}

def get_imported_modules(file_path: str) -> list[str]:
    """Parse python file AST and return list of imported module paths."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports

def test_enforce_layer_import_rules():
    base_app_dir = os.path.join(os.path.dirname(__file__), "..", "app")
    violations = []

    for root, _, files in os.walk(base_app_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, base_app_dir)
                parts = rel_path.split(os.sep)
                
                layer = parts[0]
                if layer in FORBIDDEN_IMPORTS:
                    forbidden_list = FORBIDDEN_IMPORTS[layer]
                    imported = get_imported_modules(file_path)
                    
                    for imp in imported:
                        for forbidden in forbidden_list:
                            if imp == forbidden or imp.startswith(forbidden + "."):
                                violations.append(
                                    f"Architecture Layer Violation in {rel_path}: Layer '{layer}' "
                                    f"is forbidden from importing '{imp}' (Rule: {forbidden})"
                                )

    assert not violations, "\n".join(violations)
