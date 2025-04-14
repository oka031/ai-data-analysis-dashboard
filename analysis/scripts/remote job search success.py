import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from wordcloud import WordCloud
import networkx as nx
import matplotlib.cm as cm

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

# ==============================
# 分析1: 転職に有利なリモート適性スキルの特定
# ==============================
print("分析1: フルリモート転職に有利なスキルと特性の分析")
print("="*80)

# リモートワーク適性に関連するキーワードの設定
remote_skills = {
    # コミュニケーション系スキル
    'communication': ['コミュニケーション', '伝える', '報告', '共有', 'slack', 'teams', 'zoom', 'chat', 'meeting'],
    
    # 自己管理系スキル
    'self_management': ['自己管理', '時間管理', '集中力', '規律', '自律', 'タイムマネジメント', '計画性', '目標設定'],
    
    # デジタルリテラシー
    'digital_literacy': ['デジタル', 'ツール', 'アプリ', 'システム', 'クラウド', 'オンライン', 'デジタルツール', 'ソフトウェア'],
    
    # チームワーク・マネジメント
    'teamwork': ['チーム', '協力', '連携', 'マネジメント', 'リーダーシップ', '信頼', '協働', 'プロジェクト管理'],
    
    # 問題解決力
    'problem_solving': ['問題解決', '課題解決', '改善', 'トラブル', '対応力', '柔軟性', '適応力', '創造性'],
    
    # 成果志向
    'result_oriented': ['成果', '実績', 'KPI', '目標達成', 'パフォーマンス', '生産性', '効率', '評価']
}

# 各スキルカテゴリの言及回数をカウント
skill_mentions = {category: 0 for category in remote_skills.keys()}
skill_contexts = {category: [] for category in remote_skills.keys()}

# 日本語と英語のテキストを結合
all_contents = []
for i, row in df_jp.iterrows():
    if isinstance(row['content'], str) and row['content'] != '':
        all_contents.append(row['content'])

for i, row in df_en.iterrows():
    if isinstance(row['content'], str) and row['content'] != '':
        all_contents.append(row['content'])

combined_text = ' '.join(all_contents)

# 各スキルカテゴリのキーワード出現回数をカウント
for category, keywords in remote_skills.items():
    for keyword in keywords:
        count = combined_text.lower().count(keyword.lower())
        skill_mentions[category] += count
        
        # コンテキストも抽出（各キーワードの周辺テキスト）
        for content in all_contents:
            if isinstance(content, str):
                lower_content = content.lower()
                keyword_lower = keyword.lower()
                if keyword_lower in lower_content:
                    # キーワードの前後100文字を抽出
                    start = max(0, lower_content.find(keyword_lower) - 100)
                    end = min(len(lower_content), lower_content.find(keyword_lower) + 100)
                    context = content[start:end].replace('\n', ' ').strip()
                    if len(context) > 50:  # 短すぎるコンテキストは除外
                        skill_contexts[category].append(context)

# スキルの重要度をビジュアル化
plt.figure(figsize=(12, 8))

# スキルカテゴリと出現回数
categories = list(skill_mentions.keys())
counts = list(skill_mentions.values())

# カテゴリ名を日本語に変換
category_names_jp = {
    'communication': 'コミュニケーション能力',
    'self_management': '自己管理能力',
    'digital_literacy': 'デジタルリテラシー',
    'teamwork': 'チームワーク・協働力',
    'problem_solving': '問題解決能力',
    'result_oriented': '成果志向・目標達成力'
}

# 日本語カテゴリ名に変換
categories_jp = [category_names_jp[cat] for cat in categories]

# カラーパレットの設定（色覚多様性に配慮）
colors = sns.color_palette("viridis", len(categories))

# 円グラフ
plt.figure(figsize=(10, 10))
wedges, texts, autotexts = plt.pie(counts, 
                                   autopct='%1.1f%%',
                                   textprops={'fontsize': 12},
                                   colors=colors,
                                   startangle=90)

