from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class RecordingConfig:
    """録音設定。"""

    sample_rate: int = 16000
    channels: int = 1
    timeout_seconds: float = 5.0
    block_size: int = 1024


@dataclass(frozen=True)
class AudioData:
    """録音された音声データ。"""

    data: NDArray[np.float32]
    sample_rate: int
    duration_seconds: float


@dataclass(frozen=True)
class NotificationConfig:
    """音声通知設定。"""

    start_sound_path: str | None = None
    stop_sound_path: str | None = None


@dataclass(frozen=True)
class TranscriptionResult:
    """文字起こし結果。"""

    text: str
    language: str
    language_probability: float
    duration_seconds: float
    model_load_time_seconds: float
    transcription_time_seconds: float


class TriggerKey(Enum):
    """録音トリガーキーの列挙型。pynput への依存をドメイン外に封じ込める。"""

    ENTER = "enter"
    RIGHT_ALT = "alt_r"
    LEFT_ALT = "alt"
    RIGHT_CTRL = "ctrl_r"
    LEFT_CTRL = "ctrl"
    F1 = "f1"
    F2 = "f2"


@dataclass(frozen=True)
class PushToTalkConfig:
    """Push-to-Talk 機能の設定。"""

    trigger_key: TriggerKey = TriggerKey.ENTER
    model_size: str = "base"
    language: str | None = None
    output_dir: Path | None = None
    filename_format: str = "%Y%m%d-%H%M%S"
    min_recording_seconds: float = 0.5
    recording_config: RecordingConfig = field(default_factory=RecordingConfig)
    notification_config: NotificationConfig = field(default_factory=NotificationConfig)


@dataclass(frozen=True)
class PushToTalkResult:
    """Push-to-Talk の 1 サイクル結果。"""

    text: str
    recording_duration_seconds: float
    transcription_result: TranscriptionResult | None
    saved_file: Path | None
