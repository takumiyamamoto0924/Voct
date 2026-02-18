"""タスク 2.1: TriggerKey, PushToTalkConfig, PushToTalkResult のテスト。"""

from pathlib import Path

import pytest

from voct.domain.entities import (
    NotificationConfig,
    PushToTalkConfig,
    PushToTalkResult,
    RecordingConfig,
    TriggerKey,
    TranscriptionResult,
)


def test_trigger_key_has_all_members():
    expected_keys = {"ENTER", "RIGHT_ALT", "LEFT_ALT", "RIGHT_CTRL", "LEFT_CTRL", "F1", "F2"}
    actual_keys = {member.name for member in TriggerKey}
    assert actual_keys == expected_keys


def test_trigger_key_values():
    assert TriggerKey.ENTER.value == "enter"
    assert TriggerKey.RIGHT_ALT.value == "alt_r"
    assert TriggerKey.LEFT_ALT.value == "alt"
    assert TriggerKey.RIGHT_CTRL.value == "ctrl_r"
    assert TriggerKey.LEFT_CTRL.value == "ctrl"
    assert TriggerKey.F1.value == "f1"
    assert TriggerKey.F2.value == "f2"


def test_push_to_talk_config_defaults():
    config = PushToTalkConfig()
    assert config.trigger_key == TriggerKey.ENTER
    assert config.model_size == "base"
    assert config.language is None
    assert config.output_dir is None
    assert config.filename_format == "%Y%m%d-%H%M%S"
    assert config.min_recording_seconds == 0.5
    assert isinstance(config.recording_config, RecordingConfig)
    assert isinstance(config.notification_config, NotificationConfig)


def test_push_to_talk_config_custom_values():
    config = PushToTalkConfig(
        trigger_key=TriggerKey.F1,
        model_size="large",
        language="ja",
        output_dir=Path("/tmp/transcripts"),
        filename_format="%Y-%m-%d",
        min_recording_seconds=1.0,
    )
    assert config.trigger_key == TriggerKey.F1
    assert config.model_size == "large"
    assert config.language == "ja"
    assert config.output_dir == Path("/tmp/transcripts")
    assert config.filename_format == "%Y-%m-%d"
    assert config.min_recording_seconds == 1.0


def test_push_to_talk_config_is_frozen():
    config = PushToTalkConfig()
    with pytest.raises(Exception):  # frozen=True なので代入不可
        config.trigger_key = TriggerKey.F2  # type: ignore[misc]


def test_push_to_talk_result_instantiation():
    result = PushToTalkResult(
        text="こんにちは",
        recording_duration_seconds=1.5,
        transcription_result=None,
        saved_file=None,
    )
    assert result.text == "こんにちは"
    assert result.recording_duration_seconds == 1.5
    assert result.transcription_result is None
    assert result.saved_file is None


def test_push_to_talk_result_with_optional_fields():
    import numpy as np
    tr = TranscriptionResult(
        text="hello",
        language="en",
        language_probability=0.99,
        duration_seconds=1.0,
        model_load_time_seconds=0.5,
        transcription_time_seconds=0.3,
    )
    result = PushToTalkResult(
        text="hello",
        recording_duration_seconds=1.0,
        transcription_result=tr,
        saved_file=Path("/tmp/out.md"),
    )
    assert result.transcription_result is tr
    assert result.saved_file == Path("/tmp/out.md")


def test_push_to_talk_result_is_frozen():
    result = PushToTalkResult(
        text="x",
        recording_duration_seconds=0.0,
        transcription_result=None,
        saved_file=None,
    )
    with pytest.raises(Exception):
        result.text = "y"  # type: ignore[misc]
