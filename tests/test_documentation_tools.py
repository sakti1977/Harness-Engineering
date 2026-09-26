from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

exporter = load("export_handbook")
checker = load("check_docs")

class DocumentationTools(unittest.TestCase):
    def test_alias_and_space_path_render_as_relative_markdown(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Topic Folder").mkdir()
            (root / "Topic Folder/Target.md").write_text("# Target\n")
            (root / "Index.md").write_text("[[Target|Read this]]\n")
            self.assertEqual(exporter.render(root)[Path("Index.md")], "[Read this](Topic%20Folder/Target.md)\n")

    def test_unresolved_and_ambiguous_links_fail(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Index.md").write_text("[[Missing]]")
            with self.assertRaises(ValueError):
                exporter.render(root)
            (root / "Missing.md").write_text("one")
            (root / "other").mkdir()
            (root / "other/Missing.md").write_text("two")
            with self.assertRaises(ValueError):
                exporter.render(root)

    def test_missing_local_link_is_detected_but_external_is_not_fetched(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("[missing](no.md) [external](https://example.com)\n")
            found = checker.errors(root)
            self.assertEqual(len(found), 1)
            self.assertIn("no.md", found[0])

if __name__ == "__main__":
    unittest.main()
