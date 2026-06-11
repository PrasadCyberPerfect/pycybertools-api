"""
PyCyberTools — Backend API
Deploy on Render.com (free tier)
Author: PrasadCyberPerfect
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from tools.engine import (
    port_scan, banner_grab, crack_hash, identify_hash,
    subdomain_find, gen_passwords, whois_lookup, dns_lookup,
    COMMON_PORTS
)

app = Flask(__name__)
CORS(app)  # Allow requests from Vercel frontend
app.config["JSON_SORT_KEYS"] = False


@app.route("/")
def home():
    return jsonify({
        "name": "PyCyberTools API",
        "author": "PrasadCyberPerfect",
        "version": "2.0",
        "status": "online",
        "endpoints": [
            "/api/port-scan", "/api/banner-grab", "/api/hash-crack",
            "/api/subdomain", "/api/passgen", "/api/whois", "/api/dns"
        ]
    })

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/port-scan", methods=["POST"])
def api_port_scan():
    d = request.get_json(force=True) or {}
    target  = str(d.get("target", "")).strip()
    start   = max(1,     int(d.get("start",   1)))
    end     = min(65535, int(d.get("end",   1024)))
    threads = min(300,   int(d.get("threads", 150)))
    if not target:
        return jsonify(error="Target is required"), 400
    if start > end:
        return jsonify(error="Start port must be <= end port"), 400
    result = port_scan(target, start, end, threads)
    if "error" in result:
        return jsonify(**result), 400
    return jsonify(**result)

@app.route("/api/banner-grab", methods=["POST"])
def api_banner():
    d = request.get_json(force=True) or {}
    target  = str(d.get("target", "")).strip()
    raw_p   = str(d.get("ports", "")).strip()
    timeout = float(d.get("timeout", 3.0))
    if not target:
        return jsonify(error="Target is required"), 400
    ports = COMMON_PORTS
    if raw_p:
        try:
            ports = [int(p.strip()) for p in raw_p.split(",") if p.strip()]
        except ValueError:
            return jsonify(error="Invalid port list"), 400
    result = banner_grab(target, ports, timeout)
    if "error" in result:
        return jsonify(**result), 400
    return jsonify(**result)

@app.route("/api/hash-crack", methods=["POST"])
def api_hash():
    d = request.get_json(force=True) or {}
    h        = str(d.get("hash", "")).strip()
    algo     = str(d.get("algo", "auto")).strip().lower()
    wordlist = str(d.get("wordlist", "")).strip()
    if not h:
        return jsonify(error="Hash value is required"), 400
    identified = identify_hash(h)
    result = crack_hash(h, algo, wordlist)
    result["identified"] = identified
    if "error" in result:
        return jsonify(**result), 400
    return jsonify(**result)

@app.route("/api/subdomain", methods=["POST"])
def api_subdomain():
    d = request.get_json(force=True) or {}
    domain   = str(d.get("domain", "")).strip().lstrip("https://").lstrip("http://").rstrip("/")
    wordlist = str(d.get("wordlist", "")).strip()
    if not domain:
        return jsonify(error="Domain is required"), 400
    result = subdomain_find(domain, wordlist)
    return jsonify(**result)

@app.route("/api/passgen", methods=["POST"])
def api_passgen():
    d = request.get_json(force=True) or {}
    length   = min(128, max(4,  int(d.get("length", 16))))
    count    = min(50,  max(1,  int(d.get("count",   8))))
    upper    = bool(d.get("upper",       True))
    digits   = bool(d.get("digits",      True))
    symbols  = bool(d.get("symbols",     True))
    no_ambig = bool(d.get("noAmbiguous", False))
    result = gen_passwords(length, count, upper, digits, symbols, no_ambig)
    if "error" in result:
        return jsonify(**result), 400
    return jsonify(**result)

@app.route("/api/whois", methods=["POST"])
def api_whois():
    d = request.get_json(force=True) or {}
    target = str(d.get("target", "")).strip()
    if not target:
        return jsonify(error="Domain or IP is required"), 400
    result = whois_lookup(target)
    return jsonify(**result)

@app.route("/api/dns", methods=["POST"])
def api_dns():
    d = request.get_json(force=True) or {}
    target = str(d.get("target", "")).strip()
    if not target:
        return jsonify(error="Target is required"), 400
    result = dns_lookup(target)
    return jsonify(**result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
