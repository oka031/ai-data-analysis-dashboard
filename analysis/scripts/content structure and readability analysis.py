import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np
from collections import Counter

# データ読み込み
data_folder = os.path.join("..", "data")
file_path = os.path.join(data_folder, "remote_work_data_en_20250329_165210.csv")
df_en = pd.read_csv(file_path)

# フォント設定
plt.rcParams['font.family'] = 'Hiragino Sans'

# コンテンツの構造を分析する関数
def analyze_structure(text):
    if not isinstance(text, str) or text == '':
        return {'headings': 0, 'paragraphs': 0, 'lists': 0, 'avg_paragraph_length': 0}
    
    # 見出しっぽい行を検出（大文字が多い短い行、または数字で始まる行）
    lines = text.split('\n')
    headings = 0
    for line in lines:
        line = line.strip()
        if len(line) > 0 and len(line) < 100:  # 短い行
            uppercase_ratio = sum(1 for c in line if c.isupper()) / len(line)
            if uppercase_ratio > 0.5 or re.match(r'^\d+[\.\)]\s', line):
                headings += 1
    
    # 段落数（空行で区切られた部分）
    paragraphs = len([p for p in re.split(r'\n\s*\n', text) if p.strip()])
    
    # リスト項目（箇条書き）
    list_items = len(re.findall(r'^\s*[\-\*\•]\s+', text, re.MULTILINE))
    
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

# 読みやすさを分析する関数
def analyze_readability(text):
    if not isinstance(text, str) or text == '':
        return {'flesch_reading_ease': 0, 'flesch_kincaid_grade': 0, 'avg_sentence_length': 0}
    
    # 文の分割
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 文の平均長（単語数）
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    
    # Flesch Reading Ease (FRE) スコア
    # 高いほど読みやすい (0-100)
    word_count = len(text.split())
    sentence_count = len(sentences)
    
    # 単語あたりの平均音節数の近似値（英語向け）
    syllable_count = sum(count_syllables(word) for word in text.split())
    
    if sentence_count > 0 and word_count > 0:
        fre = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
        fkg = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
    else:
        fre = 0
        fkg = 0
    
    return {
        'flesch_reading_ease': fre,
        'flesch_kincaid_grade': fkg,
        'avg_sentence_length': avg_sentence_length
    }

# 英単語の音節数を推定する関数（簡易版）
def count_syllables(word):
    word = word.lower()
    if len(word) <= 3:
        return 1
    
    # 母音をカウント
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    
    # 特定のパターンで調整
    if word.endswith('e'):
        count -= 1
    if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
        count += 1
    if count == 0:
        count = 1
        
    return count

# 記事ごとの構造と読みやすさの分析
structure_data = []
readability_data = []
titles = []

for i, row in df_en.iterrows():
    if isinstance(row['content'], str) and row['content'] != '':
        structure = analyze_structure(row['content'])
        readability_metrics = analyze_readability(row['content'])
        
        structure_data.append(structure)
        readability_data.append(readability_metrics)
        titles.append(row['title'] if isinstance(row['title'], str) else '')

# 結果をデータフレームに
structure_df = pd.DataFrame({
    'title': titles,
    'headings': [s['headings'] for s in structure_data],
    'paragraphs': [s['paragraphs'] for s in structure_data],
    'lists': [s['lists'] for s in structure_data],
    'avg_paragraph_length': [s['avg_paragraph_length'] for s in structure_data]
})

readability_df = pd.DataFrame({
    'title': titles,
    'flesch_reading_ease': [r['flesch_reading_ease'] for r in readability_data],
    'flesch_kincaid_grade': [r['flesch_kincaid_grade'] for r in readability_data],
    'avg_sentence_length': [r['avg_sentence_length'] for r in readability_data]
})

# 分析結果の表示
print("記事の構造分析:")
print(structure_df)

print("\n記事の読みやすさ分析:")
print(readability_df)

# 構造の可視化 - 記事ごとの構造要素の比較
plt.figure(figsize=(12, 6))
x = np.arange(len(titles))
width = 0.2

plt.bar(x - width, structure_df['headings'], width, label='見出し数')
plt.bar(x, structure_df['paragraphs'], width, label='段落数')
plt.bar(x + width, structure_df['lists'], width, label='リスト項目数')

plt.xticks(x, [t[:15] + '...' if len(t) > 15 else t for t in titles], rotation=45)
plt.title('記事の構造要素比較')
plt.xlabel('記事')
plt.ylabel('要素数')
plt.legend()
plt.tight_layout()
plt.savefig('content_structure.png', dpi=150)
plt.close()

# 読みやすさと構造の関係の可視化
plt.figure(figsize=(10, 6))
plt.scatter(readability_df['flesch_reading_ease'], structure_df['avg_paragraph_length'], 
            s=structure_df['paragraphs']*10, alpha=0.7, 
            c=readability_df['avg_sentence_length'], cmap='viridis')

plt.colorbar(label='平均文長（単語数）')
plt.title('記事の読みやすさと構造の関係')
plt.xlabel('読みやすさスコア（高いほど読みやすい）')
plt.ylabel('平均段落長（文字数）')
plt.grid(alpha=0.3)

# バブルサイズの凡例
sizes = [10, 20, 30]
labels = ['10段落', '20段落', '30段落']
for size, label in zip(sizes, labels):
    plt.scatter([], [], s=size*10, alpha=0.7, color='gray', label=label)
plt.legend(title='段落数')

plt.tight_layout()
plt.savefig('readability_structure_relationship.png', dpi=150)
plt.close()

# 全体の統計
print("\n全体の構造統計:")
print(f"平均見出し数: {structure_df['headings'].mean():.1f}")
print(f"平均段落数: {structure_df['paragraphs'].mean():.1f}")
print(f"平均リスト項目数: {structure_df['lists'].mean():.1f}")
print(f"平均段落長: {structure_df['avg_paragraph_length'].mean():.1f}文字")

print("\n全体の読みやすさ統計:")
print(f"平均Flesch Reading Ease: {readability_df['flesch_reading_ease'].mean():.1f} (高いほど読みやすい)")
print(f"平均Flesch-Kincaid Grade Level: {readability_df['flesch_kincaid_grade'].mean():.1f} (米国の学年レベル)")
print(f"平均文長: {readability_df['avg_sentence_length'].mean():.1f}単語")