import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
import numpy as np

# フォント設定
plt.rcParams['font.family'] = 'Hiragino Sans'

# カラーパレット設定
colors = sns.color_palette("colorblind")

# データフォルダのパス
data_folder = os.path.join("..", "data")
file_path = os.path.join(data_folder, "remote_work_data_en_20250329_165210.csv")

# ファイルの読み込み
print(f"ファイルパス: {file_path}")
print(f"ファイルが存在する: {os.path.exists(file_path)}")

df_en = pd.read_csv(file_path)

# 1. 基本的な情報確認
print(f"\n英語データセットの形状（行 x 列）: {df_en.shape}")
print("\n列の情報:")
print(df_en.info())

# 2. 欠損値の確認
print("\n欠損値の数:")
print(df_en.isnull().sum())

# 3. コンテンツの長さ分析
df_en['title_length'] = df_en['title'].str.len().fillna(0)
df_en['content_length'] = df_en['content'].str.len().fillna(0)
df_en['word_count'] = df_en['content'].fillna('').apply(lambda x: len(str(x).split()))

print("\nコンテンツ長の基本統計:")
print(df_en['content_length'].describe())

print("\n単語数の基本統計:")
print(df_en['word_count'].describe())

# 4. コンテンツ長の分布をヒストグラムで可視化
plt.figure(figsize=(10, 6))
plt.hist(df_en['content_length'], bins=10, alpha=0.7, color=colors[0])
plt.title('英語コンテンツの長さ分布')
plt.xlabel('文字数')
plt.ylabel('記事数')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('en_content_length_distribution.png', dpi=150)
plt.close()

# 5. 単語数の分布
plt.figure(figsize=(10, 6))
plt.hist(df_en['word_count'], bins=10, alpha=0.7, color=colors[1])
plt.title('英語コンテンツの単語数分布')
plt.xlabel('単語数')
plt.ylabel('記事数')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('en_word_count_distribution.png', dpi=150)
plt.close()

# 6. 頻出単語の分析
def preprocess_text(text):
    if isinstance(text, str):
        # 小文字に変換し、英数字以外を削除
        text = re.sub(r'[^\w\s]', '', text.lower())
        # ストップワード除去
        stop_words = ['and', 'the', 'to', 'of', 'in', 'a', 'for', 'is', 'on', 'with', 'are', 'that', 'be', 'by', 'as', 'at', 'it',
                      'this', 'their', 'from', 'or', 'an', 'they', 'have', 'has', 'had', 'you', 'your', 'can', 'will', 'our']
        return ' '.join([word for word in text.split() if word not in stop_words and len(word) > 2])
    return ""

# タイトルからの頻出単語
title_words = []
for title in df_en['title'].fillna(''):
    title_words.extend(preprocess_text(title).split())

title_word_counts = Counter(title_words).most_common(15)
print("\n英語タイトルの頻出単語:")
for word, count in title_word_counts:
    print(f"- {word}: {count}回")

# 頻出単語の棒グラフ
plt.figure(figsize=(12, 6))
words = [word for word, count in title_word_counts]
counts = [count for word, count in title_word_counts]
bars = plt.barh(words, counts, color=colors[2])
for i, bar in enumerate(bars):
    bar.set_hatch('////')
plt.title('英語タイトルの頻出単語 TOP 15')
plt.xlabel('出現回数')
plt.ylabel('単語')
plt.tight_layout()
plt.savefig('en_title_top_words.png', dpi=150)
plt.close()

print("\n英語データの基本分析が完了しました")