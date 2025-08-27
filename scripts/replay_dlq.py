#!/usr/bin/env python3
"""Replay DLQ events to Airflow."""

import argparse
import json
from typing import List

from actions.airflow_trigger import AirflowTriggerAction


def replay(dlq_path: str, action: AirflowTriggerAction) -> None:
    """Read events from ``dlq_path`` and attempt to replay them.

    Successful events are removed from the DLQ. Failed events are written back.
    """
    remaining: List[dict] = []
    try:
        with open(dlq_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
    for line in lines:
        if not line.strip():
            continue
        entry = json.loads(line)
        event = entry.get("event", {})
        try:
            action.trigger(event)
        except Exception as e:  # pragma: no cover - re-queue failures
            entry["error"] = str(e)
            remaining.append(entry)
    with open(dlq_path, "w", encoding="utf-8") as f:
        for entry in remaining:
            f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay DLQ events")
    parser.add_argument("--airflow-url", required=True)
    parser.add_argument("--mappings", required=True)
    parser.add_argument("--dlq", required=True)
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--token")
    args = parser.parse_args()

    action = AirflowTriggerAction(
        args.airflow_url,
        args.mappings,
        username=args.username,
        password=args.password,
        token=args.token,
        dlq_path=None,
    )
    replay(args.dlq, action)


if __name__ == "__main__":
    main()
