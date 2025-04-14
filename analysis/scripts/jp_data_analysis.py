import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np
from collections import Counter
import MeCab  # 日本語形態素解析ツール

# データ読み込み
data_folder = os.path.join("..", "data")
file_path = os.path.join(data_folder, "remote_work_data_jp_20250329_165210.csv")
df_jp = pd.read_csv(file_path)

# フォント設定
plt.rcParams['font.family'] = 'Hiragino Sans'

# MeCabの初期化
mecab = MeCab.Tagger("-Ochasen")

# 日本語の感情極性辞書（簡易版）- 拡張可能
# 1：ポジティブ、-1：ネガティブ、0：中立
jp_sentiment_dict = {
    # ポジティブな単語
    "良い": 1, "素晴らしい": 1, "便利": 1, "快適": 1, "効率": 1, "向上": 1, "改善": 1, 
    "柔軟": 1, "充実": 1, "満足": 1, "活用": 1, "成功": 1, "メリット": 1, "効果": 1,
    "簡単": 1, "楽": 1, "自由": 1, "集中": 1, "効率的": 1, "有効": 1, "利点": 1,
    
    # ネガティブな単語
    "難しい": -1, "問題": -1, "課題": -1, "不安": -1, "孤独": -1, "ストレス": -1, "困難": -1,
    "低下": -1, "悪化": -1, "疲れ": -1, "疲労": -1, "デメリット": -1, "障害": -1, "負担": -1,
    "限界": -1, "失敗": -1, "トラブル": -1, "リスク": -1, "欠点": -1, "悪い": -1, "危険": -1
}

# 感情分析関数（日本語向け）
def analyze_jp_sentiment(text):
    if not isinstance(text, str) or text == '':
        return {'polarity': 0, 'subjectivity': 0}
    
    # 形態素解析
    mecab.parse('')  # バッファをクリア
    node = mecab.parseToNode(text)
    
    words = []
    while node:
        # 名詞、動詞、形容詞、副詞を抽出
        if node.feature.split(',')[0] in ['名詞', '動詞', '形容詞', '副詞']:
            words.append(node.surface)
        node = node.next
    
    # 感情スコア計算
    sentiment_score = 0
    sentiment_words = 0
    
    for word in words:
        if word in jp_sentiment_dict:
            sentiment_score += jp_sentiment_dict[word]
            sentiment_words += 1
    
    # 極性（-1 to 1）
    polarity = sentiment_score / max(sentiment_words, 1)
    
    # 主観性（感情語の割合）
    subjectivity = min(1.0, sentiment_words / max(len(words), 1))
    
    return {'polarity': polarity, 'subjectivity': subjectivity}

# ソリューション指向度を評価する関数（日本語向け）
def jp_solution_orientation(text):
    if not isinstance(text, str) or text == '':
        return 0
    
    # ソリューション関連キーワード
    solution_words = ['解決', '方法', '対策', '改善', '向上', '効率化', 'ツール', '手法', 
                     'テクニック', 'コツ', 'ベストプラクティス', '推奨', 'アドバイス', 
                     'ガイド', '提案', '実践', '活用法', '実現', '強化']
    
    # 問題関連キーワード
    problem_words = ['問題', '課題', '困難', '障害', '障壁', '弊害', '苦労', '懸念', 
                    'リスク', '制限', '限界', '欠点', 'デメリット', '悩み']
    
    # キーワード出現回数をカウント
    solution_count = sum(text.count(word) for word in solution_words)
    problem_count = sum(text.count(word) for word in problem_words)
    
    # ソリューション指向度スコア（-1〜1の範囲）
    if problem_count + solution_count == 0:
        return 0
    
    solution_ratio = solution_count / (problem_count + solution_count)
    return (solution_ratio - 0.5) * 2  # -1〜1のスケールに変換

