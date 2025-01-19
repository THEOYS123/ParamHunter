# dan ini script nya:
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from random import choice
from collections import deque
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import re
import string
import random
import time
import signal
import sys

console = Console()

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
]

extra_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


interrupted_results = {}

def signal_handler(sig, frame):
    """Handler untuk menangani CTRL+C"""
    console.print("\n[bold red][CTRL+C] Script dihentikan paksa oleh pengguna.[/bold red]")
    if interrupted_results:
        console.print("\n[bold green][HASIL] URL yang ditemukan sejauh ini:[/bold green]")
        for filter_type, urls in interrupted_results.items():
            if urls:
                table = Table(title=f"Filter: {filter_type}", show_lines=True)
                table.add_column("No", justify="center", style="cyan", no_wrap=True)
                table.add_column("URL", justify="left", style="magenta")
                for i, url in enumerate(urls, 1):
                    table.add_row(str(i), url)
                console.print(table)
    else:
        console.print("[yellow][INFO] Tidak ada hasil yang ditemukan sejauh ini.[/yellow]")
    sys.exit(0)

# Tangkap signal CTRL+C
signal.signal(signal.SIGINT, signal_handler)

def generate_random_parameter(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def make_request(url, base_url):
    """Request dengan random User-Agent, retry jika gagal tanpa proxy"""
    for _ in range(3):  # Maksimal 3 kali percobaan
        try:
            headers = {
                'User-Agent': random.choice(user_agents),
                'Referer': base_url,
                **extra_headers,
            }
            headers['X-Forwarded-For'] = '.'.join(map(str, (random.randint(0, 255) for _ in range(4))))  # IP random
            response = requests.get(url, timeout=15, headers=headers)

            if response.status_code == 403:
                console.log(f"[red][403 Forbidden] Mengakses ulang: {url}")
                time.sleep(random.randint(5, 10))  # Delay untuk menghindari block
                continue

            response.raise_for_status()  # Cek status selain 200 OK
            return response
        except requests.exceptions.RequestException as e:
            console.log(f"[yellow][ERROR] Gagal akses {url}: {e}")
            time.sleep(random.randint(5, 10))  # Delay sebelum retry
    return None

def has_query_parameter(url):
    return '?' in url and '=' in url

def crawl_website(base_url, filters, random_search=False, af_search=False, pr_search=False):
    global interrupted_results  # Variabel global untuk menyimpan hasil saat dihentikan
    visited = set()
    queue = deque([base_url])
    matching_urls = {filter_type: [] for filter_type in filters}  # Hasil disimpan berdasarkan filter
    interrupted_results = matching_urls  # Referensi hasil ke variabel global

    if random_search:
        filters.extend([generate_random_parameter() for _ in range(3)])
        console.print("[bold yellow][INFO] Menggunakan parameter random untuk pencarian.[/bold yellow]")

    if af_search:
        admin_paths = [
            '/admin', '/admin.php', '/administrator', '/adminarea', '/wp-admin', '/cpanel',
            '/admin-login', '/adminpanel', '/admin-dashboard', '/controlpanel', '/login', '/admin_login'
        ]
        filters.extend(admin_paths)
        console.print("[bold yellow][INFO] Mencari admin finder dengan filter yang relevan.[/bold yellow]")

    if pr_search:
        pr_filters = ['?id=', '?page=', '?search=', '?category=', '?product=', '?lang=', '?keyword=']
        filters.extend(pr_filters)
        console.print("[bold yellow][INFO] Mencari parameter rentan dengan filter: pr.[/bold yellow]")

    while queue:
        current_url = queue.popleft()
        if current_url in visited:
            continue

        console.log(f"[blue][SCAN] Memeriksa: {current_url}")
        response = make_request(current_url, base_url)
        if not response:
            continue

        visited.add(current_url)

        soup = BeautifulSoup(response.text, 'html.parser')
        new_urls = []

        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])
            parsed_url = urlparse(full_url)

            if parsed_url.netloc == urlparse(base_url).netloc:
                if full_url not in visited and full_url not in queue:
                    new_urls.append(full_url)

                # Cek URL berdasarkan filter
                for filter_type in filters:
                    if filter_type and isinstance(filter_type, str):
                        if re.search(re.escape(filter_type), full_url):
                            if full_url not in matching_urls[filter_type]:
                                matching_urls[filter_type].append(full_url)
                            break

        queue.extend(new_urls)

    # Output hasil berdasarkan jenis filter
    console.print("\n[bold green][HASIL] URL yang ditemukan By Ren-Xploit:[/bold green]")
    if any(matching_urls.values()):
        for filter_type, urls in matching_urls.items():
            if urls:
                table = Table(title=f"Filter: {filter_type}", show_lines=True)
                table.add_column("No", justify="center", style="cyan", no_wrap=True)
                table.add_column("URL", justify="left", style="magenta")
                for i, url in enumerate(urls, 1):
                    table.add_row(str(i), url)
                console.print(table)
    else:
        console.print("[yellow][INFO] Tidak ada URL yang cocok ditemukan.[/yellow]")
        
