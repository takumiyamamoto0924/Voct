"""タスク 7.1/7.2/7.3/7.4: PushToTalkUseCase のテスト。"""

import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import numpy as np
import pytest

from voct.domain.entities import (
    AudioData,
    NotificationConfig,
    PushToTalkConfig,
    RecordingConfig,
    TranscriptionResult,
    TriggerKey,
)


def _make_mocks(duration: float = 1.0):
    """全外部依存のモックを生成するヘルパー。"""
    recorder = MagicMock()
    audio_file = MagicMock()
    transcriber = MagicMock()
    clipboard = MagicMock()
    transcript_file = MagicMock()
    notifier = MagicMock()
    listener = MagicMock()

    recorder.stop_recording.return_value = AudioData(
        data=np.zeros(int(16000 * duration), dtype=np.float32),
        sample_rate=16000,
        duration_seconds=duration,
    )
    audio_file.save.return_value = Path("/tmp/voct_temp.wav")
    transcriber.transcribe.return_value = TranscriptionResult(
        text="文字起こし結果",
        language="ja",
        language_probability=0.99,
        duration_seconds=duration,
        model_load_time_seconds=0.5,
        transcription_time_seconds=0.3,
    )
    transcript_file.save.return_value = Path("/tmp/20250101-120000.md")

    return recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener


class TestPushToTalkUseCaseRun:
    def test_run_starts_listener_and_joins(self):
        """run() はリスナーを起動し listener.join() でブロックする。"""
        from voct.usecase.push_to_talk import PushToTalkUseCase

        recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener = _make_mocks()
        listener.join.side_effect = KeyboardInterrupt()

        usecase = PushToTalkUseCase(
            recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener
        )
        config = PushToTalkConfig()
        usecase.run(config)

        listener.start.assert_called_once()
        listener.join.assert_called_once()
        listener.stop.assert_called_once()

    def test_run_passes_trigger_key_to_listener(self):
        """run() は config の trigger_key をリスナーに渡す。"""
        from voct.usecase.push_to_talk import PushToTalkUseCase

        recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener = _make_mocks()
        listener.join.side_effect = KeyboardInterrupt()

        usecase = PushToTalkUseCase(
            recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener
        )
        config = PushToTalkConfig(trigger_key=TriggerKey.F1)
        usecase.run(config)

        _, _, trigger_key_arg = listener.start.call_args[0]
        assert trigger_key_arg == TriggerKey.F1

    def test_run_stops_listener_on_keyboard_interrupt(self):
        """run() は KeyboardInterrupt でもリスナーを stop() する（finally）。"""
        from voct.usecase.push_to_talk import PushToTalkUseCase

        recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener = _make_mocks()
        listener.join.side_effect = KeyboardInterrupt()

        usecase = PushToTalkUseCase(
            recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener
        )
        usecase.run(PushToTalkConfig())

        listener.stop.assert_called_once()


class TestPushToTalkUseCaseOnPress:
    def _make_usecase_with_config(self, config=None):
        from voct.usecase.push_to_talk import PushToTalkUseCase

        recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener = _make_mocks()
        usecase = PushToTalkUseCase(
            recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener
        )
        usecase._config = config or PushToTalkConfig()
        return usecase, recorder

    def test_on_press_starts_recording(self):
        """_on_press() は recorder.start_recording() を呼ぶ。"""
        usecase, recorder = self._make_usecase_with_config()
        usecase._on_press()
        recorder.start_recording.assert_called_once()

    def test_on_press_skipped_when_processing(self):
        """_is_processing=True のとき _on_press() は recorder を呼ばない。"""
        usecase, recorder = self._make_usecase_with_config()
        usecase._is_processing = True
        usecase._on_press()
        recorder.start_recording.assert_not_called()

    def test_on_press_skipped_when_already_recording(self):
        """_is_recording=True（キーリピート）のとき _on_press() は recorder を呼ばない。"""
        usecase, recorder = self._make_usecase_with_config()
        usecase._is_recording = True
        usecase._on_press()
        recorder.start_recording.assert_not_called()

    def test_on_press_sets_is_recording(self):
        """_on_press() は _is_recording を True にする。"""
        usecase, recorder = self._make_usecase_with_config()
        assert usecase._is_recording is False
        usecase._on_press()
        assert usecase._is_recording is True

    def test_on_release_resets_is_recording(self):
        """_on_release() は _is_recording を False にする。"""
        usecase, recorder = self._make_usecase_with_config()
        usecase._is_recording = True
        usecase._on_release()
        assert usecase._is_recording is False


