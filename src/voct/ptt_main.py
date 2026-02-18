import sys
import termios

from voct.domain.entities import PushToTalkConfig
from voct.infra.markdown_transcript_file import MarkdownTranscriptFile
from voct.infra.push_to_talk_recorder import PushToTalkSoundDeviceRecorder
from voct.infra.pyperclip_clipboard import PyperclipClipboard
from voct.infra.pynput_hotkey_listener import PynputHotkeyListener
from voct.infra.sounddevice_notifier import SoundDeviceNotifier
from voct.infra.wav_file_repository import WavFileRepository
from voct.infra.whisper_transcriber import WhisperTranscriber
from voct.usecase.push_to_talk import PushToTalkUseCase


def _disable_echo() -> list | None:
    """ターミナルの文字エコーを無効化し、元の設定を返す。非ターミナル環境では None を返す。"""
    try:
        old = termios.tcgetattr(sys.stdin)
        new = list(old)
        new[3] &= ~termios.ECHO  # c_lflag の ECHO ビットをクリア
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new)
        return old
    except termios.error:
        return None


def _restore_echo(old_settings: list | None) -> None:
    """ターミナルのエコー設定を元に戻す。"""
    if old_settings is not None:
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except termios.error:
            pass


def ptt_main() -> None:
    recorder = PushToTalkSoundDeviceRecorder()
    audio_file = WavFileRepository()
    transcriber = WhisperTranscriber()
    clipboard = PyperclipClipboard()
    transcript_file = MarkdownTranscriptFile()
    notifier = SoundDeviceNotifier()
    listener = PynputHotkeyListener()

    usecase = PushToTalkUseCase(
        recorder, audio_file, transcriber,
        clipboard, transcript_file, notifier, listener,
    )
    config = PushToTalkConfig()

    old_settings = _disable_echo()
    try:
        usecase.run(config)
    finally:
        _restore_echo(old_settings)
