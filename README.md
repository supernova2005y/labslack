# 当番お知らせbot (labslack)

研究室の週当番を、毎週月曜 9:00(日本時間)に Slack へ自動投稿する bot です。

- チャンネルに「今週の当番は ○○さんと △△さんです!」と投稿
- そのスレッドに当番の仕事内容を追記

## しくみ

```
cron-job.org (毎週月曜 9:00)
   │  GitHub API で workflow_dispatch を呼ぶ
   ▼
GitHub Actions (.github/workflows/cron.yml)
   │  python toban_bot.py
   ▼
Slack に投稿
```

GitHub Actions の `schedule` は実行が遅れたり飛ばされたりすることがあるため、起動は外部の [cron-job.org](https://cron-job.org) に任せています。

## 当番の決め方

ISO 週番号(月曜始まり)をメンバー数で割った余りで、2つのグループからそれぞれ1人ずつ選びます。週が変わるたびに名簿の順番どおりにローテーションします。

## 設定

### GitHub Secrets

リポジトリの Settings → Secrets and variables → Actions に登録します。名簿もここに入れるので、コードには個人名を書きません。

| 名前 | 内容 |
| --- | --- |
| `SLACK_BOT_TOKEN` | Slack Bot のトークン(`xoxb-...`)。`chat:write` 権限が必要で、bot を投稿先チャンネルに招待しておくこと |
| `TOBAN_MEMBERS1` | グループ1の名簿。カンマ区切り(例: `山田,佐藤,鈴木`) |
| `TOBAN_MEMBERS2` | グループ2の名簿。カンマ区切り |

投稿先チャンネルは [toban_bot.py](toban_bot.py) の `CHANNEL_ID` で指定しています。

### cron-job.org

| 項目 | 値 |
| --- | --- |
| URL | `https://api.github.com/repos/supernova2005y/labslack/actions/workflows/cron.yml/dispatches` |
| メソッド | `POST` |
| ヘッダー | `Authorization: Bearer <GitHubトークン>`<br>`Accept: application/vnd.github+json` |
| ボディ | `{"ref":"main"}` |
| スケジュール | 毎週月曜 9:00 (Asia/Tokyo) |

成功すると `204 No Content` が返ります。

GitHub トークンは Fine-grained personal access token で作成します。

- Repository access: Only select repositories → `labslack`
- Permissions: **Actions** を追加して **Read and write**(Metadata: Read は自動で付く)

## 手動で実行する

GitHub の Actions タブ → Weekly Toban Bot → Run workflow、または

```sh
gh workflow run cron.yml
```

## 投稿されないとき

1. `gh run list` で、その週の実行があるか確認する
2. 実行がなければ、cron-job.org の History を見る
   - **401 Unauthorized** → GitHub トークンの期限切れ。新しいトークンを作り、cron-job.org のヘッダーを差し替える
   - 履歴自体がない → ジョブが無効になっていないか確認する(失敗が続くと自動で無効化される)
3. 実行はあるのに投稿がなければ、Actions のログで Slack のエラーを確認する
