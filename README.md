# 📺 YouTube Playlist to README Generator

This GitHub Action generates a `README.md` based on a YouTube Playlist.

## Inputs

| Name | Description | Required |
|------|-------------|----------|
| `playlist_id` | ID of the YouTube playlist | ✅ |
| `api_key` | YouTube Data API key | ✅ |

## Example usage

```yaml
- uses: your-username/youtube-readme-action@v1
  with:
    playlist_id: ${{ secrets.PLAYLIST_ID }}
    api_key: ${{ secrets.API_KEY }}
```

key: ${{ secrets.API_KEY }}
Output
Creates/overwrites a README.md file in the repository root based on the playlist contents.

yaml
Копировать
Редактировать

---

## 📄 `.github/workflows/test.yml` — для CI и теста action

```yaml
name: Test Action

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Action
        uses: ./
        with:
          playlist_id: ${{ secrets.PLAYLIST_ID }}
          api_key: ${{ secrets.API_KEY }}
```
