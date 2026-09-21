"""Validate chapter deliverables, report headings, book TOC and local Markdown links."""
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import nbformat
import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["README.md", "正文.md", "实验.ipynb", "习题.md", "习题参考解答.md", "AI对话记录.md",
            "编写报告.md", "验证.ipynb", "验证报告.md", "手动推导.md", "人工复核.ipynb", "批判报告.md", "AI陷阱.md"]


def main():
    errors = []
    chapters = json.loads((ROOT / "协作管理/章节清单.json").read_text(encoding="utf-8"))
    if len(chapters) != 8 or len({c["directory"] for c in chapters}) != 8:
        errors.append("Expected eight unique chapters")
    for chapter in chapters:
        folder = ROOT / "教材" / chapter["directory"]
        for name in REQUIRED:
            path = folder / name
            if not path.is_file() or not path.stat().st_size:
                errors.append(f"Missing or empty: {path.relative_to(ROOT)}")
        for report in ["编写报告", "验证报告", "批判报告"]:
            path = folder / f"{report}.md"
            if path.exists():
                content = path.read_text(encoding="utf-8-sig")
                if "状态：" not in content or "commit" not in content:
                    errors.append(f"Report needs explicit status and reviewed commit: {path.relative_to(ROOT)}")
        lab = folder / "实验.ipynb"
        if lab.exists():
            nb = nbformat.read(lab, as_version=4)
            if not any(c.cell_type == "code" and c.source.strip() for c in nb.cells):
                errors.append(f"Chapter experiment has no executable code: {lab.relative_to(ROOT)}")
    toc = yaml.safe_load((ROOT / "教材/_toc.yml").read_text(encoding="utf-8"))
    expected = [c["directory"] + "/正文" for c in chapters]
    if [entry.get("file") for entry in toc.get("chapters", [])] != expected:
        errors.append("TOC chapters differ from chapter registry")

    # Check local file targets in authored Markdown. Remote URLs and anchors are not fetched.
    for path in ROOT.rglob("*.md"):
        if any(p in {".git", ".venv", ".work", "_build", ".ipynb_checkpoints"} for p in path.relative_to(ROOT).parts):
            continue
        content = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8-sig"), flags=re.S)
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", content):
            target = target.strip().strip("<>")
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            resolved = (path.parent / unquote(parts.path)).resolve()
            if not resolved.exists():
                errors.append(f"Broken local link: {path.relative_to(ROOT)} -> {target}")
    if errors:
        print("\n".join(errors))
        return 1
    print("PASS: chapter structure, report metadata headings, TOC and local file links")
    print("Pending report text is allowed in the scaffold; acceptance requires human review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
