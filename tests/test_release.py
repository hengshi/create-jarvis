import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_release", ROOT / "scripts" / "verify_release.py"
)
assert SPEC and SPEC.loader
VERIFY_RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY_RELEASE)


class ReleaseContractTest(unittest.TestCase):
    def test_stable_method_tag_is_independent_and_changelog_backed(self):
        VERIFY_RELEASE.verify("v0.1.0", (ROOT / "CHANGELOG.md").read_text())

    def test_floating_or_runtime_shaped_inputs_are_not_method_releases(self):
        for value in ("main", "0.1.0", "v0.1", "jarvis-box-v0.1.38"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    VERIFY_RELEASE.verify(value, "## 0.1.0\n")

    def test_tag_without_changelog_release_is_rejected(self):
        with self.assertRaises(ValueError):
            VERIFY_RELEASE.verify("v0.1.1", "## Unreleased\n")


if __name__ == "__main__":
    unittest.main()
