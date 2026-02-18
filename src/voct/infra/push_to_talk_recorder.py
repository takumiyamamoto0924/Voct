import threading

import numpy as np
import sounddevice as sd

from voct.domain.entities import AudioData, RecordingConfig
from voct.domain.ports import PushToTalkRecorderPort


class PushToTalkSoundDeviceRecorder(PushToTalkRecorderPort):
    """sounddevice を使った Push-to-Talk 録音実装。"""

    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._recording_thread: threading.Thread | None = None
        self._chunks: list[np.ndarray] = []
        self._sample_rate: int = 16000

    def start_recording(self, config: RecordingConfig) -> None:
        """バックグラウンドスレッドでオーディオストリームを開始する（非ブロッキング）。"""
        self._stop_event.clear()
        self._chunks = []
        self._sample_rate = config.sample_rate
        self._recording_thread = threading.Thread(
            target=self._record_loop,
            args=(config,),
            daemon=True,
        )
        self._recording_thread.start()

    def _record_loop(self, config: RecordingConfig) -> None:
        """バックグラウンドスレッドで録音を継続する。stop_event またはタイムアウトで停止。"""
        max_chunks = int(config.sample_rate * config.timeout_seconds / config.block_size)
        with sd.InputStream(
            samplerate=config.sample_rate,
            channels=config.channels,
            blocksize=config.block_size,
            dtype="float32",
        ) as stream:
            for _ in range(max_chunks):
                if self._stop_event.is_set():
                    break
                data, _ = stream.read(config.block_size)
                self._chunks.append(data.copy())

    def stop_recording(self) -> AudioData:
        """stop_event で録音ループを停止し AudioData を返す。"""
        self._stop_event.set()
        if self._recording_thread is not None:
            self._recording_thread.join()

        if not self._chunks:
            audio_data = np.array([], dtype=np.float32)
        else:
            audio_data = np.concatenate(self._chunks, axis=0).flatten()

        duration_seconds = len(audio_data) / self._sample_rate

        return AudioData(
            data=audio_data,
            sample_rate=self._sample_rate,
            duration_seconds=duration_seconds,
        )