class TestPushToTalkUseCaseOnRelease:
    def _make_usecase_with_config(self, config=None):
        from voct.usecase.push_to_talk import PushToTalkUseCase

        recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener = _make_mocks()
        usecase = PushToTalkUseCase(
            recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener
        )
        usecase._config = config or PushToTalkConfig()
        return usecase, recorder, audio_file, transcriber, clipboard, transcript_file

    def test_on_release_skipped_when_processing(self):
        """_is_processing=True のとき _on_release() は処理スレッドを起動しない。"""
        usecase, recorder, *_ = self._make_usecase_with_config()
        usecase._is_processing = True
        usecase._on_release()
        # _is_processing はそのまま True のまま
        assert usecase._is_processing is True
        recorder.stop_recording.assert_not_called()

    def test_on_release_sets_is_processing(self):
        """_on_release() は _is_processing を True にする。"""
        usecase, recorder, audio_file, transcriber, clipboard, transcript_file = self._make_usecase_with_config()
        # stop_recording をゆっくり返すよう設定（スレッドが終わる前にチェックするため）
        slow_event = threading.Event()

        def slow_stop():
            slow_event.wait(timeout=5)
            return AudioData(data=np.zeros(0, dtype=np.float32), sample_rate=16000, duration_seconds=0.0)

        recorder.stop_recording.side_effect = slow_stop
        usecase._on_release()
        # スレッドが起動した直後は _is_processing = True
        time.sleep(0.05)
        assert usecase._is_processing is True
        slow_event.set()  # スレッドをアンブロック


class TestPushToTalkUseCaseProcessCycle:
    def _make_usecase_with_config(self, config=None, duration=1.0):
        from voct.usecase.push_to_talk import PushToTalkUseCase

        recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener = _make_mocks(duration)
        usecase = PushToTalkUseCase(
            recorder, audio_file, transcriber, clipboard, transcript_file, notifier, listener
        )
        usecase._config = config or PushToTalkConfig()
        return usecase, recorder, audio_file, transcriber, clipboard, transcript_file

    def test_normal_cycle_calls_all_steps(self):
        """正常 1 サイクル: stop_recording → save → transcribe → copy。"""
        usecase, recorder, audio_file, transcriber, clipboard, transcript_file = self._make_usecase_with_config()

        usecase._process_cycle()

        recorder.stop_recording.assert_called_once()
        audio_file.save.assert_called_once()
        transcriber.transcribe.assert_called_once()
        clipboard.copy.assert_called_once_with("文字起こし結果")

    def test_short_recording_skips_transcription(self):
        """最小録音時間未満の場合は文字起こしをスキップする。"""
        config = PushToTalkConfig(min_recording_seconds=1.0)
        usecase, recorder, audio_file, transcriber, clipboard, transcript_file = self._make_usecase_with_config(
            config=config, duration=0.3
        )

        usecase._process_cycle()

        transcriber.transcribe.assert_not_called()
        clipboard.copy.assert_not_called()

    def test_short_recording_resets_is_processing(self):
        """最小録音時間未満でスキップしても finally で _is_processing = False になる。"""
        config = PushToTalkConfig(min_recording_seconds=1.0)
        usecase, recorder, *_ = self._make_usecase_with_config(config=config, duration=0.3)
        usecase._is_processing = True

        usecase._process_cycle()

        assert usecase._is_processing is False

    def test_normal_cycle_resets_is_processing(self):
        """正常サイクル後に _is_processing = False になる。"""
        usecase, recorder, *_ = self._make_usecase_with_config()
        usecase._is_processing = True

        usecase._process_cycle()

        assert usecase._is_processing is False

    def test_transcript_file_saved_when_output_dir_set(self, tmp_path):
        """output_dir が設定されている場合は transcript_file.save() が呼ばれる。"""
        config = PushToTalkConfig(output_dir=tmp_path)
        usecase, recorder, audio_file, transcriber, clipboard, transcript_file = self._make_usecase_with_config(
            config=config
        )

        usecase._process_cycle()

        transcript_file.save.assert_called_once_with(
            "文字起こし結果",
            tmp_path,
            config.filename_format,
        )

    def test_transcript_file_not_saved_when_output_dir_none(self):
        """output_dir が None の場合は transcript_file.save() は呼ばれない。"""
        config = PushToTalkConfig(output_dir=None)
        usecase, recorder, audio_file, transcriber, clipboard, transcript_file = self._make_usecase_with_config(
            config=config
        )

        usecase._process_cycle()

        transcript_file.save.assert_not_called()

    def test_double_press_ignored(self):
        """処理中に _on_release() が呼ばれても二重起動しない。"""
        usecase, recorder, audio_file, transcriber, clipboard, transcript_file = self._make_usecase_with_config()

        usecase._is_processing = True
        usecase._on_release()

        # stop_recording はまだ呼ばれない
        recorder.stop_recording.assert_not_called()

    def test_transcribe_called_with_model_size_and_language(self):
        """transcriber.transcribe() に model_size と language が渡される。"""
        config = PushToTalkConfig(model_size="large", language="ja")
        usecase, recorder, audio_file, transcriber, clipboard, transcript_file = self._make_usecase_with_config(
            config=config
        )

        usecase._process_cycle()

        call_args = transcriber.transcribe.call_args
        assert call_args[0][1] == "large"  # model_size
        assert call_args[0][2] == "ja"     # language
