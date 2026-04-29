#!/usr/bin/env python3
"""
Minimal Helix advisor sidecar skeleton.

This script is intentionally lightweight and unopinionated:
- reads a compact JSON payload from stdin
- calls Anthropic's beta Messages API with the advisor tool
- prints the returned guidance as JSON

It is a scaffold, not a production-hardened runtime.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any


def main() -> int:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(json.dumps({"error": "ANTHROPIC_API_KEY is not set"}))
        return 1

    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": f"invalid input: {exc}"}))
        return 1

    # This file is a local bridge scaffold. It intentionally avoids bundling
    # a strict SDK dependency into ~/.claude. Replace this section with your
    # preferred Anthropic SDK or HTTPS client implementation.
    result: dict[str, Any] = {
        "status": "not_implemented",
        "message": (
            "Implement the HTTP call or SDK integration here. "
            "Input payload was accepted successfully."
        ),
        "received_keys": sorted(payload.keys()),
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
