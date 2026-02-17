from pathlib import Path

from voct.domain.entities import NotificationConfig, RecordingConfig, TranscriptionResult
from voct.domain.ports import AudioFilePort, NotifierPort, RecorderPort, TranscriberPort


class RecordAndTranscribeUseCase:
    """録音→保存→文字起こしのパイプラインを実行するユースケース。"""

    def __init__(
        self,
        recorder: RecorderPort,
        audio_file: AudioFilePort,
        transcriber: TranscriberPort,
        notifier: NotifierPort,
    ) -> None:
        self._recorder = recorder
        self._audio_file = audio_file
        self._transcriber = transcriber
        self._notifier = notifier

    def execute(
        self,
        recording_config: RecordingConfig,
        notification_config: NotificationConfig,
        temp_file_path: Path,
        model_size: str = "base",
        language: str | None = None,
    ) -> TranscriptionResult:
        self._notifier.play_start_sound(notification_config)
        audio = self._recorder.record(recording_config)
        self._notifier.play_stop_sound(notification_config)
        self._audio_file.save(audio, temp_file_path)
        return self._transcriber.transcribe(temp_file_path, model_size, language)
