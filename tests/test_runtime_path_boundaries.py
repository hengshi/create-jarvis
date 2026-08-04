from __future__ import annotations

import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_runtime_paths", ROOT / "scripts" / "validate_runtime_paths.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class RuntimePathBoundaryTests(unittest.TestCase):
    def test_sibling_build_source_and_runtime_paths_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            result = VALIDATOR.validate(
                str(root / "jarvis-build"),
                str(root / "repos" / "acme-jarvis"),
                str(root / "runtime" / "jarvis-box"),
            )
            self.assertEqual(
                result["deployment_home"],
                str((root / "runtime" / "jarvis-box").resolve()),
            )

    def test_every_nested_role_pair_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            cases = [
                (root / "jarvis-build", root / "jarvis-build" / "company", root / "runtime"),
                (root / "jarvis-build", root / "company", root / "jarvis-build" / "runtime"),
                (root / "jarvis-build", root / "company", root / "company" / "runtime"),
            ]
            for construction, company, deployment in cases:
                with self.subTest(paths=(construction, company, deployment)):
                    with self.assertRaisesRegex(ValueError, "physically disjoint"):
                        VALIDATOR.validate(str(construction), str(company), str(deployment))

    def test_relative_paths_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be absolute"):
            VALIDATOR.validate("jarvis-build", "/tmp/company", "/tmp/runtime")


if __name__ == "__main__":
    unittest.main()
