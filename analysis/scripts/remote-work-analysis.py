import os
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import Counter
import numpy as np
import seaborn as sns

# フォント設定
plt.rcParams['font.family'] = 'Hiragino Sans'

# カラーパレット設定
colors = sns.color_palette("colorblind")

# データフォルダのパス
data_folder = os.path.join(os.getcwd(), "data")

# CSVファイルの読み込み
file_path = os.path.join(data_folder, "remote_work_all_data_20250329_165210.csv")
df_all = pd.read_csv(file_path)

# 1. 基本的な統計 - 言語の分布
print("言語の分布:")
language_counts = df_all['language'].value_counts()
print(language_counts)

# 言語の分布を円グラフで表示
fig, ax = plt.subplots(figsize=(8, 6))
wedges, _, _ = ax.pie(language_counts, labels=language_counts.index, autopct='%1.1f%%')
# ハッチングパターンを追加
wedges[0].set_hatch('//////')
wedges[1].set_hatch('xxxxxx')  
plt.title('言語の分布')
plt.savefig('language_distribution_hatched.png', dpi=150)
plt.close()

# 2. テキスト長の分析
df_all['title_length'] = df_all['title'].str.len().fillna(0)
df_all['content_length'] = df_all['content'].str.len().fillna(0)

print("\nタイトル長の基本統計:")
print(df_all['title_length'].describe())

print("\nコンテンツ長の基本統計:")
print(df_all['content_length'].describe())

# テキスト長の分布をヒストグラムで表示
plt.figure(figsize=(10, 6))
plt.hist(df_all['content_length'], bins=10, alpha=0.7)
plt.title('コンテンツ長の分布')
plt.xlabel('文字数')
plt.ylabel('記事数')
plt.savefig('content_length_distribution.png', dpi=200)
plt.close()

# 3. キーワード分析
def extract_keywords(text):
    if isinstance(text, str):
        words = re.findall(r'\b\w+\b', text.lower())
        stop_words = ['and', 'the', 'to', 'of', 'in', 'a', 'for', 'is', 'on', 'with', 'are', 'that', 'be', 'by', 'as', 'at', 'it']
        return [w for w in words if w not in stop_words and len(w) > 2]
    return []

# タイトルから抽出
all_title_words = []
for title in df_all['title'].dropna():
    all_title_words.extend(extract_keywords(title))

title_word_counts = Counter(all_title_words)
print("\n最も頻出するタイトルの単語:")
print(title_word_counts.most_common(10))

# ここで top_words を定義
top_words = dict(title_word_counts.most_common(10))

# それから棒グラフを作成
plt.figure(figsize=(12, 6))
bars = plt.bar(top_words.keys(), top_words.values(), color=colors[0:len(top_words)])
# パターンを追加
for i, bar in enumerate(bars):
    if i % 2 == 0:
        bar.set_hatch('//////')
    else:
        bar.set_hatch('xxxxxx')
plt.title('タイトルの頻出単語 TOP 10')
plt.xlabel('単語')
plt.ylabel('出現回数')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('title_top_words_hatched.png', dpi=200)
plt.close()

print("\n分析が完了しました。グラフが保存されました。")