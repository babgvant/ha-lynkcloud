"""Helpers for discovering LYNK controllers in the portal tree."""

from __future__ import annotations

from typing import Any


def lynk_node_id(node: dict[str, Any]) -> str | None:
    """Return the identifier used as ulId by the telemetry endpoints."""
    for key in ("dataId", "ulId"):
        value = node.get(key)
        if value is not None:
            return str(value)
    return None


def lynk_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten the portal tree and retain telemetry-addressable nodes."""
    found: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if (node_id := lynk_node_id(node)) is not None:
            found[node_id] = node
        children = node.get("children")
        if isinstance(children, list):
            for child in lynk_nodes(children):
                if (child_id := lynk_node_id(child)) is not None:
                    found[child_id] = child
    return list(found.values())
