import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# 環境変数の読み込み（APIキーなどを保存する場合）
load_dotenv()

# ユーザーエージェントのリスト（ブロックを避けるため）
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
]

def get_search_results(query, num_pages=2, language=None):
    """
    検索エンジンから検索結果を取得する
    
    Parameters:
    query (str): 検索クエリ
    num_pages (int): 取得するページ数
    language (str): 言語設定（例: 'ja'は日本語）
    
    Returns:
    list: 検索結果のURL、タイトル、スニペットのリスト
    """
    all_results = []
    
    # SearchAPIを使う代わりに、別の検索エンジンを試す
    # Google以外の検索エンジンURLを用意
    search_engines = [
        # Bingの検索URL
        "https://www.bing.com/search?q={}&first={}",
        # DuckDuckGoの検索URL
        "https://duckduckgo.com/html/?q={}"
    ]
    
    # ランダムに検索エンジンを選択
    search_url = random.choice(search_engines)
    
    for page in range(num_pages):
        # 検索ページのインデックス（10件ごと）
        start_idx = page * 10
        
        # ランダムなユーザーエージェントを選択
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5' if not language else f'{language},{language}-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # クエリにランダムな文字列を追加して検出を避ける
        modified_query = query
        
        # リクエストを送信
        try:
            response = requests.get(
                search_url.format(modified_query.replace(' ', '+'), start_idx),
                headers=headers,
                timeout=15
            )
            
            # レスポンスのステータスコードをチェック
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 検索エンジンに応じたセレクタを使用
                if "bing" in search_url:
                    search_results = soup.select('li.b_algo')
                    
                    for result in search_results:
                        try:
                            title_element = result.select_one('h2')
                            if not title_element:
                                continue
                                
                            title = title_element.get_text()
                            
                            link_element = result.select_one('h2 a')
                            if not link_element:
                                continue
                                
                            link = link_element.get('href')
                            
                            # スニペット（ディスクリプション）を取得
                            snippet_element = result.select_one('p')
                            snippet = snippet_element.get_text() if snippet_element else ""
                            
                            all_results.append({
                                'title': title,
                                'url': link,
                                'snippet': snippet
                            })
                            
                        except Exception as e:
                            print(f"エラーが発生しました: {e}")
                            continue
                
                elif "duckduckgo" in search_url:
                    search_results = soup.select('.result')
                    
                    for result in search_results:
                        try:
                            title_element = result.select_one('.result__title')
                            if not title_element:
                                continue
                                
                            title = title_element.get_text()
                            
                            link_element = result.select_one('.result__title a')
                            if not link_element:
                                continue
                                
                            link = link_element.get('href')
                            
                            # スニペット（ディスクリプション）を取得
                            snippet_element = result.select_one('.result__snippet')
                            snippet = snippet_element.get_text() if snippet_element else ""
                            
                            all_results.append({
                                'title': title,
                                'url': link,
                                'snippet': snippet
                            })
                            
                        except Exception as e:
                            print(f"エラーが発生しました: {e}")
                            continue
            else:
                print(f"エラー: HTTPステータスコード {response.status_code}")
                # 他の検索エンジンに切り替え
                search_url = [engine for engine in search_engines if engine != search_url][0]
                continue
        
        except requests.exceptions.RequestException as e:
            print(f"リクエスト中にエラーが発生しました: {e}")
            # 他の検索エンジンに切り替え
            search_url = [engine for engine in search_engines if engine != search_url][0]
            continue
            
        # サーバーに負荷をかけないように、リクエスト間に遅延を入れる
        # さらにランダム性を高める
        time.sleep(random.uniform(5, 15))
        
        # IPアドレスを変更するためにプロキシを使用する場合
        # 注: プロキシリストを用意する必要があります
        # proxies = get_next_proxy()  # 実装が必要
        # response = requests.get(..., proxies=proxies)
    
    return all_results

