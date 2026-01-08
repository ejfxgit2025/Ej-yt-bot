#!/usr/bin/env python3
"""
cookie_checker.py
- Validates cookies.txt (Netscape format)
- Looks for youtube domains
- Runs a quick yt-dlp test download HEAD to check auth
- Prints actionable advice
"""

import os
import re
import subprocess
import sys
import tempfile

COOKIE_FN = "cookies.txt"
TEST_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # harmless public test video
YTDLP_CMD = "yt-dlp"

def find_cookie_file():
    # absolute path resolution (important on Render / Docker)
    cwd = os.getcwd()
    path = os.path.join(cwd, COOKIE_FN)
    if os.path.isfile(path):
        return path
    # also check common alt names
    alt = os.path.join(cwd, "cookies_youtube.txt")
    if os.path.isfile(alt):
        return alt
    return None

def inspect_cookies(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # quick checks
    has_netscape_header = "HTTP Cookie File" in content or content.strip().startswith("# Netscape")
    has_youtube = ".youtube.com" in content or "youtube.com" in content
    has_login_cookies_like = re.search(r"SID|HSID|SSID|SAPISID|APISID", content, re.IGNORECASE)

    lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
    sample_lines = lines[:6]

    return {
        "size_bytes": os.path.getsize(path),
        "lines_count": len(lines),
        "has_netscape_header": has_netscape_header,
        "has_youtube": has_youtube,
        "has_login_cookie_names": bool(has_login_cookies_like),
        "sample_lines": sample_lines,
    }

def run_yt_dlp_check(cookie_path, url=TEST_URL):
    """
    Runs yt-dlp in a safe test mode:
    - uses --simulate with --no-warnings and --restrict-filenames
    - captures stderr for YouTube auth error messages
    """
    cmd = [
        YTDLP_CMD,
        "--cookies", cookie_path,
        "--no-warnings",
        "--simulate",           # don't download
        "--restrict-filenames",
        "--no-playlist",
        "-f", "best",
        url
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except FileNotFoundError:
        return {"error": "yt-dlp not found. Run: pip install -U yt-dlp"}
    except subprocess.TimeoutExpired:
        return {"error": "yt-dlp timed out (process hung)."}
    except Exception as e:
        return {"error": f"unexpected error: {e}"}

def analyze_yt_dlp_output(out):
    # common yt-dlp messages and suggested fixes
    stderr = out.get("stderr", "") or ""
    rc = out.get("returncode")

    advice = []

    if "Sign in to confirm you're not a bot" in stderr or "403" in stderr or "you are not allowed" in stderr.lower():
        advice.append("YouTube is asking for human verification: your cookies are not giving yt-dlp access. Re-export cookies while logged in and ensure the account is verified.")
    if "This video is unavailable" in stderr or "private video" in stderr.lower():
        advice.append("The video may be private or age-restricted and your cookies don't have permission. Use an account that has access.")
    if "Login required" in stderr or "ERROR: unable to download" in stderr:
        advice.append("General auth failure. Check that cookies file contains youtube.com cookies and that it wasn't exported from an incognito session.")
    if "cookies.txt" in stderr and "No such file" in stderr:
        advice.append("Shared path problem: use absolute path for cookies (check working directory).")
    if out.get("error"):
        advice.append(out["error"])

    if not advice and rc == 0:
        advice.append("Looks OK: yt-dlp simulated the download successfully with these cookies.")
    if not advice:
        advice.append("Unable to determine exact cause from yt-dlp output. Paste the stderr to get deeper help.")

    return advice

def main():
    print("=== cookies.txt deep checker ===")
    cookie_path = find_cookie_file()
    if not cookie_path:
        print(f"✖ No {COOKIE_FN} found in {os.getcwd()}. Place your cookies.txt in this folder.")
        sys.exit(1)

    print(f"Using cookie file: {cookie_path}")
    info = inspect_cookies(cookie_path)
    print(f"- file size: {info['size_bytes']} bytes, {info['lines_count']} cookie lines")
    print(f"- contains youtube domain? {'YES' if info['has_youtube'] else 'NO'}")
    print(f"- looks like Netscape cookies format? {'YES' if info['has_netscape_header'] else 'MAYBE/NO'}")
    print(f"- contains login cookie names (SID/HSID/APISID...)? {'YES' if info['has_login_cookie_names'] else 'NO'}")
    print("\nSample cookie lines:")
    for ln in info['sample_lines']:
        print("  ", ln)

    print("\nRunning yt-dlp simulate test (this uses your cookies to check auth)...")
    out = run_yt_dlp_check(cookie_path)
    if out.get("error"):
        print("✖ Error:", out["error"])
        print("→ Fix: install or upgrade yt-dlp with `pip install -U yt-dlp` and ensure it's on PATH.")
        sys.exit(1)

    print("yt-dlp return code:", out.get("returncode"))
    # print small chunk of stderr for debugging (do not paste whole cookie content)
    stderr_preview = (out.get("stderr") or "").strip()[:2000]
    print("\n--- yt-dlp stderr (preview) ---")
    print(stderr_preview or "(no stderr)")

    suggestions = analyze_yt_dlp_output(out)
    print("\n=== Suggestions & Next Steps ===")
    for s in suggestions:
        print(" -", s)

    print("\nHelpful manual fixes:")
    print("  * Re-export cookies using a browser extension like 'Get cookies.txt' while logged into YouTube.")
    print("  * Ensure the account used is phone-verified if you see frequent bot checks.")
    print("  * Use absolute cookie path in your bot (os.path.join(os.getcwd(), 'cookies.txt'))")
    print("  * Update yt-dlp: pip install -U yt-dlp")
    print("  * If errors continue, paste the yt-dlp stderr (not your cookies) so I can analyze it.")

if __name__ == "__main__":
    main()
