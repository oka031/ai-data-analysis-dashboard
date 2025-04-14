# 言語別分析

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter


# カラーパレット設定
colors = sns.color_palette("colorblind")
# フォント設定
plt.rcParams['font.family'] = 'Hiragino Sans'

# データフォルダのパス
data_folder = os.path.join(os.getcwd(), "..", "data")
file_path = os.path.join(data_folder, "remote_work_all_data_20250329_165210.csv")
df_all = pd.read_csv(file_path)

# コンテンツの単語数を計算
df_all['word_count'] = df_all['content'].fillna('').apply(lambda x: len(str(x).split()))

# 言語ごとにデータを分離する
df_en = df_all[df_all['language'] == 'en']
df_ja = df_all[df_all['language'] == 'ja']

# 言語別の単語数統計
lang_word_stats = df_all.groupby('language')['word_count'].agg(['mean', 'median', 'min', 'max', 'std']).reset_index()
print("\n言語別単語数統計:")
print(lang_word_stats)

# 言語別の単語数分布
plt.figure(figsize=(10, 6))
sns.boxplot(x='language', y='word_count', data=df_all, palette="colorblind")
plt.title('言語別コンテンツの単語数分布')
plt.xlabel('言語')
plt.ylabel('単語数')
plt.savefig('language_wordcount_comparison.png', dpi=150)
plt.close()



# 前処理関数
def preprocess_text(text):
    if isinstance(text, str):
        # 小文字に変換し、英数字と空白以外を削除
        text = re.sub(r'[^\w\s]', '', text.lower())
        # ストップワード除去
        stop_words = ['and', 'the', 'to', 'of', 'in', 'a', 'for', 'is', 'on', 'with', 'are', 'that', 'be', 'by', 'as', 'at', 'it']
        return ' '.join([word for word in text.split() if word not in stop_words and len(word) > 2])
    return ""

# 言語別の共通キーワード比較
# 各言語ごとの頻出単語を抽出
en_content_words = []
ja_content_words = []

for content in df_en['content'].fillna(''):
    words = preprocess_text(content).split()
    en_content_words.extend(words)

for content in df_ja['content'].fillna(''):
    words = preprocess_text(content).split()
    ja_content_words.extend(words)

en_word_counts = Counter(en_content_words).most_common(15)
ja_word_counts = Counter(ja_content_words).most_common(15)

# 言語別頻出単語の比較グラフ
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# 英語の頻出単語
en_words = [word for word, count in en_word_counts]
en_counts = [count for word, count in en_word_counts]
bars1 = ax1.barh(range(len(en_words)), en_counts, color=colors[0])
for bar in bars1:
    bar.set_hatch('////')
ax1.set_yticks(range(len(en_words)))
ax1.set_yticklabels(en_words)
ax1.invert_yaxis()
ax1.set_title('英語コンテンツの頻出単語')

# 日本語の頻出単語
ja_words = [word for word, count in ja_word_counts]
ja_counts = [count for word, count in ja_word_counts]
bars2 = ax2.barh(range(len(ja_words)), ja_counts, color=colors[1])
for bar in bars2:
    bar.set_hatch('\\\\\\\\')
ax2.set_yticks(range(len(ja_words)))
ax2.set_yticklabels(ja_words)
ax2.invert_yaxis()
ax2.set_title('日本語コンテンツの頻出単語')

plt.tight_layout()
plt.savefig('language_keyword_comparison.png', dpi=150)
plt.close()