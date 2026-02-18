"""タスク 5.1: PyperclipClipboard のテスト。"""

from unittest.mock import MagicMock, patch


class TestPyperclipClipboard:
    @patch("voct.infra.pyperclip_clipboard.platform")
    @patch("voct.infra.pyperclip_clipboard.subprocess")
    def test_copy_uses_pbcopy_on_macos(self, mock_subprocess, mock_platform):
        """macOS では pbcopy を使ってテキストをコピーする。"""
        from voct.infra.pyperclip_clipboard import PyperclipClipboard

        mock_platform.system.return_value = "Darwin"
        mock_proc = MagicMock()
        mock_subprocess.Popen.return_value = mock_proc

        clipboard = PyperclipClipboard()
        clipboard.copy("こんにちは")

        mock_subprocess.Popen.assert_called_once_with(
            ["pbcopy"], stdin=mock_subprocess.PIPE, close_fds=True
        )
        mock_proc.communicate.assert_called_once_with(input="こんにちは".encode("utf-8"))

    @patch("voct.infra.pyperclip_clipboard.platform")
    @patch("voct.infra.pyperclip_clipboard.pyperclip")
    def test_copy_uses_pyperclip_on_non_macos(self, mock_pyperclip, mock_platform):
        """macOS 以外では pyperclip.copy() を呼び出す。"""
        from voct.infra.pyperclip_clipboard import PyperclipClipboard

        mock_platform.system.return_value = "Linux"

        clipboard = PyperclipClipboard()
        clipboard.copy("hello")

        mock_pyperclip.copy.assert_called_once_with("hello")

    @patch("voct.infra.pyperclip_clipboard.platform")
    @patch("voct.infra.pyperclip_clipboard.subprocess")
    def test_copy_encodes_utf8_for_pbcopy(self, mock_subprocess, mock_platform):
        """pbcopy には UTF-8 エンコードしたバイト列を渡す。"""
        from voct.infra.pyperclip_clipboard import PyperclipClipboard

        mock_platform.system.return_value = "Darwin"
        mock_proc = MagicMock()
        mock_subprocess.Popen.return_value = mock_proc

        text = "日本語テスト\n複数行"
        clipboard = PyperclipClipboard()
        clipboard.copy(text)

        mock_proc.communicate.assert_called_once_with(input=text.encode("utf-8"))
