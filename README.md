# LeetCode Journey

LeetCode の解答を難易度別に管理するリポジトリです。

## Statistics

<!-- STATS:START -->
```text
LeetCode Progress Report
========================
Easy   : 0
Medium : 0
Hard   : 0
------------------------
Total  : 0
```

```mermaid
flowchart TD
    N[No solutions recorded yet]
    N --> A[Add files to easy/]
    N --> B[Add files to medium/]
    N --> C[Add files to hard/]
```

```mermaid
pie showData
    title Sample Visualization
    "Easy" : 3
    "Medium" : 2
    "Hard" : 1
```
<!-- STATS:END -->

## Structure

- `easy/`: Easy 問題の解答
- `medium/`: Medium 問題の解答
- `hard/`: Hard 問題の解答
- `scripts/`: 統計更新スクリプト

## Add a Solution

1. 対応する難易度ディレクトリに解答ファイルを追加する（例: `easy/two_sum.py`）。
2. 問題名が分かるファイル名にする。
3. `main` への push 後、GitHub Actions が統計を自動更新する。
