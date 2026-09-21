"""Check trap record structure only, never claim to detect scientific/AI errors."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["检查范围", "状态：", "来源：", "错误主张：", "隐含假设：", "最小反例：", "预期与实测：", "原因分析：", "修复方式：", "回归验证："]


def main():
    errors = []
    pending = 0
    files = sorted((ROOT / "教材").glob("第*/AI陷阱.md"))
    if len(files) != 8:
        errors.append("Expected eight chapter trap records")
    for path in files:
        text = path.read_text(encoding="utf-8")
        for field in FIELDS:
            if field not in text:
                errors.append(f"{path.relative_to(ROOT)} missing: {field}")
        pending += "状态：待填写" in text
    if errors:
        print("\n".join(errors))
        return 1
    print(f"PASS: {len(files)} trap record structures; {pending} pending student completion")
    print("This is a format check, not automatic detection or proof of absence of AI traps.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
