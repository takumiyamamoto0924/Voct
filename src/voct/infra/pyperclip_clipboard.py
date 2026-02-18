import platform
import subprocess

import pyperclip

from voct.domain.ports import ClipboardPort


class PyperclipClipboard(ClipboardPort):
    """クリップボード実装。macOS は pbcopy を直接使用し確実にコピーする。"""

    def copy(self, text: str) -> None:
        """テキストをシステムクリップボードにコピーする。"""
        if platform.system() == "Darwin":
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, close_fds=True)
            proc.communicate(input=text.encode("utf-8"))
        else:
            pyperclip.copy(text)