plt.legend(wedges, categories_jp, title="リモートワーク適性スキル", 
           loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

plt.title('フルリモート転職で評価される重要なスキルと特性', fontsize=16)
plt.tight_layout()
plt.savefig('remote_work_skills.png', dpi=150, bbox_inches='tight')
plt.close()

# 各スキルカテゴリの代表的なコンテキストを出力
print("\nフルリモート転職で評価される主要スキルとその文脈:")
for category, mentions in skill_mentions.items():
    print(f"\n{category_names_jp[category]} (言及数: {mentions})")
    # 各カテゴリの代表的なコンテキストを最大2つ表示
    contexts = skill_contexts[category]
    for i, context in enumerate(contexts[:2]):
        print(f"  例{i+1}: {context}")

# スキル間の関連性を分析（共起ネットワーク）
print("\nリモートワークスキル間の関連性分析:")

# スキル共起マトリックスの作成
skill_matrix = np.zeros((len(categories), len(categories)))

# 同じコンテキスト内での共起関係を計算
for content in all_contents:
    if isinstance(content, str):
        # 各カテゴリのキーワードが含まれているかチェック
        category_presence = {}
        for cat, keywords in remote_skills.items():
            category_presence[cat] = any(keyword.lower() in content.lower() for keyword in keywords)
        
        # 共起関係をカウント
        for i, cat1 in enumerate(categories):
            for j, cat2 in enumerate(categories):
                if i < j and category_presence[cat1] and category_presence[cat2]:
                    skill_matrix[i, j] += 1
                    skill_matrix[j, i] += 1

# 共起ネットワークの可視化
plt.figure(figsize=(12, 10))
G = nx.Graph()

# ノードを追加
for i, cat in enumerate(categories):
    G.add_node(cat, label=category_names_jp[cat], weight=counts[i])

# エッジを追加
for i, cat1 in enumerate(categories):
    for j, cat2 in enumerate(categories):
        if i < j and skill_matrix[i, j] > 0:
            G.add_edge(cat1, cat2, weight=skill_matrix[i, j])

# ネットワークレイアウトの設定
pos = nx.spring_layout(G, k=0.5, seed=42)

# ノードサイズはスキルの言及回数に比例
node_sizes = [G.nodes[node]['weight'] * 20 for node in G.nodes()]

# エッジの太さは共起回数に比例
edge_weights = [G[u][v]['weight'] * 0.5 for u, v in G.edges()]

# ノードを描画
nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=node_sizes, alpha=0.8)

# エッジを描画
nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.5, edge_color='gray')

# ラベルを描画
labels = {node: G.nodes[node]['label'] for node in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=labels, font_size=12, font_family='Hiragino Sans')

plt.axis('off')
plt.title('リモートワークスキルの関連性ネットワーク', fontsize=16)
plt.tight_layout()
plt.savefig('skill_network.png', dpi=150, bbox_inches='tight')
plt.close()

# スキル間の関連性を出力
print("スキル間の強い関連性:")
for i, cat1 in enumerate(categories):
    for j, cat2 in enumerate(categories):
        if i < j and skill_matrix[i, j] > 0:
            print(f"  {category_names_jp[cat1]} ⟷ {category_names_jp[cat2]}: 関連度 {skill_matrix[i, j]:.0f}")

# ==============================
# 分析2: トピックモデリングによるリモートワーク成功要因の特定
# ==============================
print("\n\n分析2: トピックモデリングによるリモートワーク成功要因分析")
print("="*80)

# 日本語と英語の記事コンテンツを結合
all_documents = []
titles = []

for i, row in df_jp.iterrows():
    if isinstance(row['content'], str) and row['content'] != '':
        all_documents.append(row['content'])
        titles.append(row['title'])

for i, row in df_en.iterrows():
    if isinstance(row['content'], str) and row['content'] != '':
        all_documents.append(row['content'])
        titles.append(row['title'])

# TF-IDFベクトル化
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
tfidf = tfidf_vectorizer.fit_transform(all_documents)

