# 1. Modular Monolith Architecture and Import Layering Rules

* Status: Accepted
* Date: 2026-08-22
* Deciders: RazorRecover AI Architecture Team

## Context and Problem Statement
In v1.0, components were named without enforcing explicit boundary contracts or import constraints. Unconstrained imports between routers, DB models, AI logic, and payment adapters create tight coupling, unpredictable side-effects, and untestable business logic.

## Decision Drivers
* Enforce "LLM proposes, deterministic policy code decides, and tool executor acts".
* Ensure routers contain zero business or DB logic.
* Ensure AI and integration layers cannot trigger direct state or financial mutations outside the Policy Engine & Tool Executor.
* Enable strict static analysis enforcement via CI (AST linting).

## Considered Options
1. Microservices architecture with HTTP/gRPC internal calls.
2. Unstructured monolithic application.
3. Modular Monolith with enforced AST import linter rules (`routers → services → {repositories, integrations, policy, ai, tools}`).

## Decision Outcome
Chosen Option: **3. Modular Monolith with enforced AST import linter rules**.

### Import Dependency Graph
* **Routers** (`app/api/v1/`): May ONLY import `app/services/` and `app/schemas/`.
* **Services** (`app/services/`): May import `app/repositories/`, `app/integrations/`, `app/policy/`, `app/ai/`, `app/tools/`, `app/schemas/`, `app/models/`.
* **Repositories** (`app/repositories/`): Database access only. Forbidden from importing `services`, `routers`, `policy`, `ai`, `tools`.
* **Integrations** (`app/integrations/`): External API adapters only. Forbidden from importing `services`, `routers`, `repositories`, `policy`, `ai`, `tools`.
* **Policy** (`app/policy/`): Deterministic authorization pure functions (`context → decision`). Pure in-memory computation, zero I/O.
* **AI** (`app/ai/`): Produces structured recommendations only. Cannot import `tools` or `integrations`.
* **Tools** (`app/tools/`): Action execution layer. Only layer permitted to invoke write integration methods.

Reverse imports are strictly forbidden and enforced via `pytest apps/api/tests/test_layer_imports.py`.

## Consequences
* Good: Clear separation of concerns, high unit testability, zero risk of accidental AI-driven financial mutation.
* Good: Fast single-process deployment while maintaining modular boundaries.
* Mitigation: Import linter runs on every build in CI to prevent architectural drift.
