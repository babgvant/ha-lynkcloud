"""Tests for LYNK Cloud controller discovery."""

import importlib.util
from pathlib import Path
import unittest


_MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "lynk_cloud"
    / "discovery.py"
)
_SPEC = importlib.util.spec_from_file_location("lynk_cloud_discovery", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_DISCOVERY = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_DISCOVERY)
lynk_node_id = _DISCOVERY.lynk_node_id
lynk_nodes = _DISCOVERY.lynk_nodes


class DiscoveryTests(unittest.TestCase):
    """Verify supported portal tree response shapes."""

    def test_data_id_is_used_for_current_portal_responses(self) -> None:
        node = {"id": 10, "dataId": 42, "lbId": 7, "children": []}

        self.assertEqual(lynk_node_id(node), "42")
        self.assertEqual(lynk_nodes([node]), [node])

    def test_ul_id_remains_supported(self) -> None:
        node = {"ulId": "legacy-controller", "children": []}

        self.assertEqual(lynk_node_id(node), "legacy-controller")

    def test_nested_nodes_are_flattened_and_deduplicated(self) -> None:
        controller = {"dataId": 42, "name": "Controller"}
        tree = [
            {"name": "Site", "children": [controller]},
            {"name": "Duplicate branch", "children": [controller.copy()]},
        ]

        self.assertEqual(lynk_nodes(tree), [controller])

    def test_unaddressable_nodes_are_ignored(self) -> None:
        self.assertEqual(lynk_nodes([{"id": 10, "children": []}]), [])


if __name__ == "__main__":
    unittest.main()
