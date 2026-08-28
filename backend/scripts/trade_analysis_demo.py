"""Demo parser: folder in, workbook out.

Place trade_analysis_v2.py in this folder to use it instead of this script.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.demo_parser import write_parser_workbook


def main() -> None:
    if len(sys.argv) != 2:
        print('Usage: python trade_analysis_demo.py "/path/to/logs"', file=sys.stderr)
        raise SystemExit(1)
    folder = Path(sys.argv[1])
    if not folder.is_dir():
        print("Log folder does not exist", file=sys.stderr)
        raise SystemExit(1)
    output = write_parser_workbook(folder)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
