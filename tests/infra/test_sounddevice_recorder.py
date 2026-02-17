from unittest.mock import MagicMock, patch

import numpy as np

from voct.domain.entities import RecordingConfig
from voct.infra.sounddevice_recorder import SoundDeviceRecorder


class TestSoundDeviceRecorder:
    @patch("voct.infra.sounddevice_recorder.sd")
    def test_record_returns_audio_data(self, mock_sd):
        mock_stream = MagicMock()
        chunk = np.zeros((1024, 1), dtype=np.float32)
        mock_stream.read.return_value = (chunk, False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = SoundDeviceRecorder()
        config = RecordingConfig(timeout_seconds=0.1, block_size=1024)

        result = recorder.record(config)

        assert result.sample_rate == 16000
        assert result.data.dtype == np.float32
        assert len(result.data) > 0

    @patch("voct.infra.sounddevice_recorder.sd")
    def test_record_timeout_stops_recording(self, mock_sd):
        mock_stream = MagicMock()
        chunk = np.zeros((1024, 1), dtype=np.float32)
        mock_stream.read.return_value = (chunk, False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = SoundDeviceRecorder()
        config = RecordingConfig(timeout_seconds=0.1, block_size=1024, sample_rate=16000)

        result = recorder.record(config)

        assert result.duration_seconds > 0
        assert result.duration_seconds <= 1.0  # should be roughly timeout + overhead

    @patch("voct.infra.sounddevice_recorder.sd")
    def test_record_uses_correct_stream_params(self, mock_sd):
        mock_stream = MagicMock()
        chunk = np.zeros((1024, 1), dtype=np.float32)
        mock_stream.read.return_value = (chunk, False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = SoundDeviceRecorder()
        config = RecordingConfig(sample_rate=16000, channels=1, timeout_seconds=0.1, block_size=1024)

        recorder.record(config)

        mock_sd.InputStream.assert_called_once_with(
            samplerate=16000,
            channels=1,
            blocksize=1024,
            dtype="float32",
        )

    @patch("voct.infra.sounddevice_recorder.sd")
    def test_record_data_is_mono(self, mock_sd):
        mock_stream = MagicMock()
        chunk = np.ones((1024, 1), dtype=np.float32) * 0.5
        mock_stream.read.return_value = (chunk, False)
        mock_sd.InputStream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_sd.InputStream.return_value.__exit__ = MagicMock(return_value=False)

        recorder = SoundDeviceRecorder()
        config = RecordingConfig(timeout_seconds=0.1, block_size=1024)

        result = recorder.record(config)

        assert result.data.ndim == 1
