"""タスク 4.1/4.2/4.3: PynputHotkeyListener のテスト。"""

import sys
import threading
from unittest.mock import MagicMock, call, patch

import pytest

from voct.domain.entities import TriggerKey


class TestPynputHotkeyListener:
    @patch("voct.infra.pynput_hotkey_listener.keyboard")
    def test_start_launches_background_listener(self, mock_keyboard):
        """start() は pynput.keyboard.Listener をバックグラウンドで起動する。"""
        from voct.infra.pynput_hotkey_listener import PynputHotkeyListener

        mock_listener_instance = MagicMock()
        mock_keyboard.Listener.return_value = mock_listener_instance

        listener = PynputHotkeyListener()
        on_press = MagicMock()
        on_release = MagicMock()

        listener.start(on_press, on_release, TriggerKey.ENTER)

        mock_keyboard.Listener.assert_called_once()
        mock_listener_instance.start.assert_called_once()

    @patch("voct.infra.pynput_hotkey_listener.keyboard")
    def test_on_press_callback_called_for_trigger_key(self, mock_keyboard):
        """対象トリガーキーが押されると on_press コールバックが呼ばれる。"""
        from voct.infra.pynput_hotkey_listener import PynputHotkeyListener

        captured_on_press = {}

        def fake_listener(**kwargs):
            captured_on_press["fn"] = kwargs.get("on_press")
            mock = MagicMock()
            mock.start = MagicMock()
            mock.join = MagicMock()
            mock.stop = MagicMock()
            return mock

        mock_keyboard.Listener.side_effect = fake_listener
        mock_keyboard.Key.enter = "enter_key"

        listener = PynputHotkeyListener()
        on_press_cb = MagicMock()
        on_release_cb = MagicMock()

        listener.start(on_press_cb, on_release_cb, TriggerKey.ENTER)

        # pynput の on_press ハンドラを直接呼び出してシミュレート
        pynput_on_press = captured_on_press["fn"]
        pynput_on_press("enter_key")  # トリガーキーと一致

        on_press_cb.assert_called_once()

    @patch("voct.infra.pynput_hotkey_listener.keyboard")
    def test_on_press_not_called_for_other_keys(self, mock_keyboard):
        """トリガーキー以外のキーでは on_press コールバックが呼ばれない。"""
        from voct.infra.pynput_hotkey_listener import PynputHotkeyListener

        captured_on_press = {}

        def fake_listener(**kwargs):
            captured_on_press["fn"] = kwargs.get("on_press")
            mock = MagicMock()
            mock.start = MagicMock()
            return mock

        mock_keyboard.Listener.side_effect = fake_listener
        mock_keyboard.Key.enter = "enter_key"
        mock_keyboard.Key.space = "space_key"

        listener = PynputHotkeyListener()
        on_press_cb = MagicMock()
        on_release_cb = MagicMock()

        listener.start(on_press_cb, on_release_cb, TriggerKey.ENTER)

        pynput_on_press = captured_on_press["fn"]
        pynput_on_press("space_key")  # トリガーキーと不一致

        on_press_cb.assert_not_called()

    @patch("voct.infra.pynput_hotkey_listener.keyboard")
    def test_on_release_callback_called_for_trigger_key(self, mock_keyboard):
        """対象トリガーキーが離されると on_release コールバックが呼ばれる。"""
        from voct.infra.pynput_hotkey_listener import PynputHotkeyListener

        captured = {}

        def fake_listener(**kwargs):
            captured["on_release"] = kwargs.get("on_release")
            mock = MagicMock()
            mock.start = MagicMock()
            return mock

        mock_keyboard.Listener.side_effect = fake_listener
        mock_keyboard.Key.f1 = "f1_key"

        listener = PynputHotkeyListener()
        on_press_cb = MagicMock()
        on_release_cb = MagicMock()

        listener.start(on_press_cb, on_release_cb, TriggerKey.F1)

        pynput_on_release = captured["on_release"]
        pynput_on_release("f1_key")

        on_release_cb.assert_called_once()

    @patch("voct.infra.pynput_hotkey_listener.keyboard")
    def test_on_release_not_called_for_other_keys(self, mock_keyboard):
        """トリガーキー以外のキーを離しても on_release は呼ばれない。"""
        from voct.infra.pynput_hotkey_listener import PynputHotkeyListener

        captured = {}

        def fake_listener(**kwargs):
            captured["on_release"] = kwargs.get("on_release")
            mock = MagicMock()
            mock.start = MagicMock()
            return mock

        mock_keyboard.Listener.side_effect = fake_listener
        mock_keyboard.Key.f1 = "f1_key"
        mock_keyboard.Key.space = "space_key"

        listener = PynputHotkeyListener()
        on_press_cb = MagicMock()
        on_release_cb = MagicMock()

        listener.start(on_press_cb, on_release_cb, TriggerKey.F1)

        pynput_on_release = captured["on_release"]
        pynput_on_release("space_key")

        on_release_cb.assert_not_called()

    @patch("voct.infra.pynput_hotkey_listener.keyboard")
    def test_join_blocks_on_listener_join(self, mock_keyboard):
        """join() は内部の pynput Listener の join() を呼ぶ。"""
        from voct.infra.pynput_hotkey_listener import PynputHotkeyListener

        mock_listener_instance = MagicMock()
        mock_keyboard.Listener.return_value = mock_listener_instance

        listener = PynputHotkeyListener()
        listener.start(MagicMock(), MagicMock(), TriggerKey.ENTER)
        listener.join()

        mock_listener_instance.join.assert_called_once()

    @patch("voct.infra.pynput_hotkey_listener.keyboard")
    def test_stop_stops_listener(self, mock_keyboard):
        """stop() は内部の pynput Listener を停止する。"""
        from voct.infra.pynput_hotkey_listener import PynputHotkeyListener

        mock_listener_instance = MagicMock()
        mock_keyboard.Listener.return_value = mock_listener_instance

        listener = PynputHotkeyListener()
        listener.start(MagicMock(), MagicMock(), TriggerKey.ENTER)
        listener.stop()

        mock_listener_instance.stop.assert_called_once()

    @patch("voct.infra.pynput_hotkey_listener.sys")
    @patch("voct.infra.pynput_hotkey_listener.keyboard")
    def test_oserror_shows_guidance_and_exits(self, mock_keyboard, mock_sys):
        """macOS 権限エラー（OSError）発生時は案内メッセージを表示して sys.exit(1)。"""
        from voct.infra.pynput_hotkey_listener import PynputHotkeyListener

        mock_keyboard.Listener.side_effect = OSError("accessibility permissions required")

        listener = PynputHotkeyListener()

        listener.start(MagicMock(), MagicMock(), TriggerKey.ENTER)

        mock_sys.exit.assert_called_once_with(1)

    @patch("voct.infra.pynput_hotkey_listener.keyboard")
    def test_all_trigger_keys_are_mapped(self, mock_keyboard):
        """全 TriggerKey が _KEY_MAP に定義されている。"""
        from voct.infra.pynput_hotkey_listener import _KEY_MAP

        for trigger_key in TriggerKey:
            assert trigger_key in _KEY_MAP, f"{trigger_key} が _KEY_MAP に存在しない"
