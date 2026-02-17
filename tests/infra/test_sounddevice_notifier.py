from unittest.mock import MagicMock, patch

import numpy as np

from voct.domain.entities import NotificationConfig
from voct.infra.sounddevice_notifier import SoundDeviceNotifier


class TestSoundDeviceNotifier:
    @patch("voct.infra.sounddevice_notifier.sd")
    def test_play_start_sound_default_calls_play(self, mock_sd):
        notifier = SoundDeviceNotifier()
        config = NotificationConfig()

        notifier.play_start_sound(config)

        mock_sd.play.assert_called_once()
        mock_sd.wait.assert_called_once()

    @patch("voct.infra.sounddevice_notifier.sd")
    def test_play_start_sound_default_uses_880hz(self, mock_sd):
        notifier = SoundDeviceNotifier()
        config = NotificationConfig()

        notifier.play_start_sound(config)

        played_data = mock_sd.play.call_args[0][0]
        assert isinstance(played_data, np.ndarray)
        assert played_data.dtype == np.float32
        assert len(played_data) > 0

    @patch("voct.infra.sounddevice_notifier.sd")
    def test_play_stop_sound_default_calls_play(self, mock_sd):
        notifier = SoundDeviceNotifier()
        config = NotificationConfig()

        notifier.play_stop_sound(config)

        mock_sd.play.assert_called_once()
        mock_sd.wait.assert_called_once()

    @patch("voct.infra.sounddevice_notifier.sd")
    def test_start_and_stop_sounds_differ(self, mock_sd):
        notifier = SoundDeviceNotifier()
        config = NotificationConfig()

        notifier.play_start_sound(config)
        start_data = mock_sd.play.call_args[0][0].copy()

        mock_sd.reset_mock()

        notifier.play_stop_sound(config)
        stop_data = mock_sd.play.call_args[0][0]

        assert not np.array_equal(start_data, stop_data)

    @patch("voct.infra.sounddevice_notifier.sf")
    @patch("voct.infra.sounddevice_notifier.sd")
    def test_play_start_sound_custom_file(self, mock_sd, mock_sf):
        mock_sf.read.return_value = (np.zeros(1000, dtype=np.float32), 44100)
        notifier = SoundDeviceNotifier()
        config = NotificationConfig(start_sound_path="/path/to/start.wav")

        notifier.play_start_sound(config)

        mock_sf.read.assert_called_once_with("/path/to/start.wav", dtype="float32")
        mock_sd.play.assert_called_once()
        mock_sd.wait.assert_called_once()

    @patch("voct.infra.sounddevice_notifier.sf")
    @patch("voct.infra.sounddevice_notifier.sd")
    def test_play_stop_sound_custom_file(self, mock_sd, mock_sf):
        mock_sf.read.return_value = (np.zeros(1000, dtype=np.float32), 44100)
        notifier = SoundDeviceNotifier()
        config = NotificationConfig(stop_sound_path="/path/to/stop.wav")

        notifier.play_stop_sound(config)

        mock_sf.read.assert_called_once_with("/path/to/stop.wav", dtype="float32")
        mock_sd.play.assert_called_once()
        mock_sd.wait.assert_called_once()
