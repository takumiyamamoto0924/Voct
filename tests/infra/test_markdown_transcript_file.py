"""タスク 6.1/6.2: MarkdownTranscriptFile のテスト。"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestMarkdownTranscriptFile:
    def test_save_creates_file_in_directory(self, tmp_path):
        """save() は指定ディレクトリにファイルを作成する。"""
        from voct.infra.markdown_transcript_file import MarkdownTranscriptFile

        tf = MarkdownTranscriptFile()
        result = tf.save("hello", tmp_path, "%Y%m%d-%H%M%S")

        assert result.exists()
        assert result.parent == tmp_path

    def test_save_file_has_md_extension(self, tmp_path):
        """save() は .md 拡張子のファイルを作成する。"""
        from voct.infra.markdown_transcript_file import MarkdownTranscriptFile

        tf = MarkdownTranscriptFile()
        result = tf.save("hello", tmp_path, "%Y%m%d-%H%M%S")

        assert result.suffix == ".md"

    def test_save_file_contains_text(self, tmp_path):
        """save() はファイルに指定テキストを書き込む。"""
        from voct.infra.markdown_transcript_file import MarkdownTranscriptFile

        text = "文字起こし結果です"
        tf = MarkdownTranscriptFile()
        result = tf.save(text, tmp_path, "%Y%m%d-%H%M%S")

        assert result.read_text(encoding="utf-8") == text

    def test_save_creates_directory_if_not_exists(self, tmp_path):
        """save() はディレクトリが存在しない場合に自動作成する。"""
        from voct.infra.markdown_transcript_file import MarkdownTranscriptFile

        new_dir = tmp_path / "nested" / "dir"
        assert not new_dir.exists()

        tf = MarkdownTranscriptFile()
        result = tf.save("hello", new_dir, "%Y%m%d-%H%M%S")

        assert new_dir.exists()
        assert result.exists()

    def test_save_filename_uses_format(self, tmp_path):
        """save() は datetime.strftime(filename_format) + '.md' でファイル名を生成する。"""
        from voct.infra.markdown_transcript_file import MarkdownTranscriptFile

        fixed_dt = datetime(2025, 3, 15, 10, 30, 45)

        with patch("voct.infra.markdown_transcript_file.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_dt

            tf = MarkdownTranscriptFile()
            result = tf.save("hello", tmp_path, "%Y%m%d-%H%M%S")

        assert result.name == "20250315-103045.md"

    def test_save_returns_path_object(self, tmp_path):
        """save() は Path オブジェクトを返す。"""
        from voct.infra.markdown_transcript_file import MarkdownTranscriptFile

        tf = MarkdownTranscriptFile()
        result = tf.save("hello", tmp_path, "%Y%m%d-%H%M%S")

        assert isinstance(result, Path)

    def test_save_with_custom_filename_format(self, tmp_path):
        """save() はカスタムフォーマット文字列を使用する。"""
        from voct.infra.markdown_transcript_file import MarkdownTranscriptFile

        fixed_dt = datetime(2025, 3, 15, 10, 30, 45)

        with patch("voct.infra.markdown_transcript_file.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_dt

            tf = MarkdownTranscriptFile()
            result = tf.save("hello", tmp_path, "%Y-%m-%d")

        assert result.name == "2025-03-15.md"
