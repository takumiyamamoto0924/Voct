import tempfile
import threading
from pathlib import Path

from voct.domain.entities import PushToTalkConfig
from voct.domain.ports import (
    AudioFilePort,
    ClipboardPort,
    HotkeyListenerPort,
    NotifierPort,
    PushToTalkRecorderPort,
    TranscriptFilePort,
    TranscriberPort,
)


class PushToTalkUseCase:
    """Push-to-Talk による録音・文字起こし・クリップボード連携ユースケース。"""

    def __init__(
        self,
        recorder: PushToTalkRecorderPort,
        audio_file: AudioFilePort,
        transcriber: TranscriberPort,
        clipboard: ClipboardPort,
        transcript_file: TranscriptFilePort,
        notifier: NotifierPort,
        listener: HotkeyListenerPort,
    ) -> None:
        self._recorder = recorder
        self._audio_file = audio_file
        self._transcriber = transcriber
        self._clipboard = clipboard
        self._transcript_file = transcript_file
        self._notifier = notifier
        self._listener = listener
        self._is_processing: bool = False
        self._is_recording: bool = False
        self._config: PushToTalkConfig | None = None

    def run(self, config: PushToTalkConfig) -> None:
        """バックグラウンド常駐ループを開始し、Ctrl+C で終了する。"""
        self._config = config
        print(f"[Voct] 起動しました。{config.trigger_key.name}キーを押している間だけ録音します。Ctrl+C で終了。")
        self._listener.start(self._on_press, self._on_release, config.trigger_key)
        try:
            self._listener.join()
        except KeyboardInterrupt:
            print("\n[Voct] 終了します。")
        finally:
            self._listener.stop()

    def _on_press(self) -> None:
        """キー押下コールバック: 処理中・録音中でなければ録音を開始する。"""
        if self._is_processing or self._is_recording:
            return
        self._is_recording = True
        self._recorder.start_recording(self._config.recording_config)
        print("[Voct] 録音中...")

    def _on_release(self) -> None:
        """キーリリースコールバック: 処理中でなければ処理スレッドを起動する。"""
        if self._is_processing:
            return
        self._is_recording = False
        self._is_processing = True
        threading.Thread(target=self._process_cycle, daemon=True).start()

    def _process_cycle(self) -> None:
        """1 サイクル分の処理: 停止→文字起こし→保存→クリップボードコピー。"""
        try:
            audio = self._recorder.stop_recording()

            if audio.duration_seconds < self._config.min_recording_seconds:
                print("[Voct] 録音が短すぎます。スキップします。")
                return

            temp_path = Path(tempfile.mktemp(suffix=".wav"))
            self._audio_file.save(audio, temp_path)
            print("[Voct] 文字起こし中...")
            result = self._transcriber.transcribe(
                temp_path,
                self._config.model_size,
                self._config.language,
            )
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

            if self._config.output_dir is not None:
                self._transcript_file.save(
                    result.text,
                    self._config.output_dir,
                    self._config.filename_format,
                )

            self._clipboard.copy(result.text)
            print(f"[Voct] コピー完了: {result.text[:50]}")
            print(f"[Voct] 待機中... ({self._config.trigger_key.name}キーで録音)")
        finally:
            self._is_processing = False
