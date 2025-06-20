
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


TEST_URL = 'http://httpbin.org/ip'  # チェック対象URL
TIMEOUT = 5                         # タイムアウト

# ファイルからプロキシリストを読み込む
def load_proxies_file(filepath: str) -> list[str]:
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# プロキシが生きているか
def is_proxy_alive(proxy: str) -> tuple[str, bool]:
    try:
        response = requests.get(TEST_URL, proxies={"http": proxy, "https": proxy}, timeout=TIMEOUT)
        if response.status_code == 200:
            return (proxy, True)
    except requests.RequestException:
        pass
    return (proxy, False)

# プロキシをちぇっく
def check_proxies(proxy_list: list[str]) -> None:
    print("startingg...\n")
    alive = []
    dead = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(is_proxy_alive, proxy): proxy for proxy in proxy_list}
        for future in as_completed(future_to_proxy):
            proxy, status = future.result()
            if status:
                print(f"[✓]: {proxy}")
                alive.append(proxy)
            else:
                print(f"[✗] died: {proxy}")
                dead.append(proxy)

    print("\n=== 結果 ===")
    print(f"生存プロキシ: {len(alive)}")
    print(f"死亡プロキシ: {len(dead)} ")

    # 生きているプロキシを保存
    with open("alive_proxies.txt", "w") as f:
        for proxy in alive:
            f.write(proxy + "\n")

if __name__ == '__main__':
    proxy_list = load_proxies_file('proxy.txt')
    check_proxies(proxy_list)
