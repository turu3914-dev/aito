"""旧コマンドを維持する互換用入口。処理は日本語名のスクリプトに引き継ぐ。"""

from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "スクリプト" / "ボイスメモ文字起こし.py"

runpy.run_path(str(SCRIPT), run_name="__main__")
