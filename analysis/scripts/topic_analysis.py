import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# フォント設定
plt.rcParams['font.family'] = 'Hiragino Sans'

# カラーパレット設定
colors = sns.color_palette("colorblind")

# データフォルダのパス
data_folder = os.path.join("..", "data")
file_path = os.path.join(data_folder, "remote_work_all_data_20250329_165210.csv")

# ファイルの読み込み
df_all = pd.read_csv(file_path)

# 言語ごとにデータを分離
df_en = df_all[df_all['language'] == 'en']
df_ja = df_all[df_all['language'] == 'ja']

# 前処理関数 - 拡張版
def preprocess_text(text, language='en'):
    if not isinstance(text, str):
        return ""
    
    # 小文字に変換
    text = text.lower()
    
    # 英語の場合
    if language == 'en':
        # 英数字と空白以外を削除
        text = re.sub(r'[^\w\s]', ' ', text)
        # 拡張ストップワード
        stop_words = ['and', 'the', 'to', 'of', 'in', 'a', 'for', 'is', 'on', 'with', 'are', 'that', 'be', 'by', 'as', 'at', 'it',
                      'this', 'their', 'from', 'or', 'an', 'they', 'have', 'has', 'had', 'you', 'your', 'can', 'will', 'our']
    # 日本語の場合 (簡易的な処理)
    else:
        # 特殊文字を削除
        text = re.sub(r'[^\w\s]', ' ', text)
        # 日本語のストップワード (例)
        stop_words = ['を', 'に', 'は', 'が', 'の', 'と', 'た', 'して', 'です', 'ます', 'から', 'など', 'による']
    
    # ストップワードの除去とトークン化
    return ' '.join([word for word in text.split() if word not in stop_words and len(word) > 2])

# 英語データのトピックモデリング
print("英語コンテンツのトピックモデリング:")
en_contents = df_en['content'].fillna('').apply(lambda x: preprocess_text(x, 'en'))

# TF-IDFベクトル化 (改良版パラメータ)
en_tfidf_vectorizer = TfidfVectorizer(max_features=100, min_df=1, max_df=0.9)
en_tfidf_matrix = en_tfidf_vectorizer.fit_transform(en_contents)

# 最適なトピック数を2に設定
n_topics = 2
en_lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=20)
en_lda.fit(en_tfidf_matrix)

# 各トピックの上位単語を表示
en_feature_names = en_tfidf_vectorizer.get_feature_names_out()
en_top_words_per_topic = []

for topic_idx, topic in enumerate(en_lda.components_):
    top_words_idx = topic.argsort()[:-11:-1]  # 上位10単語
    top_words = [en_feature_names[i] for i in top_words_idx]
    en_top_words_per_topic.append(top_words)
    print(f"英語トピック {topic_idx+1}: {', '.join(top_words)}")

# 可視化 - 英語トピック
plt.figure(figsize=(12, 8))
for i, words in enumerate(en_top_words_per_topic):
    plt.subplot(1, n_topics, i + 1)
    y_pos = np.arange(len(words))
    weights = en_lda.components_[i][en_lda.components_[i].argsort()[:-11:-1]]
    bars = plt.barh(y_pos, weights, color=colors[i])
    
    # パターンを追加
    for bar in bars:
        bar.set_hatch('////' if i % 2 == 0 else 'xxxx')
    
    plt.yticks(y_pos, words)
    plt.title(f'英語トピック {i+1} の主要単語')
    plt.gca().invert_yaxis()  # 最大値を上に

plt.tight_layout()
plt.savefig('en_topics_analysis.png', dpi=150)
plt.close()

# 日本語データも十分な量があれば、同様のトピックモデリングを実施
if len(df_ja) >= 5:  # 少なくとも5件あれば分析を実施
    print("\n日本語コンテンツのトピックモデリング:")
    ja_contents = df_ja['content'].fillna('').apply(lambda x: preprocess_text(x, 'ja'))
    
    # 日本語用のベクトル化 (パラメータ調整)
    ja_tfidf_vectorizer = TfidfVectorizer(max_features=100, min_df=1)
    ja_tfidf_matrix = ja_tfidf_vectorizer.fit_transform(ja_contents)
    
    # トピック数は1か2に (データ量による)
    ja_n_topics = min(2, len(df_ja) // 3)  # データ量に応じて調整
    if ja_n_topics > 0:
        ja_lda = LatentDirichletAllocation(n_components=ja_n_topics, random_state=42)
        ja_lda.fit(ja_tfidf_matrix)
        
        # 各トピックの上位単語を表示
        ja_feature_names = ja_tfidf_vectorizer.get_feature_names_out()
        ja_top_words_per_topic = []
        
        for topic_idx, topic in enumerate(ja_lda.components_):
            top_words_idx = topic.argsort()[:-11:-1]  # 上位10単語
            top_words = [ja_feature_names[i] for i in top_words_idx]
            ja_top_words_per_topic.append(top_words)
            print(f"日本語トピック {topic_idx+1}: {', '.join(top_words)}")
        
        # 可視化 - 日本語トピック
        plt.figure(figsize=(12, 8))
        for i, words in enumerate(ja_top_words_per_topic):
            plt.subplot(1, ja_n_topics, i + 1)
            y_pos = np.arange(len(words))
            weights = ja_lda.components_[i][ja_lda.components_[i].argsort()[:-11:-1]]
            bars = plt.barh(y_pos, weights, color=colors[i+2])  # 色は英語と被らないよう調整
            
            # パターンを追加
            for bar in bars:
                bar.set_hatch('\\\\\\' if i % 2 == 0 else 'ooo')
            
            plt.yticks(y_pos, words)
            plt.title(f'日本語トピック {i+1} の主要単語')
            plt.gca().invert_yaxis()
            
        plt.tight_layout()
        plt.savefig('ja_topics_analysis.png', dpi=150)
        plt.close()
    else:
        print("日本語データが少なすぎるためトピックモデリングをスキップします")
else:
    print("日本語データが少なすぎるためトピックモデリングをスキップします")

print("\n改善版トピックモデリング分析が完了しました")