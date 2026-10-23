"""Visual-contract tests: all records and generated PNGs are SYNTHETIC ONLY."""
import base64
import copy
import hashlib
from html import escape
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import unittest
import zlib

import appraisal_report as report
import test_appraisal_report as baseline


def synthetic_png():
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data)))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + chunk(b"IEND", b""))


class VisualTests(unittest.TestCase):
    setUp = baseline.ReportTests.setUp
    cli = baseline.ReportTests.cli
    validate = baseline.ReportTests.validate

    def visual(self, **changes):
        path = self.root / "assets" / "synthetic.png"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(synthetic_png())
        row = dict(id="SYNTHETIC-V1", kind="figure", source_id="S1", source_page=1,
                   label="Figura sintética 1", path="assets/synthetic.png",
                   sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                   caption="Quadrado vermelho gerado apenas para teste sintético.",
                   analysis="Permite testar a integridade da ilustração; não representa dados clínicos.",
                   evidence_ids=["E1"], section="results")
        row.update(changes)
        self.record["visuals"] = [row]
        return row

    def test_valid_png_resolves_relative_to_record_base(self):
        self.visual()
        report.validate(self.record, self.root)
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.record["visuals"] = []
        report.validate(self.record, self.root)

    def test_visual_sha256_matches_original_png_bytes(self):
        row = self.visual()
        for digest in ("0" * 64, "not-a-digest", row["sha256"].upper(), None):
            with self.subTest(digest=digest):
                row["sha256"] = digest
                with self.assertRaisesRegex(ValueError, "visuals.sha256"):
                    report.validate(self.record, self.root)

    def test_png_requires_signature_and_complete_ihdr(self):
        row = self.visual()
        good = synthetic_png()
        invalid = [b"not png", good[:8], good[:32], b"BADBYTES" + good[8:],
                   good[:12] + b"NOPE" + good[16:],
                   good[:8] + struct.pack(">I", 12) + good[12:],
                   good[:16] + struct.pack(">I", 0) + good[20:]]
        for data in invalid:
            with self.subTest(data=data[:24]):
                (self.root / row["path"]).write_bytes(data)
                row["sha256"] = hashlib.sha256(data).hexdigest()
                with self.assertRaisesRegex(ValueError, "visuals.path.*PNG"):
                    report.validate(self.record, self.root)

    def test_visual_provenance_requires_full_text_page_and_existing_evidence(self):
        row = self.visual()
        for field, value, diagnostic in (("source_id", "S999", "source_id"),
                ("evidence_ids", ["E999"], "evidence_ids"), ("evidence_ids", [], "evidence_ids"),
                ("evidence_ids", ["E1", "E1"], "evidence_ids"),
                ("source_page", True, "source_page"), ("source_page", 0, "source_page"),
                ("source_page", -1, "source_page"), ("source_page", "1", "source_page")):
            saved = row[field]
            with self.subTest(field=field, value=value):
                row[field] = value
                with self.assertRaisesRegex(ValueError, "visuals." + diagnostic):
                    report.validate(self.record, self.root)
            row[field] = saved
        self.record["sources"][0]["kind"] = "abstract"
        self.record["assessment"]["status"] = "limited"
        with self.assertRaisesRegex(ValueError, "visuals.source_id.*full_text"):
            report.validate(self.record, self.root)

    def test_visual_paths_are_local_relative_png_inside_record_base(self):
        row = self.visual()
        absolute = str(self.root / row["path"])
        (self.root / "assets" / "synthetic.jpg").write_bytes(synthetic_png())
        (self.root / "assets" / "escape.png").symlink_to(self.root.parent / "outside.png")
        invalid = [absolute, "../synthetic.png", "assets/../assets/synthetic.png",
                   "https://invalid.example/image.png", "//host/image.png", "data:image/png;base64,AA",
                   "C:\\image.png", "assets\\synthetic.png", "assets/synthetic.jpg", "assets",
                   "assets/missing.png", "assets/escape.png", "assets/\x00.png"]
        for value in invalid:
            with self.subTest(path=value):
                row["path"] = value
                with self.assertRaisesRegex(ValueError, "visuals.path"):
                    report.validate(self.record, self.root)

    def test_visual_contract_requires_caption_analysis_and_native_section(self):
        original = self.visual()
        for field, value in (("caption", " "), ("analysis", ""), ("label", ""),
                ("kind", "decoration"), ("section", "unknown"), ("id", ""),
                ("kind", ["figure"]), ("section", ["results"])):
            self.record["visuals"] = [dict(original, **{field: value})]
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, "visuals"):
                report.validate(self.record, self.root)
        for field in original:
            row = dict(original)
            del row[field]
            self.record["visuals"] = [row]
            with self.subTest(missing=field), self.assertRaisesRegex(ValueError, "visuals"):
                report.validate(self.record, self.root)
        for rows in (None, {}, [dict(original, score=1)], [original, original]):
            self.record["visuals"] = rows
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, "visuals"):
                report.validate(self.record, self.root)
        self.record["visuals"] = [dict(original, kind="article_header", section="methods")]
        with self.assertRaisesRegex(ValueError, "visuals.section"):
            report.validate(self.record, self.root)
        for kind in ("figure", "table"):
            for section in report.SECTIONS:
                self.record["visuals"] = [dict(original, kind=kind, section=section)]
                report.validate(self.record, self.root)

    def test_only_one_article_header_is_allowed(self):
        row = self.visual(kind="article_header", section="executive_summary")
        report.validate(self.record, self.root)
        self.record["visuals"].append(dict(row, id="SYNTHETIC-V2"))
        with self.assertRaisesRegex(ValueError, "visuals.*article_header"):
            report.validate(self.record, self.root)

    def test_render_places_escaped_illustrations_and_embeds_original_bytes(self):
        payload = '<svg onload="x">&\' [synthetic]'
        figure = self.visual(label="Figura 1 " + payload, caption="Descrição " + payload,
                             analysis="Utilidade analítica " + payload)
        header = dict(figure, id="HEADER", kind="article_header", section="executive_summary", label="Cabeçalho")
        table = dict(figure, id="TABLE", kind="table", section="methods", label="Tabela 1")
        self.record["visuals"] = [figure, header, table]
        self.record["sources"][0]["label"] += payload
        for key in ("methods", "results"):
            claim = dict(self.record["claims"][0], id=key, text="SYNTHETIC unique " + key)
            self.record["claims"].append(claim)
            self.record["sections"][key] = [key]
        report.validate(self.record, self.root)
        md, html = report.render(self.record, self.root)
        images = re.findall(r'<img[^>]+src="data:image/png;base64,([^" ]+)"', html)
        self.assertEqual(len(images), 3)
        for encoded in images:
            self.assertEqual(base64.b64decode(encoded, validate=True), synthetic_png())
        self.assertLess(html.index("<figure>"), html.index("<h1>"))
        for key, next_heading, label in (("methods", "Intervenção / exposição", "Tabela 1"),
                                          ("results", "Avaliação estatística", "Figura 1")):
            between = html.split("SYNTHETIC unique " + key, 1)[1].split("<h2>" + next_heading, 1)[0]
            self.assertRegex(between, r"</p>\s*<figure>")
            self.assertIn(escape(label), between)
        for value in (figure["label"], figure["caption"], figure["analysis"], self.record["sources"][0]["label"]):
            self.assertIn(escape(value), html)
        self.assertNotIn("<svg", html)
        self.assertIn("Fonte: S1", html)
        self.assertIn("página 1", html)
        self.assertIn("[E1]", html)
        self.assertEqual(md.count("](assets/synthetic.png)"), 3)
        self.assertLess(md.index("!["), md.index("# Análise"))
        self.assertIn("Descrição &lt;svg", md)
        self.assertIn("Análise: Utilidade analítica", md)
        self.assertIn("<footer>Revisão humana: pendente</footer>", html)

    def test_cli_uses_record_base_and_output_relative_markdown_links(self):
        row = self.visual()
        old = self.root / row["path"]
        row["path"] = 'assets/synthetic [x] " &.png'
        old.rename(self.root / row["path"])
        self.record_path.write_text(json.dumps(self.record), encoding="utf-8")
        prefix = self.root / "reports" / "illustrated"
        for command in ("validate", "render"):
            args = [sys.executable, str(baseline.SCRIPT), command, str(self.record_path)]
            if command == "render":
                args += ["--output-prefix", str(prefix)]
            result = subprocess.run(args, cwd=self.root.parent, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        html = prefix.with_suffix(".html").read_text(encoding="utf-8")
        encoded = re.search(r'data:image/png;base64,([^" ]+)', html).group(1)
        self.assertEqual(base64.b64decode(encoded), synthetic_png())
        md = prefix.with_suffix(".md").read_text(encoding="utf-8")
        self.assertIn("](../assets/synthetic%20%5Bx%5D%20%22%20%26.png)", md)

    def test_cli_cannot_overwrite_visual_through_output_symlink(self):
        row = self.visual()
        prefix = self.root / "protected-visual"
        prefix.with_suffix(".md").symlink_to(self.root / row["path"])
        result = self.cli("render", str(self.record_path), "--output-prefix", str(prefix))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("entrada", result.stderr)
        self.assertEqual((self.root / row["path"]).read_bytes(), synthetic_png())
        self.assertFalse(prefix.with_suffix(".html").exists())


if __name__ == "__main__":
    unittest.main()
