from pathlib import Path

import numpy as np
import soundfile as sf

from voct.domain.entities import AudioData
from voct.domain.ports import AudioFilePort


class WavFileRepository(AudioFilePort):
    """soundfileを使用したWAVファイルI/O実装。"""

    def save(self, audio: AudioData, file_path: Path) -> Path:
        sf.write(str(file_path), audio.data, audio.sample_rate, subtype="PCM_16")
        return file_path

    def load(self, file_path: Path) -> AudioData:
        data, sample_rate = sf.read(str(file_path), dtype="float32")
        duration_seconds = len(data) / sample_rate
        return AudioData(
            data=np.asarray(data, dtype=np.float32),
            sample_rate=sample_rate,
            duration_seconds=duration_seconds,
        )