# コンテンツの構造を分析する関数（日本語向け）
def analyze_jp_structure(text):
    if not isinstance(text, str) or text == '':
        return {'headings': 0, 'paragraphs': 0, 'lists': 0, 'avg_paragraph_length': 0}
    
    # 見出しっぽい行を検出
    lines = text.split('\n')
    headings = 0
    for line in lines:
        line = line.strip()
        if len(line) > 0 and len(line) < 50:  # 短い行（日本語は英語より文字数少なめ）
            if (line.endswith('とは') or line.endswith('について') or 
                re.match(r'^[\d１２３４５６７８９０]+[\.．、]', line) or 
                re.match(r'^【.+】$', line) or re.match(r'^■.+', line) or 
                re.match(r'^●.+', line) or re.match(r'^◆.+', line)):
                headings += 1
    
    # 段落数（空行で区切られた部分）
    paragraphs = len([p for p in re.split(r'\n\s*\n', text) if p.strip()])
    
    # リスト項目（箇条書き）
    list_items = len(re.findall(r'^\s*[・※◎○●■□▲△▼▽◆◇★☆→①-⑩]+\s+', text, re.MULTILINE))
    
    # 段落の平均長（文字数）
    if paragraphs > 0:
        paragraph_texts = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        avg_paragraph_length = sum(len(p) for p in paragraph_texts) / paragraphs
    else:
        avg_paragraph_length = 0
    
    return {
        'headings': headings,
        'paragraphs': paragraphs,
        'lists': list_items,
        'avg_paragraph_length': avg_paragraph_length
    }

# 読みやすさを分析する関数（日本語向け）
def analyze_jp_readability(text):
    if not isinstance(text, str) or text == '':
        return {'avg_sentence_length': 0, 'character_per_sentence': 0}
    
    # 文の分割
    sentences = re.split(r'[。．!！?？]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {'avg_sentence_length': 0, 'character_per_sentence': 0}
    
    # 単語数カウント（簡易的に形態素解析）
    word_counts = []
    for sentence in sentences:
        mecab.parse('')  # バッファをクリア
        node = mecab.parseToNode(sentence)
        count = 0
        while node:
            if node.feature.split(',')[0] not in ['BOS/EOS']:  # 文頭/文末記号以外
                count += 1
            node = node.next
        word_counts.append(count)
    
    # 平均語数/文
    avg_sentence_length = sum(word_counts) / len(sentences)
    
    # 平均文字数/文
    avg_char_per_sentence = sum(len(s) for s in sentences) / len(sentences)
    
    return {
        'avg_sentence_length': avg_sentence_length,
        'character_per_sentence': avg_char_per_sentence
    }

# 記事ごとの分析実行
sentiments = []
solution_scores = []
structure_data = []
readability_data = []
titles = []

for i, row in df_jp.iterrows():
    if isinstance(row['content'], str) and row['content'] != '':
        sentiment = analyze_jp_sentiment(row['content'])
        solution_score = jp_solution_orientation(row['content'])
        structure = analyze_jp_structure(row['content'])
        readability_metrics = analyze_jp_readability(row['content'])
        
        sentiments.append(sentiment)
        solution_scores.append(solution_score)
        structure_data.append(structure)
        readability_data.append(readability_metrics)
        titles.append(row['title'] if isinstance(row['title'], str) else '')

# 分析結果をデータフレームに
sentiment_df = pd.DataFrame({
    'title': titles,
    'polarity': [s['polarity'] for s in sentiments],
    'subjectivity': [s['subjectivity'] for s in sentiments],
    'solution_score': solution_scores
})

structure_df = pd.DataFrame({
    'title': titles,
    'headings': [s['headings'] for s in structure_data],
    'paragraphs': [s['paragraphs'] for s in structure_data],
    'lists': [s['lists'] for s in structure_data],
    'avg_paragraph_length': [s['avg_paragraph_length'] for s in structure_data]
})

readability_df = pd.DataFrame({
    'title': titles,
    'avg_sentence_length': [r['avg_sentence_length'] for r in readability_data],
    'character_per_sentence': [r['character_per_sentence'] for r in readability_data]
})

# 分析結果の表示
print("日本語記事の感情分析とソリューション指向度:")
print(sentiment_df)

print("\n日本語記事の構造分析:")
print(structure_df)

print("\n日本語記事の読みやすさ分析:")
print(readability_df)

# 英語分析と同様のグラフ作成
# 1. 構造比較グラフ
plt.figure(figsize=(12, 6))
x = np.arange(len(titles))
width = 0.2

plt.bar(x - width, structure_df['headings'], width, label='見出し数')
plt.bar(x, structure_df['paragraphs'], width, label='段落数')
plt.bar(x + width, structure_df['lists'], width, label='リスト項目数')

plt.xticks(x, [t[:10] + '...' if len(t) > 10 else t for t in titles], rotation=45)
plt.title('日本語記事の構造要素比較')
plt.xlabel('記事')
plt.ylabel('要素数')
plt.legend()
plt.tight_layout()
plt.savefig('jp_content_structure.png', dpi=150)
plt.close()

# 2. ソリューション指向度と感情極性の散布図
plt.figure(figsize=(10, 6))
plt.scatter(sentiment_df['solution_score'], sentiment_df['polarity'], 
            alpha=0.7, s=100, c=sentiment_df['subjectivity'], cmap='viridis')

plt.colorbar(label='主観性スコア')
plt.title('日本語リモートワーク記事のソリューション指向度と感情極性')
plt.xlabel('ソリューション指向度 (-1=問題中心, 1=解決策中心)')
plt.ylabel('感情極性 (-1=ネガティブ, 1=ポジティブ)')
plt.grid(alpha=0.3)
plt.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle='-', alpha=0.5)

