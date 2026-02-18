from datetime import datetime
from pathlib import Path

from voct.domain.ports import TranscriptFilePort


class MarkdownTranscriptFile(TranscriptFilePort):
    """Markdown ファイルに文字起こし結果を保存する実装。"""

    def save(self, text: str, directory: Path, filename_format: str) -> Path:
        """文字起こし結果を Markdown ファイルとして保存し、パスを返す。"""
        directory.mkdir(parents=True, exist_ok=True)
        filename = datetime.now().strftime(filename_format) + ".md"
        file_path = directory / filename
        file_path.write_text(text, encoding="utf-8")
        return file_path
