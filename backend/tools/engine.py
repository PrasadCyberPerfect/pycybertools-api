"""
PyCyberTools — Tool Engine
All real scanning/cracking logic.
Author: PrasadCyberPerfect
"""
import socket, threading, hashlib, secrets, string, math, re, time, os

# ── PORT SCANNER ─────────────────────────────────────────────
def port_scan(target, start, end, thread_count=150):
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        return {"error": f"Cannot resolve hostname: {target}"}

    open_ports = []
    lock = threading.Lock()

    def probe(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.7)
            if s.connect_ex((ip, port)) == 0:
                try:    svc = socket.getservbyport(port)
                except: svc = "unknown"
                with lock:
                    open_ports.append({"port": port, "service": svc})
            s.close()
        except: pass

    sem = threading.Semaphore(thread_count)
    def worker(p):
        with sem: probe(p)

    threads = [threading.Thread(target=worker, args=(p,), daemon=True) for p in range(start, end+1)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)

    open_ports.sort(key=lambda x: x["port"])
    return {"ip": ip, "target": target, "open_ports": open_ports, "count": len(open_ports)}


# ── BANNER GRABBER ───────────────────────────────────────────
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 5432, 6379, 8080, 8443]

def banner_grab(target, ports, timeout=3.0):
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        return {"error": f"Cannot resolve hostname: {target}"}

    results = []
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((ip, port))
            if port in (80, 8080, 8443, 443):
                s.send(b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n")
            banner = s.recv(1024).decode("utf-8", errors="ignore").strip()
            s.close()
            first = banner.split("\n")[0][:120] if banner else "(connected — no banner)"
            results.append({"port": port, "status": "open", "banner": first})
        except (ConnectionRefusedError, socket.timeout):
            results.append({"port": port, "status": "closed", "banner": ""})
        except Exception as e:
            results.append({"port": port, "status": "error", "banner": str(e)[:60]})

    grabbed = sum(1 for r in results if r["status"] == "open")
    return {"ip": ip, "results": results, "grabbed": grabbed, "total": len(ports)}


# ── HASH CRACKER ─────────────────────────────────────────────
def identify_hash(h):
    return {32:"MD5",40:"SHA-1",56:"SHA-224",64:"SHA-256",
            96:"SHA-384",128:"SHA-512"}.get(len(h.strip()),"Unknown")

def crack_hash(target_hash, algo, wordlist_path=""):
    target_hash = target_hash.strip().lower()
    algo_map = {"md5":"md5","sha1":"sha1","sha256":"sha256","sha512":"sha512"}

    if algo == "auto":
        algo = {32:"md5",40:"sha1",64:"sha256",128:"sha512"}.get(len(target_hash))
        if not algo:
            return {"error": "Cannot auto-detect hash type. Please select manually."}

    algo_key = algo_map.get(algo.lower())
    if not algo_key:
        return {"error": f"Unsupported algorithm: {algo}"}

    def h(word):
        return hashlib.new(algo_key, word.encode()).hexdigest()

    builtins = [
        "password","123456","admin","root","toor","letmein","qwerty",
        "abc123","monkey","dragon","pass","test","1234","12345",
        "password1","iloveyou","sunshine","master","hello","welcome",
        "shadow","superman","batman","login","default","guest",
        "football","baseball","soccer","hockey","trustno1","access",
        "mustang","michael","jessica","passw0rd","princess","charlie",
    ]

    t0 = time.time()
    for i, w in enumerate(builtins, 1):
        if h(w) == target_hash:
            return {"found":True,"password":w,"algo":algo_key.upper(),
                    "attempts":i,"time":round(time.time()-t0,3),"source":"built-in list"}

    attempts = len(builtins)
    if wordlist_path and os.path.isfile(wordlist_path):
        try:
            with open(wordlist_path,"r",encoding="utf-8",errors="ignore") as f:
                for line in f:
                    word = line.strip()
                    if not word: continue
                    attempts += 1
                    if h(word) == target_hash:
                        return {"found":True,"password":word,"algo":algo_key.upper(),
                                "attempts":attempts,"time":round(time.time()-t0,3),"source":wordlist_path}
        except Exception as e:
            return {"error": f"Wordlist error: {e}"}

    return {"found":False,"algo":algo_key.upper(),"attempts":attempts,
            "time":round(time.time()-t0,3),"note":"Not found in built-in list. Provide a wordlist for full cracking."}


# ── SUBDOMAIN FINDER ─────────────────────────────────────────
BUILTIN_SUBS = [
    "www","mail","ftp","smtp","pop","pop3","imap","api","dev","staging",
    "test","admin","blog","shop","app","cdn","ns1","ns2","vpn","remote",
    "portal","git","secure","mx","forum","support","m","static","media",
    "img","images","news","beta","demo","dashboard","panel","manage",
    "login","auth","docs","help","status","monitor","internal","intranet",
    "corp","data","db","ssh","server","cloud","files","webmail","cpanel",
]

def subdomain_find(domain, wordlist_path=""):
    words = BUILTIN_SUBS.copy()
    if wordlist_path and os.path.isfile(wordlist_path):
        try:
            with open(wordlist_path,"r",encoding="utf-8",errors="ignore") as f:
                extra = [l.strip() for l in f if l.strip()]
            words = list(dict.fromkeys(extra + words))
        except: pass

    found = []
    lock = threading.Lock()

    def check(word):
        sub = f"{word}.{domain}"
        try:
            ip = socket.gethostbyname(sub)
            with lock: found.append({"subdomain": sub, "ip": ip})
        except: pass

    threads = [threading.Thread(target=check, args=(w,), daemon=True) for w in words]
    for t in threads: t.start()
    for t in threads: t.join(timeout=8)

    found.sort(key=lambda x: x["subdomain"])
    return {"domain": domain, "found": found, "tried": len(words), "count": len(found)}


# ── PASSWORD GENERATOR ───────────────────────────────────────
def _entropy(pwd):
    sz = 0
    if any(c in string.ascii_lowercase for c in pwd): sz += 26
    if any(c in string.ascii_uppercase for c in pwd): sz += 26
    if any(c in string.digits for c in pwd):          sz += 10
    if any(c in string.punctuation for c in pwd):     sz += 32
    return round(len(pwd) * math.log2(sz), 1) if sz else 0.0

def _strength(e):
    if e < 28:  return "Very Weak"
    if e < 40:  return "Weak"
    if e < 60:  return "Fair"
    if e < 100: return "Strong"
    return "Very Strong"

def gen_passwords(length, count, upper, digits, symbols, no_ambiguous):
    charset = string.ascii_lowercase
    if upper:   charset += string.ascii_uppercase
    if digits:  charset += string.digits
    if symbols: charset += string.punctuation
    if no_ambiguous:
        for c in "0O1lI|`'\"\\": charset = charset.replace(c, "")
    if not charset:
        return {"error": "Select at least one character set."}

    results = []
    for _ in range(count):
        guaranteed = []
        if upper:   guaranteed.append(secrets.choice(string.ascii_uppercase))
        if digits:  guaranteed.append(secrets.choice(string.digits))
        if symbols: guaranteed.append(secrets.choice(string.punctuation))
        rest = [secrets.choice(charset) for _ in range(max(0, length - len(guaranteed)))]
        combined = guaranteed + rest
        secrets.SystemRandom().shuffle(combined)
        pwd = "".join(combined)
        e = _entropy(pwd)
        results.append({"password": pwd, "entropy": e, "strength": _strength(e)})

    return {"passwords": results}


# ── WHOIS LOOKUP ─────────────────────────────────────────────
WHOIS_SERVERS = {
    "com":"whois.verisign-grs.com","net":"whois.verisign-grs.com",
    "org":"whois.pir.org","io":"whois.nic.io","in":"whois.registry.in",
    "uk":"whois.nic.uk","de":"whois.denic.de","co":"whois.nic.co",
    "ai":"whois.nic.ai","xyz":"whois.nic.xyz",
}

def _whois_query(server, query, timeout=10.0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((server, 43))
        s.send(f"{query}\r\n".encode())
        raw = b""
        while True:
            chunk = s.recv(4096)
            if not chunk: break
            raw += chunk
        s.close()
        return raw.decode("utf-8", errors="ignore")
    except Exception as e:
        return f"[ERROR] {e}"

def whois_lookup(target):
    tld = target.rsplit(".",1)[-1].lower() if "." in target else ""
    server = WHOIS_SERVERS.get(tld, "whois.iana.org")
    raw = _whois_query(server, target)
    if server == "whois.iana.org":
        m = re.search(r"(?:refer|whois):\s+(\S+)", raw, re.IGNORECASE)
        if m:
            server = m.group(1).strip()
            raw = _whois_query(server, target)
    FIELDS = ["domain name","registrar","creation date","updated date",
              "expiry date","expiration date","registry expiry date",
              "name server","dnssec","status","registrant organization",
              "registrant country","netname","org","country"]
    parsed = {}
    for line in raw.splitlines():
        low = line.lower().strip()
        for f in FIELDS:
            if low.startswith(f) and ":" in line:
                k, _, v = line.partition(":")
                k = k.strip(); v = v.strip()
                if k not in parsed and v:
                    parsed[k] = v
    return {"server": server, "parsed": parsed, "raw": raw[:5000]}


# ── DNS LOOKUP ───────────────────────────────────────────────
def dns_lookup(target):
    results = {}
    try:    results["A"] = socket.gethostbyname_ex(target)[2]
    except: results["A"] = []
    try:    results["PTR"] = [socket.gethostbyaddr(results["A"][0])[0]] if results["A"] else []
    except: results["PTR"] = []
    return {"target": target, "records": results}