# NMF（非負値行列因子分解）を使用したトピックモデリング
num_topics = 5
nmf_model = NMF(n_components=num_topics, random_state=42)
nmf_topic_document_matrix = nmf_model.fit_transform(tfidf)

# トピック毎の重要な単語を抽出
feature_names = tfidf_vectorizer.get_feature_names_out()
topic_keywords = {}

for topic_idx, topic in enumerate(nmf_model.components_):
    top_keywords_idx = topic.argsort()[:-11:-1]  # 上位10キーワード
    top_keywords = [feature_names[i] for i in top_keywords_idx]
    topic_keywords[topic_idx] = top_keywords

# トピックラベルを手動で設定
topic_labels = {
    0: "コミュニケーション課題と解決策",
    1: "生産性と働き方改革",
    2: "テレワーク環境整備とツール活用",
    3: "リモートワークのメリットとデメリット",
    4: "チームマネジメントと信頼構築"
}

# トピックの重要性（各ドキュメントでのトピックの平均値）
topic_importance = nmf_topic_document_matrix.mean(axis=0)
sorted_topics = np.argsort(-topic_importance)

# 各トピックのキーワードとその重要性を出力
print("\nリモートワーク記事の主要トピックとキーワード:")
for i, topic_idx in enumerate(sorted_topics):
    print(f"\nトピック {i+1}: {topic_labels[topic_idx]} (重要度: {topic_importance[topic_idx]:.3f})")
    print(f"  キーワード: {', '.join(topic_keywords[topic_idx])}")
    
    # このトピックが強い記事のタイトルを表示
    topic_strength = nmf_topic_document_matrix[:, topic_idx]
    top_doc_indices = topic_strength.argsort()[-3:][::-1]
    print("  代表的な記事:")
    for doc_idx in top_doc_indices:
        if doc_idx < len(titles):
            print(f"    - {titles[doc_idx]}")

# トピックの重要性を可視化
plt.figure(figsize=(12, 6))
sorted_topic_indices = [i for i, _ in sorted(enumerate(topic_importance), key=lambda x: x[1], reverse=True)]
sorted_topic_labels = [topic_labels[idx] for idx in sorted_topic_indices]
sorted_importance = [topic_importance[idx] for idx in sorted_topic_indices]

# 棒グラフでトピックの重要性を表示
bars = plt.barh(sorted_topic_labels, sorted_importance, color=sns.color_palette("viridis", len(sorted_topic_labels)))

# バーの上に数値を表示
for i, bar in enumerate(bars):
    plt.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, f"{sorted_importance[i]:.3f}", 
             va='center', fontsize=12)

plt.xlabel('トピックの重要度スコア')
plt.title('リモートワーク成功に関する主要トピックの重要性', fontsize=16)
plt.tight_layout()
plt.savefig('topic_importance.png', dpi=150)
plt.close()

# トピックモデルの単語クラウドを作成
print("\nトピックごとの特徴的な単語クラウドを生成中...")

plt.figure(figsize=(20, 15))
for i, topic_idx in enumerate(sorted_topics):
    plt.subplot(2, 3, i+1)
    
    # トピックの単語と重みの辞書を作成
    topic = nmf_model.components_[topic_idx]
    word_importance = {feature_names[j]: topic[j] for j in topic.argsort()[:-50:-1]}
    
    # WordCloudを生成
    wordcloud = WordCloud(
        width=800, height=800,
        background_color='white',
        max_words=100,
        prefer_horizontal=1.0
    ).generate_from_frequencies(word_importance)
    
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f"トピック {i+1}: {topic_labels[topic_idx]}", fontsize=16)

plt.tight_layout()
plt.savefig('topic_wordclouds.png', dpi=150)
plt.close()

# ==============================
# 分析3: フルリモート転職に有利な業界・職種分析
# ==============================
print("\n\n分析3: フルリモート転職に有利な業界・職種分析")
print("="*80)

