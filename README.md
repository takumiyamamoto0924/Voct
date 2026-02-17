# Voct

ローカル完結型の CLI 音声入力支援ツール。マイクから音声を録音し、[faster-whisper](https://github.com/SYSTRAN/faster-whisper) でテキストに変換して標準出力に表示します。

外部 API（クラウド）を一切使用せず、すべての音声認識処理をローカルマシン内で完結させます。

## 機能

- マイクからの音声録音（Enter キーまたはタイムアウトで停止）
- faster-whisper による高速なローカル文字起こし（日本語対応）
- 録音開始・終了時のビープ音通知（カスタム音声ファイルに変更可能）
- モデルロード時間・推論時間のパフォーマンス計測表示

## 必要環境

- [mise](https://mise.jdx.dev/)（Python, uv, go-task を自動管理）
- macOS または Linux
- マイクデバイス

## セットアップ

```bash
mise install   # Python 3.12, uv, go-task をインストール
task setup     # 依存パッケージをインストール
```

## 使い方

```bash
task app:run
```

実行すると即座に録音が開始されます。Enter キーを押すか、5 秒経過で録音が停止し、文字起こし結果が表示されます。

```
[Voct] 録音を開始します... (Enterキーで停止、または5秒でタイムアウト)
[Voct] 録音完了: 3.2秒
[Voct] モデルロード時間: 1.5秒
[Voct] 文字起こし時間: 0.8秒 (録音時間比: 0.25x)
[Voct] 結果:
こんにちは、今日はいい天気ですね。
```

## 開発

```bash
task                # 利用可能なタスク一覧を表示
task app:debug      # デバッグモードで実行
task test           # テスト実行
task lint           # リンター実行
task lint:fix       # リンター自動修正
task format         # コードフォーマット
task format:check   # フォーマット差分確認
```

## プロジェクト構成

```
src/voct/
├── main.py                  # CLI エントリーポイント
├── domain/
│   ├── entities.py          # データモデル定義
│   └── ports.py             # 抽象インターフェース
├── usecase/
│   └── record_and_transcribe.py  # ユースケース
└── infra/
    ├── sounddevice_recorder.py   # 録音実装
    ├── wav_file_repository.py    # WAV ファイル I/O
    ├── whisper_transcriber.py    # 文字起こし実装
    └── sounddevice_notifier.py   # ビープ音通知
```

## 技術スタック

| パッケージ | 用途 |
|-----------|------|
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | ローカル音声認識（STT） |
| [sounddevice](https://python-sounddevice.readthedocs.io/) | マイク録音・音声再生 |
| [soundfile](https://python-soundfile.readthedocs.io/) | WAV ファイル読み書き |
| numpy | 音声データ操作・ビープ音生成 |

## ライセンス

MIT
