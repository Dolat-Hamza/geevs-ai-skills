import pathlib
import unittest
import zipfile

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
ZIP = PLUGIN.parents[1] / "dist" / "geevs-agent-team.zip"


def plugin_files():
    return {
        f"geevs-agent-team/{p.relative_to(PLUGIN).as_posix()}": p.read_bytes()
        for p in PLUGIN.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


@unittest.skipUnless(ZIP.is_file(), "no dist zip in this checkout")
class DistZip(unittest.TestCase):
    def test_zip_matches_plugin(self):
        with zipfile.ZipFile(ZIP) as z:
            packed = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
        self.assertEqual(sorted(packed), sorted(plugin_files()), "rebuild dist/geevs-agent-team.zip")
        self.assertEqual(packed, plugin_files(), "rebuild dist/geevs-agent-team.zip")


if __name__ == "__main__":
    unittest.main()
