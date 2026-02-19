#!/usr/bin/env python3
"""
Prévisualisation locale des cours (y compris les drafts)

Usage:
    python preview.py
    python preview.py --port 8080
"""

import sys
import argparse
import webbrowser
import http.server
import socketserver
import subprocess
import threading
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

class WatcherThread(threading.Thread):
    """Thread qui surveille les fichiers et rebuild si nécessaire"""
    
    def __init__(self, source_dir: Path, build_cmd: list, interval: float = 1.0):
        super().__init__(daemon=True)
        self.source_dir = source_dir
        self.build_cmd = build_cmd
        self.interval = interval
        self.running = True
        self.last_mtime = self._get_max_mtime()
    
    def _get_max_mtime(self) -> float:
        """Retourne le timestamp de modification le plus récent"""
        max_mtime = 0
        patterns = ['**/*.md', '**/*.toml', 'css/*.css', 'js/*.js']
        
        for pattern in patterns:
            for f in self.source_dir.glob(pattern):
                if f.is_file():
                    mtime = f.stat().st_mtime
                    if mtime > max_mtime:
                        max_mtime = mtime
        
        return max_mtime
    
    def run(self):
        while self.running:
            time.sleep(self.interval)
            current_mtime = self._get_max_mtime()
            
            if current_mtime > self.last_mtime:
                print("\n🔄 Changement détecté, rebuild en cours...")
                result = subprocess.run(self.build_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Rebuild terminé — Rafraîchissez le navigateur (F5)")
                else:
                    print(f"❌ Erreur de build:\n{result.stderr}")
                
                self.last_mtime = current_mtime
    
    def stop(self):
        self.running = False


def main():
    parser = argparse.ArgumentParser(description='Prévisualisation locale')
    parser.add_argument('--port', type=int, default=8000, help='Port du serveur (défaut: 8000)')
    parser.add_argument('-s', '--source', type=Path, default=Path('./cours'), help='Dossier source')
    parser.add_argument('-n', '--no-browser', action='store_true',help="N'ouvre pas de nouvel onglet dans le navigateur")
    parser.add_argument('--no-watch', action='store_true', help="Désactiver le hot reload")
    args = parser.parse_args()
    
    # Build dans un dossier temporaire
    preview_dir = SCRIPT_DIR / '.preview'
    source_dir = args.source if args.source.is_absolute() else Path.cwd() / args.source
    
    build_cmd = [
        sys.executable, str(SCRIPT_DIR / 'build.py'),
        '-s', str(source_dir),
        '-o', str(preview_dir),
        '--clean',
        '--preview'
    ]

    result = subprocess.run(build_cmd)

    if result.returncode != 0:
        print("❌ Échec du build")
        return 1
    
    rebuild_cmd = [
        sys.executable, str(SCRIPT_DIR / 'build.py'),
        '-s', str(source_dir),
        '-o', str(preview_dir),
        '--preview'
    ]

    watcher = None
    if not args.no_watch:
        watcher = WatcherThread(source_dir, rebuild_cmd)
        watcher.start()
        print("** Hot reload activé **")
    import os
    os.chdir(preview_dir)
    
    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True 
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        url = f"http://localhost:{args.port}"
        print(f"\n🌐 Serveur démarré : {url}")
        print("   Ctrl+C pour arrêter\n")
        if not args.no_browser:
            webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Arrêt du serveur")
            if watcher:
                watcher.stop()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
