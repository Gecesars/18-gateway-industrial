#!/usr/bin/env python3
"""Validate EDGE-18 JSON examples against their schemas.

Uses jsonschema when available. Syntax and repository-specific invariants are
always checked with the Python standard library.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_config_invariants(config: dict) -> None:
    device_ids = [device["id"] for device in config["modbus_devices"]]
    point_ids = [point["id"] for point in config["points"]]

    if len(device_ids) != len(set(device_ids)):
        raise ValueError("duplicate Modbus device id")
    if len(point_ids) != len(set(point_ids)):
        raise ValueError("duplicate point id")

    known_devices = set(device_ids)
    for point in config["points"]:
        if point["source"] == "modbus" and point["device"] not in known_devices:
            raise ValueError(
                f"point {point['id']} references unknown device {point['device']}"
            )
        if point["stale_ms"] < point["period_ms"]:
            raise ValueError(f"point {point['id']} has stale_ms < period_ms")


def main() -> int:
    config_schema = load("schemas/gateway-config.schema.json")
    telemetry_schema = load("schemas/telemetry.schema.json")
    config = load("examples/gateway-config.example.json")
    telemetry = load("examples/telemetry.example.json")

    validate_config_invariants(config)

    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed: structural invariants only")
    else:
        jsonschema.Draft202012Validator.check_schema(config_schema)
        jsonschema.Draft202012Validator.check_schema(telemetry_schema)
        jsonschema.validate(config, config_schema)
        jsonschema.validate(telemetry, telemetry_schema)
        print("JSON Schema validation: PASS")

    print("EDGE-18 schema invariants: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
