"""
VerifyChain - Certificate Verification Using Blockchain
Foundation of Blockchain mini project.

Run:   python app.py        (Mac/Linux: python3 app.py)
The browser opens automatically at http://localhost:8000

Only the Python standard library is used, so no pip install is needed.
"""

import hashlib
import json
import os
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
CHAIN_FILE = os.path.join(HERE, "chain.json")

# Proof of Work: a block's hash must start with this many zeros.
DIFFICULTY = 3

# The fields that are hashed to form a block's fingerprint.
BLOCK_FIELDS = (
    "index", "timestamp", "student", "course", "cert_id",
    "issued_on", "cert_hash", "previous_hash", "nonce",
)


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def certificate_hash(student, course, cert_id, issued_on):
    """Fingerprint of one certificate. Any change in the details changes this hash."""
    payload = "|".join(s.strip().lower() for s in (student, course, cert_id, issued_on))
    return sha256(payload)


def block_hash(block):
    """Fingerprint of a whole block (includes the previous block's hash and the nonce)."""
    body = {key: block[key] for key in BLOCK_FIELDS}
    return sha256(json.dumps(body, sort_keys=True))


class Blockchain:
    def __init__(self, path=CHAIN_FILE):
        self.path = path
        self.chain = []
        self._load()

    # ---------- storage ----------
    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.chain = json.load(f)
        if not self.chain:
            self._create_genesis()

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.chain, f, indent=2)

    def _create_genesis(self):
        genesis = {
            "index": 0,
            "timestamp": time.time(),
            "student": "Genesis Block",
            "course": "-",
            "cert_id": "GENESIS",
            "issued_on": "-",
            "cert_hash": "0" * 64,
            "previous_hash": "0" * 64,
        }
        self.chain = [self._mine(genesis)]
        self._save()

    def reset(self):
        self._create_genesis()

    # ---------- mining (Proof of Work) ----------
    @staticmethod
    def _mine(block):
        block["nonce"] = 0
        while True:
            digest = block_hash(block)
            if digest.startswith("0" * DIFFICULTY):
                block["hash"] = digest
                return block
            block["nonce"] += 1

    # ---------- operations ----------
    def find(self, cert_id):
        for block in self.chain[1:]:
            if block["cert_id"].strip().lower() == cert_id.strip().lower():
                return block
        return None

    def issue(self, student, course, cert_id, issued_on):
        if self.find(cert_id):
            return False, "A certificate with this ID is already on the blockchain."
        block = {
            "index": len(self.chain),
            "timestamp": time.time(),
            "student": student.strip(),
            "course": course.strip(),
            "cert_id": cert_id.strip(),
            "issued_on": issued_on.strip(),
            "cert_hash": certificate_hash(student, course, cert_id, issued_on),
            "previous_hash": self.chain[-1]["hash"],
        }
        self.chain.append(self._mine(block))
        self._save()
        return True, "Certificate stored in Block #%d (nonce %d)." % (block["index"], block["nonce"])

    def is_valid(self):
        """Re-check every block. Returns (True/False, message)."""
        for i, block in enumerate(self.chain):
            if block_hash(block) != block["hash"]:
                return False, "Block #%d has been modified (its hash does not match)." % i
            if not block["hash"].startswith("0" * DIFFICULTY):
                return False, "Block #%d has no valid Proof of Work." % i
            if i > 0 and block["previous_hash"] != self.chain[i - 1]["hash"]:
                return False, "Block #%d is not linked to Block #%d." % (i, i - 1)
        return True, "Blockchain is valid. No tampering detected."

    def verify(self, student, course, cert_id, issued_on):
        block = self.find(cert_id)
        if block is None:
            return {"status": "fake", "message": "FAKE: no certificate with this ID exists on the blockchain."}
        if certificate_hash(student, course, cert_id, issued_on) != block["cert_hash"]:
            return {"status": "fake", "message": "FAKE: the details do not match the certificate stored on the blockchain."}
        ok, message = self.is_valid()
        if not ok:
            return {"status": "tampered", "message": "WARNING: details match, but the blockchain itself was tampered with. " + message}
        return {"status": "valid", "message": "VALID: this certificate is genuine (found in Block #%d)." % block["index"]}

    def tamper_demo(self):
        """For demonstration only: secretly edit a stored record so the chain breaks."""
        if len(self.chain) < 2:
            return False, "Issue at least one certificate first."
        self.chain[1]["student"] = "Tampered Name"
        self._save()
        return True, "Block #1 was edited without re-mining it."


