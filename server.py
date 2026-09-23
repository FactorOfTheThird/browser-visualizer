"""Serves the visualizer and fetches YouTube audio via yt-dlp (same origin, so Web Audio can analyse it).
Run: python server.py  ->  http://127.0.0.1:8000"""
import http.server, subprocess, urllib.parse, pathlib, shutil

ROOT = pathlib.Path(__file__).parent
CACHE = ROOT / "cache"
YT_HOSTS = ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be",
            "soundcloud.com", "www.soundcloud.com", "m.soundcloud.com", "on.soundcloud.com")
TYPES = {".m4a": "audio/mp4", ".mp4": "audio/mp4", ".webm": "audio/webm", ".opus": "audio/ogg", ".mp3": "audio/mpeg"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path != "/yt":
            return super().do_GET()
        url = urllib.parse.parse_qs(u.query).get("url", [""])[0]
        p = urllib.parse.urlparse(url)
        if p.scheme != "https" or p.hostname not in YT_HOSTS:
            return self.send_error(400, "Not a YouTube or SoundCloud URL")
        r = subprocess.run(
            [shutil.which("yt-dlp") or "yt-dlp", "-f", "bestaudio[ext=m4a]/bestaudio", "--no-playlist",
             *(["--js-runtimes", "node"] if shutil.which("node") else []), "--encoding", "utf-8", "-o", str(CACHE / "%(id)s.%(ext)s"),
             "--print", "after_move:%(title)s", "--print", "after_move:%(track,title)s",
             "--print", "after_move:%(artist,creator,uploader|)s", "--print", "after_move:filepath", "--", url],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        lines = r.stdout.strip().splitlines()
        if r.returncode or len(lines) < 4:
            return self.send_error(502, "yt-dlp failed", (r.stderr or r.stdout)[-500:])
        f = pathlib.Path(lines[-1])
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", TYPES.get(f.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Title", urllib.parse.quote(lines[-4]))   # full title (also keys saved drop markers)
        self.send_header("X-Track", urllib.parse.quote(lines[-3]))   # track name if known, else title
        self.send_header("X-Artist", urllib.parse.quote(lines[-2]))  # artist / uploader
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print("Trap visualizer on http://127.0.0.1:8000")
    http.server.ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
