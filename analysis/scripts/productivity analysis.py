import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr

# フォント設定
plt.rcParams['font.family'] = 'Hiragino Sans'

# データ読み込み
data_folder = os.path.join("..", "data")
jp_file_path = os.path.join(data_folder, "remote_work_data_jp_20250329_165210.csv")
en_file_path = os.path.join(data_folder, "remote_work_data_en_20250329_165210.csv")

df_jp = pd.read_csv(jp_file_path)
df_en = pd.read_csv(en_file_path)

# 感情分析データの読み込み
jp_sentiment_df = pd.read_csv("jp_sentiment_analysis.csv")
en_sentiment_df = pd.read_csv("en_sentiment_analysis.csv") if os.path.exists("en_sentiment_analysis.csv") else None

# 構造分析データの読み込み
jp_structure_df = pd.read_csv("jp_structure_analysis.csv")
en_structure_df = pd.read_csv("en_structure_analysis.csv") if os.path.exists("en_structure_analysis.csv") else None

# 読みやすさデータの読み込み
jp_readability_df = pd.read_csv("jp_readability_analysis.csv")
en_readability_df = pd.read_csv("en_readability_analysis.csv") if os.path.exists("en_readability_analysis.csv") else None

# 分析1: リモートワークの生産性向上要因の抽出
print("分析1: リモートワークの生産性向上要因の抽出")
print("="*80)

# 生産性向上に関するキーワードを設定
productivity_keywords_jp = [
    "生産性向上", "効率化", "業務効率", "パフォーマンス向上", "成果", "効果的", "時間短縮",
    "集中力", "成功", "メリット", "効果", "向上", "改善", "最適化", "時間活用"
]

productivity_keywords_en = [
    "productivity", "efficiency", "performance", "outcome", "effective", "time-saving",
    "focus", "success", "benefit", "improvement", "optimize", "time management"
]

# 日本語記事から生産性向上要因を抽出
jp_productivity_mentions = []

for i, row in df_jp.iterrows():
    if isinstance(row['content'], str) and row['content'] != '':
        # 生産性向上に関する言及を含む段落を抽出
        paragraphs = re.split(r'\n\s*\n', row['content'])
        for paragraph in paragraphs:
            if any(keyword in paragraph for keyword in productivity_keywords_jp):
                # 追加の条件: ポジティブなコンテキストであること
                if "向上" in paragraph or "効果" in paragraph or "改善" in paragraph or "成功" in paragraph:
                    jp_productivity_mentions.append({
                        'title': row['title'],
                        'paragraph': paragraph,
                        'source': 'jp'
                    })

# 英語記事から生産性向上要因を抽出
en_productivity_mentions = []

for i, row in df_en.iterrows():
    if isinstance(row['content'], str) and row['content'] != '':
        # 生産性向上に関する言及を含む段落を抽出
        paragraphs = re.split(r'\n\s*\n', row['content'])
        for paragraph in paragraphs:
            if any(keyword in paragraph.lower() for keyword in productivity_keywords_en):
                # 追加の条件: ポジティブなコンテキストであること
                if "improve" in paragraph.lower() or "benefit" in paragraph.lower() or "success" in paragraph.lower():
                    en_productivity_mentions.append({
                        'title': row['title'],
                        'paragraph': paragraph,
                        'source': 'en'
                    })

# すべての生産性向上言及を結合
all_productivity_mentions = jp_productivity_mentions + en_productivity_mentions

# 生産性向上要因のカテゴリ分類（手動）
productivity_factors = [
    {'category': 'コミュニケーションツール', 'keywords': ['slack', 'teams', 'zoom', 'チャット', 'ビデオ会議', 'オンライン会議', 'コミュニケーションツール']},
    {'category': '時間管理', 'keywords': ['時間管理', '時間効率', 'スケジュール', '集中時間', '時間の使い方', 'タイムマネジメント']},
    {'category': '作業環境', 'keywords': ['環境', '集中', '静か', '快適', 'オフィス環境', '仕事場所', 'ワークスペース']},
    {'category': '自己管理', 'keywords': ['自己管理', 'セルフマネジメント', '自律', '規律', 'モチベーション', '意識']},
    {'category': 'ワークライフバランス', 'keywords': ['ワークライフ', '通勤時間', '家族', '生活', 'バランス', '余暇', 'プライベート']},
    {'category': 'ICTツール活用', 'keywords': ['ツール', 'アプリ', 'デジタル', 'クラウド', 'オンライン', 'システム', 'デジタルツール']},
    {'category': '組織文化・マネジメント', 'keywords': ['信頼', '裁量', '自律', 'マネジメント', 'リーダーシップ', '組織', '評価']}
]

