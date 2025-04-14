import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from dotenv import load_dotenv
from datetime import datetime

# 環境変数の読み込み（APIキーなどを保存する場合）
load_dotenv()

# ユーザーエージェントのリスト（ブロックを避けるため）
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

def get_search_results(query, num_pages=2):
    """
    検索エンジンから検索結果を取得する
    
    Parameters:
    query (str): 検索クエリ
    num_pages (int): 取得するページ数
    
    Returns:
    list: 検索結果のURL、タイトル、スニペットのリスト
    """
    all_results = []
    
    # Google検索のURLテンプレート
    # 注意: Googleは自動化されたクエリを検出すると制限する場合があります
    # 本番環境では、Google Search APIなどの公式APIを使用することを推奨
    search_url = "https://www.google.com/search?q={}&start={}"
    
    for page in range(num_pages):
        # 検索ページのインデックス（10件ごと）
        start_idx = page * 10
        
        # ランダムなユーザーエージェントを選択
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # リクエストを送信
        response = requests.get(
            search_url.format(query.replace(' ', '+'), start_idx),
            headers=headers
        )
        
        # レスポンスのステータスコードをチェック
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Google検索結果の各エントリを取得
            search_results = soup.select('div.g')
            
            for result in search_results:
                try:
                    title_element = result.select_one('h3')
                    if not title_element:
                        continue
                        
                    title = title_element.get_text()
                    
                    link_element = result.select_one('a')
                    if not link_element:
                        continue
                        
                    link = link_element.get('href')
                    
                    # 相対URLの場合は絶対URLに変換
                    if link.startswith('/url?q='):
                        link = link.split('/url?q=')[1].split('&sa=')[0]
                    
                    # スニペット（ディスクリプション）を取得
                    snippet_element = result.select_one('div.VwiC3b')
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
            break
            
        # サーバーに負荷をかけないように、リクエスト間に遅延を入れる
        time.sleep(random.uniform(3, 7))
    
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
            'User-Agent': random.choice(USER_AGENTS)
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
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
            for selector in ['article', 'main', '.post-content', '.entry-content', '#content']:
                content_element = soup.select_one(selector)
                if content_element:
                    content = content_element.get_text(separator='\n', strip=True)
                    break
            
            # コンテンツが見つからない場合は、すべての段落テキストを収集
            if not content:
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
            
            return {
                'url': url,
                'title': title,
                'meta_description': meta_desc,
                'content': content,
                'extracted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        else:
            print(f"エラー: URLからのコンテンツ取得に失敗しました - ステータスコード {response.status_code}")
            return None
            
    except Exception as e:
        print(f"URL {url} からのコンテンツ抽出中にエラーが発生しました: {e}")
        return None

def search_and_extract_data(search_queries, num_pages_per_query=2, max_articles=20):
    """
    検索クエリのリストを実行し、結果からコンテンツを抽出する
    
    Parameters:
    search_queries (list): 検索クエリのリスト
    num_pages_per_query (int): クエリごとに取得するページ数
    max_articles (int): 抽出する最大記事数
    
    Returns:
    pandas.DataFrame: 抽出したデータを含むDataFrame
    """
    all_urls = []
    all_content_data = []
    
    # 各検索クエリを実行
    for query in search_queries:
        print(f"検索クエリ '{query}' を処理中...")
        search_results = get_search_results(query, num_pages=num_pages_per_query)
        
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
        time.sleep(random.uniform(2, 5))
    
    # 結果をDataFrameに変換
    if all_content_data:
        df = pd.DataFrame(all_content_data)
        return df
    else:
        print("抽出されたデータがありません")
        return pd.DataFrame()

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
    
    # データの収集と抽出
    data = search_and_extract_data(search_queries, num_pages_per_query=2, max_articles=30)
    
    # 結果を保存
    if not data.empty:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data.to_csv(f'remote_work_data_{timestamp}.csv', index=False, encoding='utf-8')
        print(f"データを remote_work_data_{timestamp}.csv に保存しました")
        
        # 簡単な統計を表示
        print(f"\nデータ収集の統計:")
        print(f"収集した記事数: {len(data)}")
        print(f"平均コンテンツ長: {data['content'].str.len().mean():.0f} 文字")
        
        # 結果のサンプルを確認
        print("\nデータサンプル:")
        print(data[['title', 'url']].head())
    
if __name__ == "__main__":
    main()