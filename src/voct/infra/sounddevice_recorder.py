import threading

import numpy as np
import sounddevice as sd

from voct.domain.entities import AudioData, RecordingConfig
from voct.domain.ports import RecorderPort


class SoundDeviceRecorder(RecorderPort):
    """sounddeviceを使用した録音実装。"""

    def record(self, config: RecordingConfig) -> AudioData:
        stop_event = threading.Event()

        def _wait_for_enter():
            try:
                input()
            except EOFError:
                pass
            stop_event.set()

        enter_thread = threading.Thread(target=_wait_for_enter, daemon=True)
        enter_thread.start()

        chunks: list[np.ndarray] = []
        max_chunks = int(config.sample_rate * config.timeout_seconds / config.block_size)

        with sd.InputStream(
            samplerate=config.sample_rate,
            channels=config.channels,
            blocksize=config.block_size,
            dtype="float32",
        ) as stream:
            for _ in range(max_chunks):
                if stop_event.is_set():
                    break
                data, _overflowed = stream.read(config.block_size)
                chunks.append(data.copy())

        if not chunks:
            audio_data = np.array([], dtype=np.float32)
        else:
            audio_data = np.concatenate(chunks, axis=0).flatten()

        duration_seconds = len(audio_data) / config.sample_rate

        return AudioData(
            data=audio_data,
            sample_rate=config.sample_rate,
            duration_seconds=duration_seconds,
        )
