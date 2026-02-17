from pathlib import Path
from unittest.mock import MagicMock, call

import numpy as np

from voct.domain.entities import AudioData, NotificationConfig, RecordingConfig, TranscriptionResult
from voct.usecase.record_and_transcribe import RecordAndTranscribeUseCase


class TestRecordAndTranscribeUseCase:
    def _make_mocks(self):
        recorder = MagicMock()
        audio_file = MagicMock()
        transcriber = MagicMock()
        notifier = MagicMock()

        recorder.record.return_value = AudioData(
            data=np.zeros(16000, dtype=np.float32),
            sample_rate=16000,
            duration_seconds=1.0,
        )
        audio_file.save.return_value = Path("/tmp/test.wav")
        transcriber.transcribe.return_value = TranscriptionResult(
            text="テスト",
            language="ja",
            language_probability=0.95,
            duration_seconds=1.0,
            model_load_time_seconds=0.5,
            transcription_time_seconds=0.3,
        )

        return recorder, audio_file, transcriber, notifier

    def test_execute_returns_transcription_result(self):
        recorder, audio_file, transcriber, notifier = self._make_mocks()
        usecase = RecordAndTranscribeUseCase(recorder, audio_file, transcriber, notifier)

        result = usecase.execute(
            recording_config=RecordingConfig(),
            notification_config=NotificationConfig(),
            temp_file_path=Path("/tmp/test.wav"),
        )

        assert result.text == "テスト"
        assert result.language == "ja"

    def test_execute_calls_in_correct_order(self):
        recorder, audio_file, transcriber, notifier = self._make_mocks()
        usecase = RecordAndTranscribeUseCase(recorder, audio_file, transcriber, notifier)

        manager = MagicMock()
        manager.attach_mock(notifier.play_start_sound, "play_start_sound")
        manager.attach_mock(recorder.record, "record")
        manager.attach_mock(notifier.play_stop_sound, "play_stop_sound")
        manager.attach_mock(audio_file.save, "save")
        manager.attach_mock(transcriber.transcribe, "transcribe")

        usecase.execute(
            recording_config=RecordingConfig(),
            notification_config=NotificationConfig(),
            temp_file_path=Path("/tmp/test.wav"),
        )

        expected_order = [
            call.play_start_sound(NotificationConfig()),
            call.record(RecordingConfig()),
            call.play_stop_sound(NotificationConfig()),
            call.save(recorder.record.return_value, Path("/tmp/test.wav")),
            call.transcribe(Path("/tmp/test.wav"), "base", None),
        ]
        manager.assert_has_calls(expected_order)

    def test_execute_passes_model_size_and_language(self):
        recorder, audio_file, transcriber, notifier = self._make_mocks()
        usecase = RecordAndTranscribeUseCase(recorder, audio_file, transcriber, notifier)

        usecase.execute(
            recording_config=RecordingConfig(),
            notification_config=NotificationConfig(),
            temp_file_path=Path("/tmp/test.wav"),
            model_size="small",
            language="ja",
        )

        transcriber.transcribe.assert_called_once_with(Path("/tmp/test.wav"), "small", "ja")

    def test_execute_passes_notification_config(self):
        recorder, audio_file, transcriber, notifier = self._make_mocks()
        usecase = RecordAndTranscribeUseCase(recorder, audio_file, transcriber, notifier)
        config = NotificationConfig(start_sound_path="/start.wav", stop_sound_path="/stop.wav")

        usecase.execute(
            recording_config=RecordingConfig(),
            notification_config=config,
            temp_file_path=Path("/tmp/test.wav"),
        )

        notifier.play_start_sound.assert_called_once_with(config)
        notifier.play_stop_sound.assert_called_once_with(config)
