import numpy as np
import sounddevice as sd
import soundfile as sf

from voct.domain.entities import NotificationConfig
from voct.domain.ports import NotifierPort

_SAMPLE_RATE = 44100
_DURATION = 0.15
_START_FREQ = 880
_STOP_FREQ = 440


def _generate_tone(frequency: float, duration: float = _DURATION, sample_rate: int = _SAMPLE_RATE) -> np.ndarray:
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False, dtype=np.float32)
    return (0.5 * np.sin(2 * np.pi * frequency * t)).astype(np.float32)


class SoundDeviceNotifier(NotifierPort):
    """sounddeviceを使用した音声通知実装。"""

    def play_start_sound(self, config: NotificationConfig) -> None:
        if config.start_sound_path is not None:
            data, sample_rate = sf.read(config.start_sound_path, dtype="float32")
        else:
            data = _generate_tone(_START_FREQ)
            sample_rate = _SAMPLE_RATE
        sd.play(data, samplerate=sample_rate)
        sd.wait()

    def play_stop_sound(self, config: NotificationConfig) -> None:
        if config.stop_sound_path is not None:
            data, sample_rate = sf.read(config.stop_sound_path, dtype="float32")
        else:
            data = _generate_tone(_STOP_FREQ)
            sample_rate = _SAMPLE_RATE
        sd.play(data, samplerate=sample_rate)
        sd.wait()
