import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.font_manager as fm
import japanize_matplotlib

# データの読み込み
jp_data_file = 'remote_work_data_jp_20250329_165210.csv'
df_jp = pd.read_csv(jp_data_file)
print(f"日本語データ: {df_jp.shape[0]}行, {df_jp.shape[1]}列")

# 欠損値の処理
print(f"コンテンツ欠損数: {df_jp['content'].isnull().sum()}")
df_jp = df_jp.dropna(subset=['content'])
print(f"欠損値除去後: {df_jp.shape[0]}行")

# テキストクリーニング関数
def clean_text(text):
    if isinstance(text, str):
        # HTML タグの除去
        text = re.sub(r'<.*?>', '', text)
        # 特殊文字の除去（日本語は保持）
        text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', '', text)
        # 複数の空白を1つに置換
        text = re.sub(r'\s+', ' ', text)
        return text
    return ''

# テキストをクリーニング
df_jp['cleaned_content'] = df_jp['content'].apply(clean_text)

# キーワード検索関数
def count_keyword_occurrences(text, keywords):
    if not isinstance(text, str):
        return {k: 0 for k in keywords}
    
    counts = {}
    for keyword in keywords:
        counts[keyword] = text.count(keyword)
    return counts

# リモートワーク関連キーワード（日本語）
remote_keywords_jp = [
    'リモートワーク', 'テレワーク', '在宅勤務', 'リモート', '在宅', 
    'オンライン会議', 'ビデオ会議', 'バーチャルオフィス', '分散型チーム'
]

# 生産性関連キーワード（日本語）
productivity_keywords_jp = [
    '生産性', '効率', 'パフォーマンス', '成果', '結果',
    'タイムマネジメント', 'ワークライフバランス', '集中', '注意散漫',
    'コミュニケーション', 'コラボレーション', '会議', 'スケジュール'
]

# 最適化関連キーワード（日本語）
optimization_keywords_jp = [
    '最適化', '改善', '戦略', 'ベストプラクティス', '効果的',
    '解決策', '課題', 'メリット', 'デメリット', 'バランス',
    'ハイブリッド', '柔軟', 'スケジュール', '環境'
]

# キーワード出現回数を計算
print("\nキーワード分析を実行中...")
remote_counts_jp = df_jp['cleaned_content'].apply(lambda x: count_keyword_occurrences(x, remote_keywords_jp))
productivity_counts_jp = df_jp['cleaned_content'].apply(lambda x: count_keyword_occurrences(x, productivity_keywords_jp))
optimization_counts_jp = df_jp['cleaned_content'].apply(lambda x: count_keyword_occurrences(x, optimization_keywords_jp))

# データフレームに変換
remote_df_jp = pd.DataFrame(remote_counts_jp.tolist())
productivity_df_jp = pd.DataFrame(productivity_counts_jp.tolist())
optimization_df_jp = pd.DataFrame(optimization_counts_jp.tolist())

# キーワードの総出現回数
print("\nリモートワーク関連キーワードの出現回数（日本語）:")
print(remote_df_jp.sum().sort_values(ascending=False))

print("\n生産性関連キーワードの出現回数（日本語）:")
print(productivity_df_jp.sum().sort_values(ascending=False))

print("\n最適化関連キーワードの出現回数（日本語）:")
print(optimization_df_jp.sum().sort_values(ascending=False))

# 簡易的な日本語テキスト分析（単語単位ではなく文字単位）
def count_characters(texts, n=30):
    # 日本語の文字だけを抽出
    jp_chars = []
    for text in texts:
        if isinstance(text, str):
            # 半角スペース、数字、アルファベットを除去
            cleaned = re.sub(r'[\s0-9a-zA-Z]', '', text)
            jp_chars.extend(list(cleaned))
    
    # 文字カウント
    char_counts = Counter(jp_chars)
    return char_counts.most_common(n)

# 頻出文字を抽出（参考情報として）
top_chars = count_characters(df_jp['cleaned_content'], n=30)
print("\n頻出文字（上位30、参考情報）:")
for char, count in top_chars:
    if len(char.strip()) > 0:  # 空白文字は除外
        print(f"{char}: {count}")

# タイトルからの情報抽出
print("\nタイトル分析:")
for title in df_jp['title'].dropna():
    print(f"- {title}")

# 記事の主題を分類（簡易版）
def classify_article(text, keyword_sets):
    if not isinstance(text, str):
        return "不明"
    
    scores = {}
    for category, keywords in keyword_sets.items():
        score = sum(text.count(keyword) for keyword in keywords)
        scores[category] = score
    
    max_category = max(scores.items(), key=lambda x: x[1])
    if max_category[1] > 0:
        return max_category[0]
    return "その他"

# キーワードセット
keyword_sets = {
    'コミュニケーション': ['コミュニケーション', '会議', 'チャット', '連絡', '情報共有'],
    '生産性向上': ['生産性', '効率', 'パフォーマンス', '成果', '向上'],
    '課題解決': ['課題', '問題', '解決', 'デメリット', '対策'],
    'ツール活用': ['ツール', 'アプリ', 'システム', 'ソフトウェア', 'プラットフォーム'],
    'マネジメント': ['マネジメント', '管理', 'リーダー', '評価', '監督']
}

# 記事を分類
df_jp['category'] = df_jp['cleaned_content'].apply(lambda x: classify_article(x, keyword_sets))
print("\n記事のカテゴリ分布:")
print(df_jp['category'].value_counts())

# カテゴリの可視化
plt.figure(figsize=(10, 6))
sns.countplot(y='category', data=df_jp)
plt.title('日本語記事のカテゴリ分布')
plt.xlabel('記事数')
plt.ylabel('カテゴリ')
plt.savefig('jp_article_categories.png')
plt.close()

# よく出現する単語のペア（共起関係）を分析
def find_cooccurring_terms(texts, target_terms, window=10):
    cooccurrences = {}
    for term in target_terms:
        cooccurrences[term] = Counter()
    
    for text in texts:
        if not isinstance(text, str):
            continue
        
        for term in target_terms:
            # 対象単語が文中に出現する位置を全て見つける
            positions = [m.start() for m in re.finditer(term, text)]
            for pos in positions:
                # 前後の文字列をウィンドウサイズ分取得
                start = max(0, pos - window)
                end = min(len(text), pos + len(term) + window)
                context = text[start:end]
                
                # 他のターゲット単語がコンテキスト内にあるか確認
                for other_term in target_terms:
                    if other_term != term and other_term in context:
                        cooccurrences[term][other_term] += 1
    
    return cooccurrences

# リモートワーク関連の共起関係を分析
core_terms = ['リモートワーク', 'テレワーク', '在宅勤務', 'コミュニケーション', '生産性']
cooccurrences = find_cooccurring_terms(df_jp['cleaned_content'].dropna(), core_terms)

print("\n共起関係分析:")
for term, related in cooccurrences.items():
    if related:
        print(f"\n{term} との共起単語:")
        for related_term, count in related.most_common(5):
            print(f"- {related_term}: {count}回")

print("\n日本語テキスト分析完了！")