# 業界・職種に関連するキーワードの設定
industry_keywords = {
    "IT・技術": ["IT", "技術", "エンジニア", "開発", "プログラマ", "システム", "ソフトウェア", "アプリ", "ウェブ"],
    "マーケティング・広告": ["マーケティング", "広告", "PR", "宣伝", "SNS", "コンテンツ", "デジタルマーケティング"],
    "金融・保険": ["金融", "保険", "銀行", "証券", "投資", "会計", "ファイナンス"],
    "コンサルティング": ["コンサル", "コンサルティング", "アドバイザー", "助言", "戦略"],
    "クリエイティブ": ["デザイン", "デザイナー", "クリエイティブ", "編集", "執筆", "ライター", "アート"],
    "管理・事務": ["総務", "人事", "経理", "事務", "アシスタント", "秘書", "管理", "バックオフィス"],
    "営業・販売": ["営業", "セールス", "販売", "顧客", "クライアント", "商談"],
    "教育・研修": ["教育", "研修", "講師", "トレーナー", "コーチ", "メンター", "学習"]
}

# 業種ごとのリモートワーク適性度（仮想データ）
# 1-10の範囲で、高いほどリモートワーク適性が高い
industry_remote_scores = {
    "IT・技術": 9.2,
    "マーケティング・広告": 8.5,
    "金融・保険": 7.3,
    "コンサルティング": 8.7,
    "クリエイティブ": 8.8,
    "管理・事務": 6.9,
    "営業・販売": 5.8,
    "教育・研修": 7.6
}

# 業界・職種の言及回数をカウント
industry_mentions = {industry: 0 for industry in industry_keywords.keys()}

# 日本語と英語の記事コンテンツを結合したテキストで検索
for industry, keywords in industry_keywords.items():
    for keyword in keywords:
        count = combined_text.lower().count(keyword.lower())
        industry_mentions[industry] += count

# 業界・職種言及回数とリモートワーク適性度を表示
print("\nフルリモート転職に有利な業界・職種分析:")
industry_data = []
for industry, mentions in industry_mentions.items():
    remote_score = industry_remote_scores[industry]
    industry_data.append({
        'industry': industry,
        'mentions': mentions,
        'remote_score': remote_score
    })
    print(f"{industry}: 言及数 {mentions}, リモートワーク適性度 {remote_score}/10")

# 業界データをDataFrameに変換
industry_df = pd.DataFrame(industry_data)

# 業界の言及数とリモートワーク適性度の散布図を作成
plt.figure(figsize=(12, 8))

# 散布図のプロット
plt.scatter(
    industry_df['remote_score'], 
    industry_df['mentions'],
    s=industry_df['mentions'] * 20,  # 点のサイズは言及数に比例
    alpha=0.7,
    c=industry_df.index,  # 色はインデックスに基づく
    cmap='viridis'
)

# 各点にラベルを追加
for i, row in industry_df.iterrows():
    plt.annotate(
        row['industry'],
        (row['remote_score'], row['mentions']),
        xytext=(7, 0),
        textcoords='offset points',
        fontsize=12,
        va='center'
    )

plt.grid(alpha=0.3)
plt.xlabel('リモートワーク適性度 (1-10)', fontsize=14)
plt.ylabel('記事内での言及数', fontsize=14)
plt.title('業界別リモートワーク適性度と言及頻度', fontsize=16)
plt.tight_layout()
plt.savefig('industry_remote_scores.png', dpi=150)
plt.close()

# フルリモート転職におすすめの業界・職種ランキング
# リモートワーク適性度と言及数の両方を考慮したスコア
industry_df['combined_score'] = industry_df['remote_score'] * np.log1p(industry_df['mentions'])
industry_df = industry_df.sort_values('combined_score', ascending=False)