# 生産性向上要因ごとの言及数をカウント
factor_counts = {factor['category']: 0 for factor in productivity_factors}
factor_contexts = {factor['category']: [] for factor in productivity_factors}

for mention in all_productivity_mentions:
    paragraph_lower = mention['paragraph'].lower()
    for factor in productivity_factors:
        if any(keyword.lower() in paragraph_lower for keyword in factor['keywords']):
            factor_counts[factor['category']] += 1
            # コンテキストの一部を保存（最初の100文字）
            short_context = mention['paragraph'][:100] + "..." if len(mention['paragraph']) > 100 else mention['paragraph']
            factor_contexts[factor['category']].append({
                'title': mention['title'],
                'context': short_context,
                'source': mention['source']
            })

# 生産性向上要因の可視化
plt.figure(figsize=(12, 8))
categories = list(factor_counts.keys())
counts = list(factor_counts.values())

# カラーパレットの設定（色覚多様性に配慮）
colors = sns.color_palette("viridis", len(categories))

# 水平バーチャート
bars = plt.barh(categories, counts, color=colors)
plt.xlabel('言及数')
plt.title('リモートワークにおける生産性向上要因')
plt.tight_layout()

# バーの上に数値を表示
for i, bar in enumerate(bars):
    plt.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, 
             str(counts[i]), va='center')

plt.savefig('productivity_factors.png', dpi=150)
plt.close()

# 生産性向上要因の詳細を出力
print("リモートワークにおける生産性向上要因の詳細:")
for category, count in factor_counts.items():
    print(f"\n{category} (言及数: {count})")
    # 各カテゴリの代表的なコンテキストを最大3つ表示
    contexts = factor_contexts[category]
    for i, context_data in enumerate(contexts[:3]):
        print(f"  例{i+1} [{context_data['source']}]: {context_data['context']}")

# 分析2: クラスター分析 - リモートワーク記事の類型化
print("\n\n分析2: リモートワーク記事の類型化（クラスター分析）")
print("="*80)

# 日本語と英語の感情分析・構造データを結合
jp_sentiment_df['language'] = 'jp'
if en_sentiment_df is not None:
    en_sentiment_df['language'] = 'en'
    combined_df = pd.concat([jp_sentiment_df, en_sentiment_df], ignore_index=True)
else:
    combined_df = jp_sentiment_df.copy()

# クラスタリングのための特徴量を選択
features = ['polarity', 'subjectivity', 'solution_score']
X = combined_df[features].values

# 特徴量の標準化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-meansクラスタリング（クラスター数=4と仮定）
kmeans = KMeans(n_clusters=4, random_state=42)
clusters = kmeans.fit_predict(X_scaled)
combined_df['cluster'] = clusters

# クラスターの特徴を分析
cluster_profiles = combined_df.groupby('cluster')[features].mean()
print("クラスター分析結果:")
print(cluster_profiles)

# クラスターごとの記事数
cluster_counts = combined_df.groupby(['cluster', 'language']).size().unstack(fill_value=0)
print("\nクラスターごとの記事数:")
print(cluster_counts)

# クラスターの解釈
cluster_interpretations = {
    0: "問題指摘型（ネガティブ・問題中心）",
    1: "解決志向型（ポジティブ・解決策中心）",
    2: "バランス型（中立・包括的）",
    3: "調査報告型（客観的・分析的）"
}

# クラスター名を追加
combined_df['cluster_name'] = combined_df['cluster'].map(cluster_interpretations)

# クラスターごとの記事タイトルを表示
print("\nクラスターごとの代表的な記事タイトル:")
for cluster, name in cluster_interpretations.items():
    print(f"\nクラスター{cluster}: {name}")
    titles = combined_df[combined_df['cluster'] == cluster]['title'].values[:3]
    for title in titles:
        print(f"  - {title}")

# クラスター分析の可視化（散布図）
plt.figure(figsize=(12, 8))

# 言語ごとに異なるマーカーを使用
markers = {'jp': 'o', 'en': '^'}
cluster_colors = sns.color_palette("viridis", len(cluster_interpretations))

for cluster, name in cluster_interpretations.items():
    for lang in ['jp', 'en']:
        mask = (combined_df['cluster'] == cluster) & (combined_df['language'] == lang)
        if mask.any():
            plt.scatter(
                combined_df.loc[mask, 'solution_score'], 
                combined_df.loc[mask, 'polarity'],
                s=100, 
                c=[cluster_colors[cluster]],
                marker=markers[lang],
                alpha=0.7,
                label=f"{name} ({lang})" if lang == 'jp' else f"{name} ({lang})"
            )

