import os

# 現在のディレクトリの確認
current_dir = os.getcwd()
print("現在のディレクトリ:", current_dir)

# dataフォルダ内のファイル一覧
data_folder = os.path.join(current_dir, "data")
if os.path.exists(data_folder):
    print("\ndataフォルダ内のファイル:")
    for file in os.listdir(data_folder):
        print(f"- {file}")