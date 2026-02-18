from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path

from voct.domain.entities import (
    AudioData,
    NotificationConfig,
    RecordingConfig,
    TranscriptionResult,
    TriggerKey,
)


class RecorderPort(ABC):
    """録音ポート。マイクからの音声録音を抽象化する。"""

    @abstractmethod
    def record(self, config: RecordingConfig) -> AudioData:
        """マイクから音声を録音する。

        Enterキー押下またはタイムアウトで録音を停止する。
        """
        ...


class AudioFilePort(ABC):
    """音声ファイルI/Oポート。音声データの保存・読み込みを抽象化する。"""

    @abstractmethod
    def save(self, audio: AudioData, file_path: Path) -> Path:
        """音声データをファイルに保存する。"""
        ...

    @abstractmethod
    def load(self, file_path: Path) -> AudioData:
        """ファイルから音声データを読み込む。"""
        ...


class TranscriberPort(ABC):
    """文字起こしポート。音声→テキスト変換を抽象化する。"""

    @abstractmethod
    def transcribe(
        self,
        audio_path: Path,
        model_size: str = "base",
        language: str | None = None,
    ) -> TranscriptionResult:
        """音声ファイルを文字起こしする。"""
        ...


class NotifierPort(ABC):
    """音声通知ポート。ビープ音の再生を抽象化する。"""

    @abstractmethod
    def play_start_sound(self, config: NotificationConfig) -> None:
        """録音開始音を再生する。"""
        ...

    @abstractmethod
    def play_stop_sound(self, config: NotificationConfig) -> None:
        """録音終了音を再生する。"""
        ...


class PushToTalkRecorderPort(ABC):
    """Push-to-Talk 録音ポート。バックグラウンド録音の開始・停止を抽象化する。"""

    @abstractmethod
    def start_recording(self, config: RecordingConfig) -> None:
        """バックグラウンドで録音を開始する（非ブロッキング）。"""
        ...

    @abstractmethod
    def stop_recording(self) -> AudioData:
        """録音を停止し、収集した AudioData を同期的に返す。"""
        ...


class HotkeyListenerPort(ABC):
    """ホットキーリスナーポート。グローバルキーイベント監視を抽象化する。"""

    @abstractmethod
    def start(
        self,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
        trigger_key: TriggerKey,
    ) -> None:
        """キーリスナーをバックグラウンドで開始する（非ブロッキング）。"""
        ...

    @abstractmethod
    def join(self) -> None:
        """リスナースレッドの終了を待機する（ブロッキング）。"""
        ...

    @abstractmethod
    def stop(self) -> None:
        """リスナーを停止する。"""
        ...


class ClipboardPort(ABC):
    """クリップボードポート。システムクリップボード操作を抽象化する。"""

    @abstractmethod
    def copy(self, text: str) -> None:
        """テキストをシステムクリップボードにコピーする。"""
        ...


class TranscriptFilePort(ABC):
    """文字起こしファイルポート。Markdown ファイル保存を抽象化する。"""

    @abstractmethod
    def save(self, text: str, directory: Path, filename_format: str) -> Path:
        """文字起こし結果を Markdown ファイルとして保存し、パスを返す。"""
        ...
