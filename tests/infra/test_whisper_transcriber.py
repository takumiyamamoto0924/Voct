from pathlib import Path
from unittest.mock import MagicMock, patch

from voct.infra.whisper_transcriber import WhisperTranscriber


def _make_mock_segment(text: str, start: float = 0.0, end: float = 1.0):
    seg = MagicMock()
    seg.text = text
    seg.start = start
    seg.end = end
    return seg


class TestWhisperTranscriber:
    @patch("voct.infra.whisper_transcriber.WhisperModel")
    def test_transcribe_returns_result(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_info = MagicMock()
        mock_info.language = "ja"
        mock_info.language_probability = 0.95
        mock_info.duration = 2.0
        segments = [_make_mock_segment("こんにちは")]
        mock_model.transcribe.return_value = (iter(segments), mock_info)

        transcriber = WhisperTranscriber()
        result = transcriber.transcribe(Path("/tmp/test.wav"))

        assert result.text == "こんにちは"
        assert result.language == "ja"
        assert result.language_probability == 0.95

    @patch("voct.infra.whisper_transcriber.WhisperModel")
    def test_transcribe_joins_segments(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_info = MagicMock()
        mock_info.language = "ja"
        mock_info.language_probability = 0.9
        mock_info.duration = 5.0
        segments = [
            _make_mock_segment("こんにちは", 0.0, 1.0),
            _make_mock_segment("今日は", 1.0, 2.0),
            _make_mock_segment("いい天気です", 2.0, 3.0),
        ]
        mock_model.transcribe.return_value = (iter(segments), mock_info)

        transcriber = WhisperTranscriber()
        result = transcriber.transcribe(Path("/tmp/test.wav"))

        assert result.text == "こんにちは今日はいい天気です"

    @patch("voct.infra.whisper_transcriber.WhisperModel")
    def test_transcribe_empty_result(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_info = MagicMock()
        mock_info.language = "ja"
        mock_info.language_probability = 0.5
        mock_info.duration = 1.0
        mock_model.transcribe.return_value = (iter([]), mock_info)

        transcriber = WhisperTranscriber()
        result = transcriber.transcribe(Path("/tmp/test.wav"))

        assert result.text == ""

    @patch("voct.infra.whisper_transcriber.WhisperModel")
    def test_transcribe_passes_language(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_info = MagicMock()
        mock_info.language = "ja"
        mock_info.language_probability = 0.99
        mock_info.duration = 1.0
        mock_model.transcribe.return_value = (iter([]), mock_info)

        transcriber = WhisperTranscriber()
        transcriber.transcribe(Path("/tmp/test.wav"), language="ja")

        mock_model.transcribe.assert_called_once()
        call_kwargs = mock_model.transcribe.call_args[1]
        assert call_kwargs["language"] == "ja"

    @patch("voct.infra.whisper_transcriber.WhisperModel")
    def test_transcribe_measures_performance(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_info = MagicMock()
        mock_info.language = "ja"
        mock_info.language_probability = 0.9
        mock_info.duration = 2.0
        mock_model.transcribe.return_value = (iter([_make_mock_segment("test")]), mock_info)

        transcriber = WhisperTranscriber()
        result = transcriber.transcribe(Path("/tmp/test.wav"))

        assert result.model_load_time_seconds >= 0
        assert result.transcription_time_seconds >= 0

    @patch("voct.infra.whisper_transcriber.WhisperModel")
    def test_transcribe_uses_cpu_int8(self, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_info = MagicMock()
        mock_info.language = "ja"
        mock_info.language_probability = 0.9
        mock_info.duration = 1.0
        mock_model.transcribe.return_value = (iter([]), mock_info)

        transcriber = WhisperTranscriber()
        transcriber.transcribe(Path("/tmp/test.wav"), model_size="base")

        mock_model_cls.assert_called_once_with("base", device="cpu", compute_type="int8")
