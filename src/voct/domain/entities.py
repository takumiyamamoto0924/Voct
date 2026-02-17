from dataclasses import dataclass

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
