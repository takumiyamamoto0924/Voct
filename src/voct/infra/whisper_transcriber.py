import time
from pathlib import Path

from faster_whisper import WhisperModel

from voct.domain.entities import TranscriptionResult
from voct.domain.ports import TranscriberPort


class WhisperTranscriber(TranscriberPort):
    """faster-whisperを使用した文字起こし実装。"""

    def transcribe(
        self,
        audio_path: Path,
        model_size: str = "base",
        language: str | None = None,
    ) -> TranscriptionResult:
        t0 = time.perf_counter()
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        t1 = time.perf_counter()
        model_load_time = t1 - t0

        transcribe_kwargs: dict = {"vad_filter": True}
        if language is not None:
            transcribe_kwargs["language"] = language

        t2 = time.perf_counter()
        segments, info = model.transcribe(str(audio_path), **transcribe_kwargs)
        text = "".join(seg.text for seg in segments)
        t3 = time.perf_counter()
        transcription_time = t3 - t2

        return TranscriptionResult(
            text=text,
            language=info.language,
            language_probability=info.language_probability,
            duration_seconds=info.duration,
            model_load_time_seconds=model_load_time,
            transcription_time_seconds=transcription_time,
        )
