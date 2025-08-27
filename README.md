# datahub-airflow-orchestrator-k8s
**Trigger Apache Airflow DAGs directly from DataHub events and UI.** Deployed on Kubernetes with security, observability, and AI-executable docs.

> No code in this repository skeleton—only requirements and issue templates so an AI agent (or a new engineer) can implement the system end-to-end without guesswork.

## Outcome
- DataHub **initiates** Airflow DAG runs using a custom **DataHub Action** that calls the Airflow REST API.
- Kubernetes-first deployment with reproducible installs via Helm (dev & prod profiles).
- All connectivity requirements (auth, RBAC, secrets, mapping rules) are specified here as **requirements**.
- Complete acceptance criteria, docs, and test expectations per task.

## Architecture (MVP)
**DataHub (Actions) → Airflow REST API → DAG Run**
1. A DataHub event (or a manual UI action) occurs.
2. The DataHub Action applies mapping rules → `{dag_id, conf}`.
3. It calls `POST /api/v1/dags/{dag_id}/dagRuns` with auth to start a run.
4. Airflow executes; results/lineage optionally appear in DataHub.

> Notes: secure the API; use allowlists for DAG IDs; add retries and a DLQ for resilience.

## Project Plan
Work is split into modular issues with acceptance criteria, docs, and explicit tests:
- EPIC + 13 issues in `.github/ISSUE_TEMPLATE/`.
- Each issue is **AI-executable**: inputs, steps, outputs, and “Definition of Done”.

## Repo Layout
```
.
├─ actions/
│  └─ airflow_trigger/         # DataHub Action source
├─ deploy/
│  ├─ airflow/                 # Helm chart scaffold
│  ├─ datahub/                 # Helm chart scaffold
│  └─ envs/
│     ├─ dev/                  # Dev profile values
│     └─ prod/                 # Prod profile values
├─ docs/
│  ├─ architecture.md          # Big picture and sequence
│  ├─ runbook.md               # Day-2 ops, playbooks
│  ├─ security.md              # Auth, RBAC, secrets
│  ├─ observability.md         # Logs, metrics, traces
│  ├─ troubleshooting.md       # Common errors & fixes
│  ├─ mappings.md              # Event→DAG mapping rules
│  ├─ lineage.md               # Optional Airflow↔DataHub lineage
│  ├─ ci.md                    # E2E CI approach (spin-up, test, tear-down)
│  ├─ airflow.md               # Airflow requirements (dev/prod profiles)
│  ├─ datahub.md               # DataHub requirements (Actions enabled)
│  ├─ profiles.md              # Dev vs Prod expectations
│  └─ CONTRIBUTING.md          # How to contribute (with AI notes)
├─ tests/
│  ├─ unit/                    # Fast unit tests
│  ├─ contract/                # API/contract tests
│  └─ e2e/                     # End-to-end tests
└─ README.md
```

## Running CI Locally

Install pinned tooling and Python dependencies:

```
asdf install
pip install -r requirements.txt
```

Run the same checks as CI:

```
make lint
make chart-lint
make test
```

## Definition of Done (Project)
- Helm-based installs for DataHub & Airflow work in dev & prod (to be implemented by issues).
- DataHub triggers a whitelisted Airflow DAG with `conf` and the run **completes**.
- Observability is in place with correlation IDs and simple metrics.
- CI (in follow-up repo) spins a local cluster, runs E2E, and tears down.
- Full docs set published and version-pinned references added.

## Naming & Tags
**Repo name suggestion:** `datahub-airflow-orchestrator-k8s`  
**Description:** “Trigger Airflow DAGs from DataHub via Actions; Kubernetes-first; secure and observable.”  
**Topics:** `datahub`, `airflow`, `kubernetes`, `helm`, `orchestration`, `lineage`, `catalog`

## License
Choose your org’s standard license (MIT/Apache-2.0/BSD-3-Clause). Add `LICENSE` when forking this skeleton.
