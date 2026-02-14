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
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description='Prévisualisation locale')
    parser.add_argument('--port', type=int, default=8000, help='Port du serveur (défaut: 8000)')
    parser.add_argument('-s', '--source', type=Path, default=Path('./cours'), help='Dossier source')
    args = parser.parse_args()
    
    # Build dans un dossier temporaire
    preview_dir = SCRIPT_DIR / '.preview'
    
    print("🔨 Build en mode preview...")
    result = subprocess.run([
        sys.executable, str(SCRIPT_DIR / 'build.py'),
        '-s', str(args.source),
        '-o', str(preview_dir),
        '--clean',
        '--preview'
    ])
    
    if result.returncode != 0:
        print("❌ Échec du build")
        return 1
    
    # Lancer le serveur
    import os
    os.chdir(preview_dir)
    
    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True 
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        url = f"http://localhost:{args.port}"
        print(f"\n🌐 Serveur démarré : {url}")
        print("   Ctrl+C pour arrêter\n")
        
        webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Arrêt du serveur")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
