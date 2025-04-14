import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from textblob import TextBlob

# データ読み込み
data_folder = os.path.join("..", "data")
file_path = os.path.join(data_folder, "remote_work_data_en_20250329_165210.csv")
df_en = pd.read_csv(file_path)

# フォント設定
plt.rcParams['font.family'] = 'Hiragino Sans'

# 感情分析関数
def analyze_sentiment(text):
    if not isinstance(text, str) or text == '':
        return {'polarity': 0, 'subjectivity': 0}
    blob = TextBlob(text)
    return {'polarity': blob.sentiment.polarity, 'subjectivity': blob.sentiment.subjectivity}

# ソリューション指向度を評価する関数
def solution_orientation(text):
    if not isinstance(text, str) or text == '':
        return 0
    
    # ソリューション関連キーワード
    solution_words = ['solution', 'solve', 'resolve', 'fix', 'improve', 'enhance', 
                      'strategy', 'approach', 'method', 'tool', 'technique', 'tip', 
                      'best practice', 'recommendation', 'advice', 'guide', 'how to']
    
    # 問題関連キーワード
    problem_words = ['problem', 'challenge', 'issue', 'difficulty', 'obstacle', 
                     'barrier', 'struggle', 'concern', 'risk', 'limitation']
    
    text_lower = text.lower()
    
    # キーワード出現回数をカウント
    solution_count = sum(text_lower.count(word) for word in solution_words)
    problem_count = sum(text_lower.count(word) for word in problem_words)
    
    # 総単語数に対する比率を計算
    total_words = len(text.split())
    
    # ソリューション指向度スコア（-1〜1の範囲）
    if problem_count + solution_count == 0:
        return 0
    
    solution_ratio = solution_count / (problem_count + solution_count)
    return (solution_ratio - 0.5) * 2  # -1〜1のスケールに変換

# 記事ごとの感情分析とソリューション指向度の評価
sentiments = []
solution_scores = []
titles = []

for i, row in df_en.iterrows():
    if isinstance(row['content'], str) and row['content'] != '':
        sentiment = analyze_sentiment(row['content'])
        solution_score = solution_orientation(row['content'])
        
        sentiments.append(sentiment)
        solution_scores.append(solution_score)
        titles.append(row['title'] if isinstance(row['title'], str) else '')

# 結果をデータフレームに
analysis_df = pd.DataFrame({
    'title': titles,
    'polarity': [s['polarity'] for s in sentiments],
    'subjectivity': [s['subjectivity'] for s in sentiments],
    'solution_score': solution_scores
})

print("記事ごとの感情分析とソリューション指向度:")
print(analysis_df)

# ソリューション指向度と感情極性の散布図
plt.figure(figsize=(10, 6))
plt.scatter(analysis_df['solution_score'], analysis_df['polarity'], 
            alpha=0.7, s=100, c=analysis_df['subjectivity'], cmap='viridis')

plt.colorbar(label='主観性スコア')
plt.title('リモートワーク記事のソリューション指向度と感情極性')
plt.xlabel('ソリューション指向度 (-1=問題中心, 1=解決策中心)')
plt.ylabel('感情極性 (-1=ネガティブ, 1=ポジティブ)')
plt.grid(alpha=0.3)
plt.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle='-', alpha=0.5)

# プロット上に記事タイトルを表示（短縮版）
for i, txt in enumerate(analysis_df['title']):
    short_title = txt[:20] + '...' if len(txt) > 20 else txt
    plt.annotate(short_title, 
                (analysis_df['solution_score'].iloc[i], analysis_df['polarity'].iloc[i]),
                fontsize=8, alpha=0.7)

plt.tight_layout()
plt.savefig('sentiment_solution_analysis.png', dpi=150)
plt.close()

# 集計統計
print("\n全体の統計:")
print(f"平均感情極性: {analysis_df['polarity'].mean():.3f} (-1=ネガティブ, 1=ポジティブ)")
print(f"平均主観性: {analysis_df['subjectivity'].mean():.3f} (0=客観的, 1=主観的)")
print(f"平均ソリューション指向度: {analysis_df['solution_score'].mean():.3f} (-1=問題中心, 1=解決策中心)")