# プロット上に記事タイトルを表示（短縮版）
for i, txt in enumerate(sentiment_df['title']):
    short_title = txt[:8] + '...' if len(txt) > 8 else txt
    plt.annotate(short_title, 
                (sentiment_df['solution_score'].iloc[i], sentiment_df['polarity'].iloc[i]),
                fontsize=8, alpha=0.7)

plt.tight_layout()
plt.savefig('jp_sentiment_solution_analysis.png', dpi=150)
plt.close()

# 3. 日英比較グラフ（もしdf_enのデータがある場合）
try:
    # 英語データの読み込み試行
    en_file_path = os.path.join(data_folder, "remote_work_data_en_20250329_165210.csv")
    df_en = pd.read_csv(en_file_path)
    
    # 英語データの分析結果があると仮定
    en_sentiment_df = pd.read_csv("en_sentiment_analysis.csv") if os.path.exists("en_sentiment_analysis.csv") else None
    
    if en_sentiment_df is not None:
        # 日英比較グラフ（感情極性とソリューション指向度）
        plt.figure(figsize=(10, 6))
        
        # 英語データ
        plt.scatter(en_sentiment_df['solution_score'], en_sentiment_df['polarity'], 
                   alpha=0.7, s=80, marker='o', color='blue', label='英語記事')
        
        # 日本語データ
        plt.scatter(sentiment_df['solution_score'], sentiment_df['polarity'], 
                   alpha=0.7, s=80, marker='^', color='red', label='日本語記事')
        
        plt.title('日英リモートワーク記事の比較')
        plt.xlabel('ソリューション指向度 (-1=問題中心, 1=解決策中心)')
        plt.ylabel('感情極性 (-1=ネガティブ, 1=ポジティブ)')
        plt.grid(alpha=0.3)
        plt.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        plt.axvline(x=0, color='gray', linestyle='-', alpha=0.5)
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('jp_en_comparison.png', dpi=150)
        plt.close()
except Exception as e:
    print(f"英語データとの比較グラフ作成をスキップ: {e}")

# 全体の統計
print("\n全体の統計:")
print(f"平均感情極性: {sentiment_df['polarity'].mean():.3f} (-1=ネガティブ, 1=ポジティブ)")
print(f"平均主観性: {sentiment_df['subjectivity'].mean():.3f} (0=客観的, 1=主観的)")
print(f"平均ソリューション指向度: {sentiment_df['solution_score'].mean():.3f} (-1=問題中心, 1=解決策中心)")
print(f"平均見出し数: {structure_df['headings'].mean():.1f}")
print(f"平均段落数: {structure_df['paragraphs'].mean():.1f}")
print(f"平均リスト項目数: {structure_df['lists'].mean():.1f}")
print(f"平均段落長: {structure_df['avg_paragraph_length'].mean():.1f}文字")
print(f"平均文長（語数）: {readability_df['avg_sentence_length'].mean():.1f}語")
print(f"平均文長（文字数）: {readability_df['character_per_sentence'].mean():.1f}文字")

# 分析結果の保存
sentiment_df.to_csv("jp_sentiment_analysis.csv", index=False)
structure_df.to_csv("jp_structure_analysis.csv", index=False)
readability_df.to_csv("jp_readability_analysis.csv", index=False)