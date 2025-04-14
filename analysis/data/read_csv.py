import os
import pandas as pd

# データフォルダのパス
data_folder = os.path.join(os.getcwd(), "data")

# CSVファイルの読み込み
file_path = os.path.join(data_folder, "remote_work_all_data_20250329_165210.csv")
df_all = pd.read_csv(file_path)

# 基本情報の確認
print("データの形状（行数, 列数）:", df_all.shape)
print("\n最初の5行:")
print(df_all.head())

# 全列名の確認
print("\n列名一覧:")
print(df_all.columns.tolist())

# データの基本情報
print("\nデータの基本情報:")
print(df_all.info())

# 欠損値の確認
print("\n欠損値の数:")
print(df_all.isnull().sum())

# 言語の分布を確認
print("\n言語の分布:")
print(df_all['language'].value_counts())

# コンテンツの長さを確認
df_all['content_length'] = df_all['content'].str.len()
print("\nコンテンツ長さの統計:")
print(df_all['content_length'].describe())

# タイトルから主要なキーワードを抽出
print("\nタイトルの一部:")
for i, title in enumerate(df_all['title'].dropna().head()):
    print(f"{i+1}. {title}")