# ======================================================================
# Web page (HTML/CSS/JS in one string, so the project stays a single file)
# ======================================================================
PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VerifyChain</title>
<style>
  body { font-family: Calibri, Arial, sans-serif; margin: 0; background: #f1f5f9; color: #0b1f3a; }
  header { background: #0b1f3a; color: #fff; padding: 20px 32px; }
  header h1 { margin: 0; font-size: 28px; }
  header p { margin: 4px 0 0; color: #f5a524; }
  main { max-width: 1000px; margin: 24px auto; padding: 0 16px; display: grid; gap: 20px; grid-template-columns: 1fr 1fr; }
  section { background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.12); }
  section.wide { grid-column: 1 / span 2; }
  h2 { margin-top: 0; font-size: 20px; }
  label { display: block; font-size: 14px; margin-top: 10px; }
  input { width: 100%; box-sizing: border-box; padding: 8px; font-size: 15px; border: 1px solid #94a3b8; border-radius: 6px; }
  button { margin-top: 14px; margin-right: 8px; padding: 9px 16px; font-size: 15px; border: 0; border-radius: 6px; background: #0b1f3a; color: #fff; cursor: pointer; }
  button.alt { background: #64748b; }
  button.warn { background: #b91c1c; }
  .msg { margin-top: 12px; padding: 10px; border-radius: 6px; font-weight: bold; display: none; }
  .msg.ok { background: #dcfce7; color: #166534; display: block; }
  .msg.bad { background: #fee2e2; color: #991b1b; display: block; }
  .msg.warn { background: #fef3c7; color: #92400e; display: block; }
  .block { border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; margin-top: 10px; font-family: Consolas, monospace; font-size: 13px; white-space: pre-wrap; word-break: break-all; }
  @media (max-width: 760px) { main { grid-template-columns: 1fr; } section.wide { grid-column: 1; } }
</style>
</head>
<body>
<header>
  <h1>VerifyChain</h1>
  <p>Certificate Verification Using Blockchain</p>
</header>
<main>
  <section>
    <h2>1. Issue a certificate (college)</h2>
    <label>Student name</label><input id="i_student">
    <label>Course</label><input id="i_course">
    <label>Certificate ID</label><input id="i_id">
    <label>Issued on</label><input id="i_date" placeholder="e.g. 2026-11-23">
    <button onclick="issue()">Store on blockchain</button>
    <div id="i_out" class="msg"></div>
  </section>

  <section>
    <h2>2. Verify a certificate (employer)</h2>
    <label>Student name</label><input id="v_student">
    <label>Course</label><input id="v_course">
    <label>Certificate ID</label><input id="v_id">
    <label>Issued on</label><input id="v_date">
    <button onclick="verify()">Verify</button>
    <div id="v_out" class="msg"></div>
  </section>

  <section class="wide">
    <h2>3. The blockchain</h2>
    <div id="status" class="msg"></div>
    <button class="alt" onclick="loadChain()">Check chain integrity</button>
    <button class="warn" onclick="tamper()">Demo: tamper with Block #1</button>
    <button class="alt" onclick="resetChain()">Reset chain</button>
    <div id="chain"></div>
  </section>
</main>

<script>
async function api(path, body) {
  const options = body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {};
  const response = await fetch(path, options);
  return response.json();
}
function val(id) { return document.getElementById(id).value.trim(); }
function show(id, text, kind) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = "msg " + kind;
}
function details(prefix) {
  return { student: val(prefix + "_student"), course: val(prefix + "_course"), cert_id: val(prefix + "_id"), issued_on: val(prefix + "_date") };
}
async function issue() {
  const res = await api("/api/issue", details("i"));
  show("i_out", res.message, res.ok ? "ok" : "bad");
  loadChain();
}
async function verify() {
  const res = await api("/api/verify", details("v"));
  const kind = res.status === "valid" ? "ok" : (res.status === "tampered" ? "warn" : "bad");
  show("v_out", res.message, kind);
}
async function tamper() {
  const res = await api("/api/tamper", {});
  alert(res.message);
  loadChain();
}
async function resetChain() {
  await api("/api/reset", {});
  loadChain();
}
async function loadChain() {
  const data = await api("/api/chain");
  show("status", data.message, data.valid ? "ok" : "bad");
  const box = document.getElementById("chain");
  box.innerHTML = "";
  data.chain.forEach(function (b) {
    const div = document.createElement("div");
    div.className = "block";
    div.textContent =
      "Block #" + b.index + "   (nonce " + b.nonce + ")\\n" +
      "Student: " + b.student + "\\n" +
      "Course: " + b.course + "   |   ID: " + b.cert_id + "   |   Issued: " + b.issued_on + "\\n" +
      "Certificate hash: " + b.cert_hash.slice(0, 24) + "...\\n" +
      "Previous hash:    " + b.previous_hash.slice(0, 24) + "...\\n" +
      "Block hash:       " + b.hash.slice(0, 24) + "...";
    box.appendChild(div);
  });
}
loadChain();
</script>
</body>
</html>
"""


# ======================================================================
# Tiny web server
# ======================================================================
class Handler(BaseHTTPRequestHandler):
    blockchain = None  # set in main()

    def _send(self, code, payload, content_type="application/json"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(200, PAGE.encode("utf-8"), "text/html")
        elif self.path == "/api/chain":
            ok, message = self.blockchain.is_valid()
            self._send(200, {"chain": self.blockchain.chain, "valid": ok, "message": message})
        else:
            self._send(404, {"message": "Not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self._send(400, {"ok": False, "message": "Invalid request."})

        if self.path in ("/api/issue", "/api/verify"):
            fields = [str(body.get(k, "")).strip() for k in ("student", "course", "cert_id", "issued_on")]
            if not all(fields) or any(len(f) > 200 for f in fields):
                return self._send(200, {"ok": False, "status": "fake", "message": "Please fill in all four fields."})
            if self.path == "/api/issue":
                ok, message = self.blockchain.issue(*fields)
                return self._send(200, {"ok": ok, "message": message})
            return self._send(200, self.blockchain.verify(*fields))

        if self.path == "/api/tamper":
            ok, message = self.blockchain.tamper_demo()
            return self._send(200, {"ok": ok, "message": message})

        if self.path == "/api/reset":
            self.blockchain.reset()
            return self._send(200, {"ok": True, "message": "Chain reset."})

        self._send(404, {"message": "Not found"})


def main():
    Handler.blockchain = Blockchain()
    port = int(os.environ.get("PORT", 8000))
    try:
        host = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
        server = HTTPServer((host, port), Handler)
    except OSError:
        print("Port %d is already in use. Close the other program, or run with a different port, e.g. PORT=8001 python app.py" % port)
        return
    url = "http://localhost:%d" % port
    print("VerifyChain running at %s  (press Ctrl+C to stop)" % url)
    if not os.environ.get("NO_BROWSER"):
        threading.Timer(1.0, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
