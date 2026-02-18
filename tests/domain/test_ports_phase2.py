"""タスク 2.2: PushToTalkRecorderPort, HotkeyListenerPort, ClipboardPort, TranscriptFilePort のテスト。"""

import inspect
from pathlib import Path

import pytest

from voct.domain.ports import (
    ClipboardPort,
    HotkeyListenerPort,
    PushToTalkRecorderPort,
    TranscriptFilePort,
)


def test_push_to_talk_recorder_port_is_abstract():
    with pytest.raises(TypeError):
        PushToTalkRecorderPort()  # type: ignore[abstract]


def test_push_to_talk_recorder_port_has_required_methods():
    abstract_methods = PushToTalkRecorderPort.__abstractmethods__
    assert "start_recording" in abstract_methods
    assert "stop_recording" in abstract_methods


def test_hotkey_listener_port_is_abstract():
    with pytest.raises(TypeError):
        HotkeyListenerPort()  # type: ignore[abstract]


def test_hotkey_listener_port_has_required_methods():
    abstract_methods = HotkeyListenerPort.__abstractmethods__
    assert "start" in abstract_methods
    assert "join" in abstract_methods
    assert "stop" in abstract_methods


def test_clipboard_port_is_abstract():
    with pytest.raises(TypeError):
        ClipboardPort()  # type: ignore[abstract]


def test_clipboard_port_has_required_methods():
    abstract_methods = ClipboardPort.__abstractmethods__
    assert "copy" in abstract_methods


def test_transcript_file_port_is_abstract():
    with pytest.raises(TypeError):
        TranscriptFilePort()  # type: ignore[abstract]


def test_transcript_file_port_has_required_methods():
    abstract_methods = TranscriptFilePort.__abstractmethods__
    assert "save" in abstract_methods


def test_push_to_talk_recorder_port_can_be_implemented():
    from voct.domain.entities import AudioData, RecordingConfig

    import numpy as np

    class ConcreteRecorder(PushToTalkRecorderPort):
        def start_recording(self, config: RecordingConfig) -> None:
            pass

        def stop_recording(self) -> AudioData:
            return AudioData(
                data=np.zeros(0, dtype=np.float32),
                sample_rate=16000,
                duration_seconds=0.0,
            )

    recorder = ConcreteRecorder()
    recorder.start_recording(RecordingConfig())
    result = recorder.stop_recording()
    assert isinstance(result, AudioData)


def test_clipboard_port_can_be_implemented():
    captured = []

    class ConcreteClipboard(ClipboardPort):
        def copy(self, text: str) -> None:
            captured.append(text)

    clipboard = ConcreteClipboard()
    clipboard.copy("hello")
    assert captured == ["hello"]


def test_transcript_file_port_can_be_implemented():
    class ConcreteTranscriptFile(TranscriptFilePort):
        def save(self, text: str, directory: Path, filename_format: str) -> Path:
            return directory / "out.md"

    tf = ConcreteTranscriptFile()
    result = tf.save("hello", Path("/tmp"), "%Y%m%d")
    assert result == Path("/tmp/out.md")
