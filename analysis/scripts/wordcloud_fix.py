import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import matplotlib.font_manager as fm

# フォント設定
plt.rcParams['font.family'] = 'Hiragino Sans'

# 日本語フォントのパスを指定
# macOSの場合の一般的な日本語フォントパス
font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc'  # または適切なパスに変更

# データ読み込み
data_folder = os.path.join("..", "data")
jp_file_path = os.path.join(data_folder, "remote_work_data_jp_20250329_165210.csv")
en_file_path = os.path.join(data_folder, "remote_work_data_en_20250329_165210.csv")

df_jp = pd.read_csv(jp_file_path)
df_en = pd.read_csv(en_file_path)

# トピックごとのキーワード（前の分析で使用したもの）
topic_labels = {
    0: "コミュニケーション課題と解決策",
    1: "生産性と働き方改革",
    2: "テレワーク環境整備とツール活用",
    3: "リモートワークのメリットとデメリット",
    4: "チームマネジメントと信頼構築"
}

# ダミーのトピックキーワードデータ（実際のデータに置き換える）
topic_keywords = {
    0: {"communication": 10.0, "team": 8.5, "slack": 7.8, "meetings": 6.5, "tools": 6.0, 
        "コミュニケーション": 9.8, "チーム": 8.2, "ツール": 7.5, "会議": 6.8, "対策": 6.2},
    1: {"生産性": 9.5, "テレワーク": 9.0, "働き方改革": 8.5, "効率": 7.8, "microsoft": 7.5, 
        "productivity": 8.9, "work": 8.0, "efficiency": 7.7, "management": 7.0, "performance": 6.8},
    2: {"ツール": 9.7, "環境": 9.0, "設備": 8.5, "システム": 8.0, "整備": 7.5,
        "tools": 9.2, "setup": 8.8, "equipment": 8.3, "system": 7.9, "digital": 7.6},
    3: {"メリット": 9.7, "デメリット": 9.5, "リモートワーク": 9.0, "在宅勤務": 8.5, "比較": 8.0,
        "benefits": 9.3, "challenges": 9.0, "remote work": 8.8, "comparison": 8.0, "balance": 7.6},
    4: {"チーム": 9.8, "マネジメント": 9.5, "信頼": 9.0, "管理": 8.5, "リーダーシップ": 8.0,
        "team": 9.6, "management": 9.2, "trust": 8.9, "leadership": 8.7, "collaboration": 8.3}
}

# 各トピックのワードクラウドを生成
plt.figure(figsize=(20, 15))

for i, topic_idx in enumerate(range(5)):
    plt.subplot(2, 3, i+1)
    
    # WordCloudを生成（日本語フォントを指定）
    wordcloud = WordCloud(
        font_path=font_path,  # 日本語フォントを明示的に指定
        width=800, 
        height=800,
        background_color='white',
        max_words=100,
        prefer_horizontal=1.0
    ).generate_from_frequencies(topic_keywords[topic_idx])
    
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f"トピック {i+1}: {topic_labels[topic_idx]}", fontsize=16, fontfamily='Hiragino Sans')

plt.tight_layout()
plt.savefig('topic_wordclouds_fixed.png', dpi=150)
plt.close()

print("ワードクラウドを生成しました。'topic_wordclouds_fixed.png'を確認してください。")