# Trap Visualizer

A Trap Nation-style audio visualizer that runs in the browser. Load a song from a file, YouTube or SoundCloud, pick a logo, background and colors, mark the drops, then render an MP4.

## Requirements

- Python 3.7+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) on your `PATH`, only needed for YouTube/SoundCloud links (`pip install yt-dlp`)
- [Node.js](https://nodejs.org/), recommended for YouTube, because yt-dlp uses it to solve YouTube's player challenges
- Chrome, Edge or Firefox 130+ (rendering uses WebCodecs)

## Run it

```bash
python server.py
```

Open http://127.0.0.1:8000. You need nothing else to use it on your own machine.

| Flag | Default | |
|---|---|---|
| `--host` | `127.0.0.1` | Address to bind. `0.0.0.0` listens on every network interface. |
| `--port` | `8000` | Port to listen on. |

Downloaded songs are kept in `cache/`. Delete it whenever you like.

## Self-hosting

### Do you need HTTPS?

Browsers only allow video encoding (WebCodecs) on **HTTPS pages or `localhost`**:

| How you open it | Preview | Render MP4 |
|---|---|---|
| `http://127.0.0.1:8000` on the same machine | ✅ | ✅ |
| `http://192.168.x.x:8000` from another device | ✅ | ❌ |
| `https://…` through a reverse proxy | ✅ | ✅ |

If you only run it on your own computer, stop here. Plain `python server.py` is all you need.

If you want other devices to use it, put it behind HTTPS.

### HTTPS with Caddy (recommended)

[Caddy](https://caddyserver.com/) gets and renews certificates for you. Leave `server.py` on its default `127.0.0.1` so it's only reachable through Caddy:

```bash
python server.py
```

**With a domain** pointing at your server (ports 80 and 443 open), write a `Caddyfile`:

```
viz.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

**Home network, no domain:** Caddy can use its own local certificate authority:

```
https://192.168.1.50 {
    tls internal
    reverse_proxy 127.0.0.1:8000
}
```

Other devices will show a certificate warning until you trust Caddy's root certificate on them. `caddy trust` does this on the server machine. On other devices, import the root certificate from Caddy's data directory.

Then run:

```bash
caddy run
```

### Lock it down if it's public

Anyone who can reach the server can make it download audio through yt-dlp, and `cache/` grows forever. If you expose it to the internet, add a password in Caddy:

```
viz.example.com {
    basic_auth {
        me <hash from `caddy hash-password`>
    }
    reverse_proxy 127.0.0.1:8000
}
```

and clear `cache/` now and then (cron, a scheduled task, etc.).

### Quick LAN workarounds without HTTPS

- **SSH tunnel:** `ssh -L 8000:127.0.0.1:8000 you@server`, then open `http://127.0.0.1:8000` locally. It counts as localhost, so rendering works.
- **Chrome/Edge flag:** in `chrome://flags/#unsafely-treat-insecure-origin-as-secure`, add `http://192.168.x.x:8000`. This is per-browser and meant for testing.

## License

MIT, see [LICENSE](LICENSE). Bundles [mp4-muxer](https://github.com/Vanilagy/mp4-muxer) (MIT, see `vendor/mp4-muxer.LICENSE`).
