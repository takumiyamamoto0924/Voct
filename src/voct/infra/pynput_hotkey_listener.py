import sys
from collections.abc import Callable

from pynput import keyboard

from voct.domain.entities import TriggerKey
from voct.domain.ports import HotkeyListenerPort

# TriggerKey → pynput keyboard.Key の属性名マッピング
# キーの解決は start() 時に行うことで、テストでのモック差し替えに対応する
_KEY_MAP: dict[TriggerKey, str] = {
    TriggerKey.ENTER:      "enter",
    TriggerKey.RIGHT_ALT:  "alt_r",
    TriggerKey.LEFT_ALT:   "alt",
    TriggerKey.RIGHT_CTRL: "ctrl_r",
    TriggerKey.LEFT_CTRL:  "ctrl",
    TriggerKey.F1:         "f1",
    TriggerKey.F2:         "f2",
}


class PynputHotkeyListener(HotkeyListenerPort):
    """pynput を使ったグローバルキーボードリスナー実装。"""

    def __init__(self) -> None:
        self._listener: keyboard.Listener | None = None

    def start(
        self,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
        trigger_key: TriggerKey,
    ) -> None:
        """キーリスナーをバックグラウンドで開始する。macOS 権限エラー時は案内して終了。"""
        target_key = getattr(keyboard.Key, _KEY_MAP[trigger_key])

        def _on_press(key: keyboard.Key) -> None:
            if key == target_key:
                on_press()

        def _on_release(key: keyboard.Key) -> None:
            if key == target_key:
                on_release()

        try:
            self._listener = keyboard.Listener(
                on_press=_on_press,
                on_release=_on_release,
            )
            self._listener.start()
        except OSError:
            print("[Voct] エラー: キーボードリスナーを起動できません。")
            print("[Voct] macOS では「システム設定 > プライバシーとセキュリティ > アクセシビリティ」で")
            print("[Voct] このアプリに権限を付与してください。")
            sys.exit(1)

    def join(self) -> None:
        """リスナースレッドの終了を待機する（ブロッキング）。"""
        if self._listener is not None:
            self._listener.join()

    def stop(self) -> None:
        """リスナーを停止する。"""
        if self._listener is not None:
            self._listener.stop()