def show_help():
    console.print(Panel.fit("""
[bold yellow]Cara Penggunaan:[/bold yellow]
python script.py [bold cyan]URL[/bold cyan] -f [bold cyan]FILTER[/bold cyan]

[bold yellow]Contoh Penggunaan:[/bold yellow]
python script.py https://example.com -f .php .html .json

[bold yellow]Jenis Parameter yang Didukung:[/bold yellow]
- .php
- .html
- .asp
- .jsp
- .aspx
- .json
- .xml
- .txt
- .js
- dan lainnya...

[bold yellow]Fitur Tambahan:[/bold yellow]
- Random User-Agent
- Menghindari Forbidden (403)
- Tampilan hasil dalam tabel
- Deteksi URL yang valid secara otomatis
- Pencarian parameter random (seperti dorking) dengan [bold cyan]-random[/bold cyan]
- Pencarian Admin Finder dengan [bold cyan]-af[/bold cyan]
- Pencarian Parameter Rentan dengan [bold cyan]-pr[/bold cyan]

[bold yellow]Pilihan Argumen:[/bold yellow]
-h, --help : Menampilkan panduan interaktif
-f, --filter : Menentukan filter parameter yang akan dicari
-random : Mencari parameter secara random (dorking)
-af : Mencari halaman admin (admin finder)
-pr : Mencari parameter rentan
    """, title="[bold blue]Parameter Finder - Help[/bold blue]", border_style="bold green"))

def main():
    parser = argparse.ArgumentParser(
        description="Script untuk mencari parameter di website dengan filter yang sangat keren dan valid.",
        add_help=False
    )
    parser.add_argument("url", nargs="?", help="URL target (contoh: https://example.com)")
    parser.add_argument("-f", "--filter", nargs="*", help="Jenis parameter yang dicari (contoh: .php .html .json)")
    parser.add_argument("-random", action="store_true", help="Menggunakan filter random otomatis (dorking)")
    parser.add_argument("-af", action="store_true", help="Mencari halaman admin (admin finder)")
    parser.add_argument("-pr", action="store_true", help="Mencari parameter rentan")
    parser.add_argument("-h", "--help", action="store_true", help="Menampilkan panduan interaktif")

    args = parser.parse_args()

    if args.help or not args.url or (not args.filter and not args.random and not args.af and not args.pr):
        show_help()
        return

    # Validasi input URL
    if not args.url.startswith(("http://", "https://")):
        console.print("[red][ERROR] Masukkan URL yang valid dengan http:// atau https://[/red]")
        return

    filters = args.filter if args.filter else []
    
    # Tambahkan filter random jika argumen -random digunakan
    if args.random:
        random_filters = [
            f"/{generate_random_parameter()}.json",
            f"/{generate_random_parameter()}.jsp",
            f"/{generate_random_parameter()}.xml",
            f"/{generate_random_parameter()}.php",
            f"/{generate_random_parameter()}.txt",
            f"/{generate_random_parameter()}.html",
        ]
        filters.extend(random_filters)
        console.print(f"[bold yellow][INFO] Menggunakan filter random otomatis: {', '.join(random_filters)}[/bold yellow]")

    # Tambahkan filter admin finder jika -af digunakan
    if args.af:
        admin_paths = [
            '/admin', '/admin.php', '/administrator', '/adminarea', '/wp-admin', '/cpanel',
            '/admin-login', '/adminpanel', '/admin-dashboard', '/controlpanel', '/login', '/admin_login'
        ]
        filters.extend(admin_paths)
        console.print("[bold yellow][INFO] Menggunakan filter admin finder.[/bold yellow]")

    # Tambahkan filter parameter rentan jika -pr digunakan
    if args.pr:
        pr_filters = ['?id=', '?page=', '?search=', '?category=', '?product=', '?lang=', '?keyword=']
        filters.extend(pr_filters)
        console.print("[bold yellow][INFO] Menggunakan filter parameter rentan.[/bold yellow]")

    # Mulai proses crawling
    console.print(f"[bold green][INFO] Memulai crawling untuk: {args.url}[/bold green]")
    crawl_website(args.url, filters, random_search=args.random, af_search=args.af, pr_search=args.pr)

if __name__ == "__main__":
    main()