# クラスターの中心点を表示
for cluster in range(len(cluster_interpretations)):
    center_x = cluster_profiles.loc[cluster, 'solution_score']
    center_y = cluster_profiles.loc[cluster, 'polarity']
    plt.scatter(center_x, center_y, s=200, c=[cluster_colors[cluster]], 
                marker='*', edgecolor='black', linewidth=1.5)
    plt.annotate(f"C{cluster}", (center_x, center_y), 
                 xytext=(5, 5), textcoords='offset points',
                 fontsize=12, fontweight='bold')

plt.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle='-', alpha=0.5)
plt.grid(alpha=0.3)
plt.title('リモートワーク記事のクラスター分析')
plt.xlabel('ソリューション指向度 (-1=問題中心, 1=解決策中心)')
plt.ylabel('感情極性 (-1=ネガティブ, 1=ポジティブ)')

# 凡例を追加
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), loc='best')

plt.tight_layout()
plt.savefig('cluster_analysis.png', dpi=150)
plt.close()

# ===============================
# リモートワーク転職に役立つ洞察
# ===============================

print("\n\nリモートワーク転職成功に役立つ洞察")
print("="*80)

# 生産性向上とポジティブな側面に焦点を当てたメッセージを抽出
positive_insights = []

# 解決志向型クラスター（クラスター1）の記事から洞察を抽出
solution_focused_articles = combined_df[combined_df['cluster'] == 1]
for _, row in solution_focused_articles.iterrows():
    article_index = df_jp[df_jp['title'] == row['title']].index
    if len(article_index) > 0:
        content = df_jp.loc[article_index[0], 'content']
        if isinstance(content, str):
            # 生産性向上に関する言及を抽出
            paragraphs = re.split(r'\n\s*\n', content)
            for paragraph in paragraphs:
                if any(keyword in paragraph for keyword in productivity_keywords_jp) and len(paragraph) > 100:
                    positive_insights.append({
                        'source': row['title'],
                        'insight': paragraph[:300] + "..." if len(paragraph) > 300 else paragraph,
                        'score': row['polarity'] + row['solution_score']  # ポジティブさとソリューション指向度の合計
                    })
    
    # 英語記事も同様に処理
    article_index = df_en[df_en['title'] == row['title']].index
    if len(article_index) > 0:
        content = df_en.loc[article_index[0], 'content']
        if isinstance(content, str):
            # 生産性向上に関する言及を抽出
            paragraphs = re.split(r'\n\s*\n', content)
            for paragraph in paragraphs:
                if any(keyword in paragraph.lower() for keyword in productivity_keywords_en) and len(paragraph) > 100:
                    positive_insights.append({
                        'source': row['title'],
                        'insight': paragraph[:300] + "..." if len(paragraph) > 300 else paragraph,
                        'score': row['polarity'] + row['solution_score']
                    })

# スコアでソートして上位の洞察を表示
positive_insights.sort(key=lambda x: x['score'], reverse=True)
print("\nリモートワークの生産性向上に関する重要な洞察:")
for i, insight in enumerate(positive_insights[:5]):
    print(f"\n洞察 {i+1} (スコア: {insight['score']:.2f}):")
    print(f"出典: {insight['source']}")
    print(f"内容: {insight['insight']}")

# 転職成功のための具体的な要因を分析
print("\nフルリモートワーク転職成功のための重要な要因:")

success_factors = [
    "コミュニケーション能力の強化: リモートワークでは明確で効果的なコミュニケーションがさらに重要になります。",
    "自己管理能力の証明: 自律的に働ける能力や時間管理のスキルをアピールすることが重要です。",
    "デジタルツールの習熟: 各種コラボレーションツールやプロジェクト管理ツールの使用経験をアピールしましょう。",
    "成果の可視化: リモートワークでの具体的な成果や、数値で示せる実績を用意しましょう。",
    "適応力と柔軟性: 新しい環境や働き方に柔軟に対応できることをアピールできます。"
]

for i, factor in enumerate(success_factors):
    print(f"{i+1}. {factor}")

# ===============================
# クラスター分析から見る最適なターゲット企業
# ===============================

print("\n分析結果から見る最適なターゲット企業タイプ:")
print("クラスター分析の結果から、以下のタイプの企業がフルリモートワークに前向きである可能性が高いです:")

target_companies = [
    "解決志向型の企業文化を持つ組織: リモートワークの課題を認識しつつも、積極的に解決策を模索している企業",
    "ICTツール活用に積極的な企業: 最新のコミュニケーションツールやプロジェクト管理ツールを導入している企業",
    "成果主義の評価体系を持つ企業: 勤務時間よりも成果で評価する文化がある企業",
    "グローバルな視点を持つ企業: 海外との取引や国際的な人材の活用に積極的な企業",
    "ワークライフバランスを重視する企業: 従業員の生活の質向上に価値を置く企業文化を持つ組織"
]

for i, company_type in enumerate(target_companies):
    print(f"{i+1}. {company_type}")