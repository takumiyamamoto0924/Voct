import os
import tempfile
from pathlib import Path

from voct.domain.entities import NotificationConfig, RecordingConfig
from voct.infra.sounddevice_notifier import SoundDeviceNotifier
from voct.infra.sounddevice_recorder import SoundDeviceRecorder
from voct.infra.wav_file_repository import WavFileRepository
from voct.infra.whisper_transcriber import WhisperTranscriber
from voct.usecase.record_and_transcribe import RecordAndTranscribeUseCase


def main() -> None:
    recorder = SoundDeviceRecorder()
    audio_file = WavFileRepository()
    transcriber = WhisperTranscriber()
    notifier = SoundDeviceNotifier()

    usecase = RecordAndTranscribeUseCase(recorder, audio_file, transcriber, notifier)

    recording_config = RecordingConfig()
    notification_config = NotificationConfig()

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_path = Path(tmp.name)
    tmp.close()

    try:
        print("[Voct] 録音を開始します... (Enterキーで停止、または5秒でタイムアウト)")
        result = usecase.execute(
            recording_config=recording_config,
            notification_config=notification_config,
            temp_file_path=temp_path,
        )
        print(f"[Voct] 録音完了: {result.duration_seconds:.1f}秒")
        print(f"[Voct] モデルロード時間: {result.model_load_time_seconds:.1f}秒")
        ratio = result.transcription_time_seconds / result.duration_seconds if result.duration_seconds > 0 else 0
        print(f"[Voct] 文字起こし時間: {result.transcription_time_seconds:.1f}秒 (録音時間比: {ratio:.2f}x)")

        if result.text:
            print(f"[Voct] 結果:\n{result.text}")
        else:
            print("[Voct] 文字起こし結果が空です")
    finally:
        if temp_path.exists():
            os.unlink(temp_path)


if __name__ == "__main__":
    main()
