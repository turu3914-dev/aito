"""
音声メモ/ にある未処理の音声ファイルを文字起こしし、
記録/音声/<ファイル名>.md に書き出す。

使い方:
    python スクリプト/ボイスメモ文字起こし.py

要約や補足はこのスクリプトでは行わない。文字起こし結果を
Claude に読ませて、記録/要約.md 等に要約を書かせる想定。
"""

import sys
from pathlib import Path
from datetime import datetime

AUDIO_EXTS = {".m4a", ".mp3", ".wav", ".mp4", ".ogg", ".flac", ".aac", ".wma"}

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "音声メモ"
OUTPUT_DIR = ROOT / "記録" / "音声"


def find_unprocessed():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for p in sorted(INPUT_DIR.iterdir()):
        if p.suffix.lower() not in AUDIO_EXTS:
            continue
        out_path = OUTPUT_DIR / f"{p.stem}.md"
        if not out_path.exists():
            files.append(p)
    return files


def transcribe_all():
    targets = find_unprocessed()
    if not targets:
        print("未処理の音声ファイルはありません。")
        return []

    from faster_whisper import WhisperModel

    print(f"モデルを読み込み中... ({len(targets)} 件を処理)")
    model = WhisperModel("base", device="cpu", compute_type="int8")

    processed = []
    for audio_path in targets:
        print(f"文字起こし中: {audio_path.name}")
        segments, info = model.transcribe(str(audio_path), language="ja")
        text_lines = [seg.text.strip() for seg in segments]
        full_text = "\n".join(line for line in text_lines if line)

        out_path = OUTPUT_DIR / f"{audio_path.stem}.md"
        recorded_at = datetime.fromtimestamp(audio_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        out_path.write_text(
            f"# {audio_path.stem}\n\n"
            f"- 元ファイル: `{audio_path.name}`\n"
            f"- 録音(更新)日時: {recorded_at}\n"
            f"- 言語検出: {info.language} (確信度 {info.language_probability:.2f})\n\n"
            f"## 文字起こし\n\n{full_text}\n",
            encoding="utf-8",
        )
        print(f"  -> {out_path.relative_to(ROOT)}")
        processed.append(out_path)

    return processed


if __name__ == "__main__":
    transcribe_all()
