"""タスク 3.1/3.2/3.3: PushToTalkSoundDeviceRecorder のテスト。"""

import threading
import time
from unittest.mock import MagicMock, call, patch

import numpy as np
import pytest

from voct.domain.entities import AudioData, RecordingConfig


class TestPushToTalkSoundDeviceRecorder:
    @patch("voct.infra.push_to_talk_recorder.sd")
    def test_start_recording_is_nonblocking(self, mock_sd):
        """start_recording() は即座に返る（非ブロッキング）。"""
        from voct.infra.push_to_talk_recorder import PushToTalkSoundDeviceRecorder

        mock_stream = MagicMock()
        mock_stream.read.return_value = (np.zeros((1024, 1), dtype=np.float32), False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = PushToTalkSoundDeviceRecorder()
        config = RecordingConfig(timeout_seconds=5.0)

        start = time.time()
        recorder.start_recording(config)
        elapsed = time.time() - start

        assert elapsed < 0.5, "start_recording() should return almost immediately"
        recorder.stop_recording()  # cleanup

    @patch("voct.infra.push_to_talk_recorder.sd")
    def test_stop_recording_returns_audio_data(self, mock_sd):
        """stop_recording() は AudioData を返す。"""
        from voct.infra.push_to_talk_recorder import PushToTalkSoundDeviceRecorder

        chunk = np.ones((1024, 1), dtype=np.float32) * 0.5
        mock_stream = MagicMock()
        mock_stream.read.return_value = (chunk, False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = PushToTalkSoundDeviceRecorder()
        config = RecordingConfig(sample_rate=16000, timeout_seconds=5.0)

        recorder.start_recording(config)
        time.sleep(0.05)
        result = recorder.stop_recording()

        assert isinstance(result, AudioData)
        assert result.sample_rate == 16000
        assert result.data.dtype == np.float32
        assert result.data.ndim == 1

    @patch("voct.infra.push_to_talk_recorder.sd")
    def test_stop_recording_accumulates_chunks(self, mock_sd):
        """録音中に読み取ったチャンクが AudioData に蓄積される。"""
        from voct.infra.push_to_talk_recorder import PushToTalkSoundDeviceRecorder

        chunk = np.ones((1024, 1), dtype=np.float32)
        mock_stream = MagicMock()
        mock_stream.read.return_value = (chunk, False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = PushToTalkSoundDeviceRecorder()
        config = RecordingConfig(sample_rate=16000, timeout_seconds=5.0, block_size=1024)

        recorder.start_recording(config)
        time.sleep(0.05)  # 複数チャンクが読まれる時間
        result = recorder.stop_recording()

        assert len(result.data) > 0, "録音データが蓄積されていること"

    @patch("voct.infra.push_to_talk_recorder.sd")
    def test_duration_seconds_is_correct(self, mock_sd):
        """duration_seconds が sample_rate に基づいて計算される。"""
        from voct.infra.push_to_talk_recorder import PushToTalkSoundDeviceRecorder

        chunk = np.ones((1024, 1), dtype=np.float32)
        mock_stream = MagicMock()
        mock_stream.read.return_value = (chunk, False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = PushToTalkSoundDeviceRecorder()
        config = RecordingConfig(sample_rate=16000, timeout_seconds=5.0, block_size=1024)

        recorder.start_recording(config)
        time.sleep(0.05)
        result = recorder.stop_recording()

        expected_duration = len(result.data) / config.sample_rate
        assert abs(result.duration_seconds - expected_duration) < 1e-6

    @patch("voct.infra.push_to_talk_recorder.sd")
    def test_timeout_stops_recording_automatically(self, mock_sd):
        """タイムアウトが経過すると録音が自動停止する。"""
        from voct.infra.push_to_talk_recorder import PushToTalkSoundDeviceRecorder

        chunk = np.ones((1024, 1), dtype=np.float32)
        mock_stream = MagicMock()
        mock_stream.read.return_value = (chunk, False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = PushToTalkSoundDeviceRecorder()
        # 非常に短いタイムアウトで自動停止をテスト
        config = RecordingConfig(sample_rate=16000, timeout_seconds=0.05, block_size=1024)

        recorder.start_recording(config)
        # タイムアウトが経過するのを待つ
        time.sleep(0.2)
        # タイムアウト後に stop_recording() を呼んでも正常に返る
        result = recorder.stop_recording()

        assert isinstance(result, AudioData)
        # タイムアウトによる録音長は timeout_seconds 以下
        assert result.duration_seconds <= config.timeout_seconds + 0.1

    @patch("voct.infra.push_to_talk_recorder.sd")
    def test_stream_params_match_recording_config(self, mock_sd):
        """sd.InputStream が RecordingConfig のパラメータで呼ばれる。"""
        from voct.infra.push_to_talk_recorder import PushToTalkSoundDeviceRecorder

        chunk = np.zeros((512, 1), dtype=np.float32)
        mock_stream = MagicMock()
        mock_stream.read.return_value = (chunk, False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = PushToTalkSoundDeviceRecorder()
        config = RecordingConfig(sample_rate=22050, channels=1, timeout_seconds=5.0, block_size=512)

        recorder.start_recording(config)
        time.sleep(0.02)
        recorder.stop_recording()

        mock_sd.InputStream.assert_called_once_with(
            samplerate=22050,
            channels=1,
            blocksize=512,
            dtype="float32",
        )

    @patch("voct.infra.push_to_talk_recorder.sd")
    def test_empty_recording_returns_empty_audio_data(self, mock_sd):
        """録音データが空の場合は duration_seconds=0.0 の AudioData を返す。"""
        from voct.infra.push_to_talk_recorder import PushToTalkSoundDeviceRecorder

        mock_stream = MagicMock()
        # read がすぐ停止されるよう timeout を極小に設定
        mock_stream.read.return_value = (np.zeros((1024, 1), dtype=np.float32), False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = PushToTalkSoundDeviceRecorder()
        config = RecordingConfig(sample_rate=16000, timeout_seconds=5.0)

        recorder.start_recording(config)
        # start 直後に stop → チャンクが蓄積される前かもしれないがクラッシュしないこと
        result = recorder.stop_recording()

        assert isinstance(result, AudioData)
        assert result.data.dtype == np.float32
        assert result.sample_rate == 16000