def extract_content_from_url(url):
    """
    指定されたURLからコンテンツを抽出する
    
    Parameters:
    url (str): 記事やブログ記事などのURL
    
    Returns:
    dict: タイトル、本文、メタデータなどを含む辞書
    """
    try:
        # ランダムなユーザーエージェントを選択
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5,ja;q=0.3',  # 日本語も受け入れる
            'Connection': 'keep-alive'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # 文字コードを適切に設定
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # タイトルを取得
            title = soup.title.string if soup.title else ""
            
            # メタディスクリプションを取得
            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', "")
            
            # 記事の本文を取得（これはサイトによって構造が異なるため、調整が必要）
            # 一般的な記事要素のセレクタをいくつか試す
            content = ""
            for selector in ['article', 'main', '.post-content', '.entry-content', '#content', '.article-body', '.blog-content']:
                content_element = soup.select_one(selector)
                if content_element:
                    content = content_element.get_text(separator='\n', strip=True)
                    break
            
            # コンテンツが見つからない場合は、すべての段落テキストを収集
            if not content or len(content) < 100:  # 短すぎる場合も全段落を試す
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
            
            # 言語の検出を試みる
            try:
                # 簡易的な言語検出
                is_japanese = any([ord(c) > 0x3000 for c in content[:100]])
                language = "ja" if is_japanese else "en"
            except:
                language = "unknown"
            
            return {
                'url': url,
                'title': title,
                'meta_description': meta_desc,
                'content': content,
                'language': language,
                'extracted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        else:
            print(f"エラー: URLからのコンテンツ取得に失敗しました - ステータスコード {response.status_code}")
            return None
            
    except Exception as e:
        print(f"URL {url} からのコンテンツ抽出中にエラーが発生しました: {e}")
        return None

def search_and_extract_data(search_queries, num_pages_per_query=2, max_articles=20, language=None):
    """
    検索クエリのリストを実行し、結果からコンテンツを抽出する
    
    Parameters:
    search_queries (list): 検索クエリのリスト
    num_pages_per_query (int): クエリごとに取得するページ数
    max_articles (int): 抽出する最大記事数
    language (str): 言語設定（例: 'ja'は日本語）
    
    Returns:
    pandas.DataFrame: 抽出したデータを含むDataFrame
    """
    all_urls = []
    all_content_data = []
    
    # 各検索クエリを実行
    for query in search_queries:
        print(f"検索クエリ '{query}' を処理中...")
        search_results = get_search_results(query, num_pages=num_pages_per_query, language=language)
        
        # 検索結果からURLを収集
        urls = [result['url'] for result in search_results]
        all_urls.extend(urls)
        
        # URLの重複を削除
        unique_urls = list(set(all_urls))
        print(f"検索クエリ '{query}' から {len(urls)} 個のURLを収集")
        
        # 最大記事数に達したかチェック
        if len(unique_urls) >= max_articles:
            unique_urls = unique_urls[:max_articles]
            break
    
    # 各URLからコンテンツを抽出
    print(f"計 {len(unique_urls)} 個のユニークURLからコンテンツを抽出中...")
    for url in unique_urls:
        content_data = extract_content_from_url(url)
        if content_data:
            all_content_data.append(content_data)
            print(f"URLからコンテンツを抽出: {url}")
        
        # サーバーに負荷をかけないように、リクエスト間に遅延を入れる
        time.sleep(random.uniform(3, 8))
    
    # 結果をDataFrameに変換
    if all_content_data:
        df = pd.DataFrame(all_content_data)
        return df
    else:
        print("抽出されたデータがありません")
        return pd.DataFrame()

def save_data(df, filename):
    """
    データをJSONまたはCSVとして保存する
    
    Parameters:
    df (pandas.DataFrame): 保存するデータフレーム
    filename (str): 保存先のファイル名
    """
    # フォルダが存在しない場合は作成
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    if filename.endswith('.json'):
        # JSONとして保存
        df.to_json(filename, orient='records', force_ascii=False, indent=2)
    else:
        # CSVとして保存
        df.to_csv(filename, index=False, encoding='utf-8-sig')  # BOMありUTF-8で日本語も正しく表示
    
    print(f"データを {filename} に保存しました")

def main():
    # リモートワークに関連する検索クエリのリスト
    search_queries = [
        "remote work productivity statistics",
        "remote work communication challenges",
        "effective remote team management",
        "remote work tools comparison",
        "remote work benefits for companies",
        "remote work productivity measurement",
        "challenges of remote work collaboration",
        "time management in remote work environment"
    ]
    
    # 日本語のクエリリスト
    japanese_search_queries = [
        'リモートワーク 生産性 統計',
        'リモートワーク コミュニケーション 課題',
        'リモートチーム 効果的な管理',
        'リモートワーク ツール 比較',
        'リモートワーク 企業にとっての利点',
        'リモートワーク 生産性 測定',
        'リモートワーク コラボレーション 課題',
        'リモートワーク環境 時間管理'
    ]
    
    # 日本語と英語のデータを収集（出力ディレクトリを確保）
    os.makedirs('data', exist_ok=True)
    
    # 英語データの収集
    print("英語のデータを収集中...")
    data_en = search_and_extract_data(search_queries, num_pages_per_query=2, max_articles=15)
    
    # 日本語データの収集
    print("日本語のデータを収集中...")
    data_jp = search_and_extract_data(japanese_search_queries, num_pages_per_query=2, max_articles=15, language="ja")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # データの保存
    if not data_en.empty:
        save_data(data_en, f'data/remote_work_data_en_{timestamp}.csv')
        
        # 簡単な統計を表示
        print(f"\n英語データ収集の統計:")
        print(f"収集した記事数: {len(data_en)}")
        if 'content' in data_en.columns:
            print(f"平均コンテンツ長: {data_en['content'].str.len().mean():.0f} 文字")
        
        # 結果のサンプルを確認
        print("\n英語データサンプル:")
        print(data_en[['title', 'url']].head())
    
    if not data_jp.empty:
        save_data(data_jp, f'data/remote_work_data_jp_{timestamp}.csv')
        
        # 簡単な統計を表示
        print(f"\n日本語データ収集の統計:")
        print(f"収集した記事数: {len(data_jp)}")
        if 'content' in data_jp.columns:
            print(f"平均コンテンツ長: {data_jp['content'].str.len().mean():.0f} 文字")
        
        # 結果のサンプルを確認
        print("\n日本語データサンプル:")
        print(data_jp[['title', 'url']].head())
    
    # 両方のデータを結合して保存する場合
    if not data_en.empty or not data_jp.empty:
        all_data = pd.concat([data_en, data_jp], ignore_index=True)
        save_data(all_data, f'data/remote_work_all_data_{timestamp}.csv')
        print(f"合計 {len(all_data)} 件のデータを保存しました")
    else:
        print("抽出されたデータがありません")

if __name__ == "__main__":
    main()