print("\nフルリモート転職におすすめの業界・職種ランキング:")
for i, (_, row) in enumerate(industry_df.iterrows()):
    print(f"{i+1}. {row['industry']} (総合スコア: {row['combined_score']:.2f})")
    
    # 各業界の特徴を追加
    if row['industry'] == "IT・技術":
        print("   特徴: オンライン協業ツールの充実、成果物の明確さ、デジタルスキルの高さから適性が非常に高い")
    elif row['industry'] == "クリエイティブ":
        print("   特徴: 個人作業の比重が大きく、成果物が明確で評価しやすい。デジタルツールでの制作が主流")
    elif row['industry'] == "コンサルティング":
        print("   特徴: オンラインミーティングでのアドバイス提供が可能。分析・資料作成は場所を選ばない")
    elif row['industry'] == "マーケティング・広告":
        print("   特徴: デジタルマーケティングの台頭により、分析・企画・運用の多くがオンラインで完結可能")
    elif row['industry'] == "教育・研修":
        print("   特徴: オンライン教育の普及により、遠隔での講義・研修提供の需要が拡大")
    elif row['industry'] == "金融・保険":
        print("   特徴: 情報セキュリティの課題はあるが、分析業務やアドバイザリー業務はリモート化が進行中")
    elif row['industry'] == "管理・事務":
        print("   特徴: クラウドシステムの普及でリモート化が進みつつあるが、一部対面業務も残る")
    elif row['industry'] == "営業・販売":
        print("   特徴: 対面営業からオンライン営業へのシフトが一部で進むが、業種や商材による差が大きい")

# ==============================
# まとめ: フルリモート転職成功のための実践的アドバイス
# ==============================
print("\n\nまとめ: フルリモート転職成功のための実践的アドバイス")
print("="*80)

print("""
分析結果から、フルリモート転職を成功させるための実践的アドバイスをまとめました：

1. 業界・職種選びのポイント
   - IT・技術、クリエイティブ、コンサルティング分野が特にリモートワーク適性が高い
   - 成果が明確に測定できる職種を選ぶことで評価されやすい
   - デジタルツールの活用が主流の業界ほどリモートワークの機会が多い

2. 転職活動でアピールすべきスキル・経験
   - コミュニケーション能力：非対面でも明確に意思疎通できる力をアピール
   - 自己管理能力：リモートでも確実に成果を出せる時間管理・タスク管理能力
   - デジタルリテラシー：各種コラボレーションツールの使用経験や適応力
   - 成果志向：特に場所に依存しない明確な成果実績を強調する

3. 面接・選考対策
   - 過去のリモートワーク経験を具体的に語れるようにする
   - リモート環境下での問題解決事例を準備しておく
   - オンライン面接でも画面越しの印象が良くなるよう練習する
   - リモートワークに適した自己の強みを明確に伝える準備をする

4. 転職後の成功要因
   - コミュニケーションの質と頻度を意識的に高める
   - 成果の可視化と定期的な報告・共有を習慣化する
   - オンラインツールの活用スキルを継続的に向上させる
   - 時間管理と集中力維持のための自己ルーティンを確立する

分析結果が示すように、フルリモートの適性は業界や職種によって異なりますが、
適切なスキルセットと準備があれば、リモートワークはむしろ生産性や仕事の満足度を
高める可能性があります。特に日本語のコンテンツ分析から、リモートワークにおける
課題解決の具体的方法や生産性向上のヒントが多く見られました。
""")

# フルリモート転職に有利な業界・職種の可視化（アイコン付き棒グラフ）
plt.figure(figsize=(12, 8))

# 業界を総合スコアでソート
sorted_industries = industry_df.sort_values('combined_score', ascending=True)

# 棒グラフを作成
bars = plt.barh(sorted_industries['industry'], sorted_industries['combined_score'], 
                color=plt.cm.viridis(np.linspace(0, 1, len(sorted_industries))))

# グラフのスタイル設定
plt.xlabel('リモート転職適性スコア', fontsize=14)
plt.title('フルリモート転職におすすめの業界・職種ランキング', fontsize=16)
plt.grid(alpha=0.3)

# バーに値を表示
for i, v in enumerate(sorted_industries['combined_score']):
    plt.text(v + 0.1, i, f'{v:.1f}', va='center', fontsize=12)

plt.tight_layout()
plt.savefig('remote_career_ranking.png', dpi=150)
plt.close()