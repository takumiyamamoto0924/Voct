import numpy as np
import soundfile as sf

from voct.domain.entities import AudioData
from voct.infra.wav_file_repository import WavFileRepository


class TestWavFileRepository:
    def test_save_creates_wav_file(self, tmp_path):
        repo = WavFileRepository()
        audio = AudioData(
            data=np.zeros(16000, dtype=np.float32),
            sample_rate=16000,
            duration_seconds=1.0,
        )
        path = tmp_path / "test.wav"

        result = repo.save(audio, path)

        assert result == path
        assert path.exists()

    def test_save_format_is_pcm16_16khz_mono(self, tmp_path):
        repo = WavFileRepository()
        audio = AudioData(
            data=np.zeros(16000, dtype=np.float32),
            sample_rate=16000,
            duration_seconds=1.0,
        )
        path = tmp_path / "test.wav"

        repo.save(audio, path)

        info = sf.info(str(path))
        assert info.subtype == "PCM_16"
        assert info.samplerate == 16000
        assert info.channels == 1

    def test_load_returns_audio_data(self, tmp_path):
        repo = WavFileRepository()
        original_data = np.random.rand(16000).astype(np.float32) * 0.5
        audio = AudioData(data=original_data, sample_rate=16000, duration_seconds=1.0)
        path = tmp_path / "test.wav"
        repo.save(audio, path)

        loaded = repo.load(path)

        assert loaded.sample_rate == 16000
        assert loaded.duration_seconds == 1.0
        assert np.allclose(loaded.data, original_data, atol=1e-4)

    def test_save_and_load_roundtrip(self, tmp_path):
        repo = WavFileRepository()
        original_data = np.sin(np.linspace(0, 2 * np.pi, 16000)).astype(np.float32)
        audio = AudioData(data=original_data, sample_rate=16000, duration_seconds=1.0)
        path = tmp_path / "roundtrip.wav"

        repo.save(audio, path)
        loaded = repo.load(path)

        assert loaded.sample_rate == audio.sample_rate
        assert np.allclose(loaded.data, original_data, atol=1e-4)
