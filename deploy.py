#!/usr/bin/env python3
"""
Déploiement des cours via SSH/SFTP

Usage:
    python deploy.py                     # Déploie avec la config par défaut
    python deploy.py --host monserveur   # Spécifie l'hôte
    python deploy.py --dry-run           # Simule sans transférer
    python deploy.py --config deploy.toml # Utilise un fichier de config

Configuration (deploy.toml):
    [server]
    host = "monserveur.com"
    user = "monuser"
    port = 22
    remote_path = "/home/monuser/public_html/cours"
    
    [build]
    source = "./cours"
    output = "./dist"
    title = "Formations Médicales"
"""

import sys
import os
import argparse
import tomllib
import subprocess
import shutil
from pathlib import Path
from datetime import datetime


# Répertoire du script (pour trouver build.py)
SCRIPT_DIR = Path(__file__).resolve().parent

# Répertoire de travail (pour deploy.toml et chemins relatifs du build)
WORK_DIR = Path.cwd()


DEFAULT_CONFIG = {
    'server': {
        'host': '',
        'user': '',
        'port': 22,
        'remote_path': '/public_html/cours',
    },
    'build': {
        'source': './cours',
        'output': './dist',
        'title': 'Formations Médicales',
    }
}


def resolve_build_path(path: str) -> Path:
    """Résout un chemin relatif par rapport au répertoire de travail"""
    p = Path(path)
    if p.is_absolute():
        return p
    return (WORK_DIR / p).resolve()


def load_config(config_file: Path) -> dict:
    """Charge la configuration depuis un fichier TOML (relatif au cwd)"""
    config = DEFAULT_CONFIG.copy()
    config['server'] = DEFAULT_CONFIG['server'].copy()
    config['build'] = DEFAULT_CONFIG['build'].copy()
    
    # Config relative au répertoire de travail
    if not config_file.is_absolute():
        config_file = WORK_DIR / config_file
    
    if config_file.exists():
        print(f"📄 Config: {config_file}")
        with open(config_file, 'rb') as f:
            file_config = tomllib.load(f)
        
        for section in ('server', 'build'):
            if section in file_config:
                config[section] = {**config[section], **file_config[section]}
    else:
        print(f"⚠️  Config non trouvée: {config_file}")
    
    return config


def run_command(cmd: list, dry_run: bool = False, description: str = '') -> bool:
    """Exécute une commande shell"""
    if description:
        print(f"  {description}")
    
    if dry_run:
        print(f"    [DRY-RUN] {' '.join(str(c) for c in cmd)}")
        return True
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ❌ Erreur: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"    ❌ Exception: {e}")
        return False


def build_courses(config: dict, clean: bool = True) -> bool:
    """Lance le build des cours"""
    print("🔨 Build des cours...")
    
    build_script = SCRIPT_DIR / 'build.py'
    
    if not build_script.exists():
        print(f"❌ Script build.py non trouvé: {build_script}")
        return False
    
    source_path = resolve_build_path(config['build']['source'])
    output_path = resolve_build_path(config['build']['output'])
    
    cmd = [
        sys.executable, str(build_script),
        '-s', str(source_path),
        '-o', str(output_path),
        '--title', config['build']['title'],
    ]
    
    if clean:
        cmd.append('--clean')
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def deploy_rsync(config: dict, dry_run: bool = False) -> bool:
    """Déploie via rsync (recommandé)"""
    server = config['server']
    build = config['build']
    
    if not server['host'] or not server['user']:
        print("❌ Configuration serveur incomplète (host, user requis)")
        return False
    
    source = resolve_build_path(build['output'])
    if not source.exists():
        print(f"❌ Dossier source inexistant: {source}")
        return False
    
    dest = f"{server['user']}@{server['host']}:{server['remote_path']}"
    
    rsync_opts = [
        '-avz',
        '--delete',
        '--progress',
        '--chmod=D755,F644',  # Dossiers: rwxr-xr-x, Fichiers: rw-r--r--
        '-e', f"ssh -p {server['port']}",
    ]
    
    cmd = ['rsync'] + rsync_opts + [f"{source}/", dest]
    
    print(f"📤 Déploiement vers {dest}")
    
    if dry_run:
        cmd.insert(1, '--dry-run')
        print(f"  [DRY-RUN] {' '.join(str(c) for c in cmd)}")
    
    try:
        result = subprocess.run(cmd)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ rsync non trouvé. Installer rsync ou utiliser --method=scp")
        return False

def deploy_scp(config: dict, dry_run: bool = False) -> bool:
    """Déploie via scp (fallback)"""
    server = config['server']
    build = config['build']
    
    if not server['host'] or not server['user']:
        print("❌ Configuration serveur incomplète (host, user requis)")
        return False
    
    source = resolve_build_path(build['output'])
    if not source.exists():
        print(f"❌ Dossier source inexistant: {source}")
        return False
    
    dest = f"{server['user']}@{server['host']}:{server['remote_path']}"
    
    print(f"📤 Déploiement vers {dest}")
    
    ssh_cmd = [
        'ssh', '-p', str(server['port']),
        f"{server['user']}@{server['host']}",
        f"mkdir -p {server['remote_path']}"
    ]
    
    if not run_command(ssh_cmd, dry_run, "Création du dossier distant..."):
        return False
    
    scp_cmd = [
        'scp', '-r', '-P', str(server['port']),
        f"{source}/.",
        dest
    ]
    
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(str(c) for c in scp_cmd)}")
        return True
    
    try:
        result = subprocess.run(scp_cmd)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ scp non trouvé")
        return False


def deploy_sftp(config: dict, dry_run: bool = False) -> bool:
    """Déploie via sftp avec un batch file"""
    server = config['server']
    build = config['build']
    
    if not server['host'] or not server['user']:
        print("❌ Configuration serveur incomplète (host, user requis)")
        return False
    
    source = resolve_build_path(build['output'])
    if not source.exists():
        print(f"❌ Dossier source inexistant: {source}")
        return False
    
    print(f"📤 Déploiement SFTP vers {server['host']}:{server['remote_path']}")
    
    batch_commands = [f"-mkdir {server['remote_path']}"]
    
    for item in source.rglob('*'):
        rel_path = item.relative_to(source)
        remote_target = f"{server['remote_path']}/{rel_path}"
        
        if item.is_dir():
            batch_commands.append(f"-mkdir {remote_target}")
        else:
            batch_commands.append(f"put {item} {remote_target}")
    
    if dry_run:
        print("  [DRY-RUN] Commandes SFTP:")
        for cmd in batch_commands[:10]:
            print(f"    {cmd}")
        if len(batch_commands) > 10:
            print(f"    ... et {len(batch_commands) - 10} autres commandes")
        return True
    
    batch_file = Path('/tmp/sftp_batch.txt')
    batch_file.write_text('\n'.join(batch_commands))
    
    sftp_cmd = [
        'sftp', '-P', str(server['port']),
        '-b', str(batch_file),
        f"{server['user']}@{server['host']}"
    ]
    
    try:
        result = subprocess.run(sftp_cmd)
        batch_file.unlink()
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ sftp non trouvé")
        return False


def create_default_config(config_file: Path):
    """Crée un fichier de configuration par défaut dans le répertoire courant"""
    if not config_file.is_absolute():
        config_file = WORK_DIR / config_file
    
    content = '''# Configuration de déploiement
# Adapter les valeurs à votre serveur

[server]
host = "monserveur.com"
user = "monuser"
port = 22
remote_path = "/home/monuser/public_html/cours"

[build]
source = "./cours"
output = "./dist"
title = "Formations Médicales"
'''
    config_file.write_text(content)
    print(f"✅ Fichier de configuration créé: {config_file}")
    print("   Éditer ce fichier avec vos paramètres serveur")


def main():
    parser = argparse.ArgumentParser(
        description='Déploie les cours compilés via SSH',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Méthodes de déploiement:
  rsync   Synchronisation incrémentale (recommandé, plus rapide)
  scp     Copie simple via SSH
  sftp    Transfert SFTP

Exemples:
  python deploy.py                          # Build + déploiement
  python deploy.py --dry-run                # Simulation
  python deploy.py --skip-build             # Déploie sans rebuild
  python deploy.py --host srv --user me     # Override config
  python deploy.py --init                   # Crée deploy.toml dans le dossier courant
        '''
    )
    
    parser.add_argument('--config', type=Path, default=Path('deploy.toml'),
                        help='Fichier de configuration (défaut: ./deploy.toml)')
    parser.add_argument('--init', action='store_true',
                        help='Créer un fichier de configuration par défaut')
    parser.add_argument('--host', type=str,
                        help='Hôte SSH (override config)')
    parser.add_argument('--user', type=str,
                        help='Utilisateur SSH (override config)')
    parser.add_argument('--port', type=int,
                        help='Port SSH (override config)')
    parser.add_argument('--remote-path', type=str,
                        help='Chemin distant (override config)')
    parser.add_argument('--method', choices=['rsync', 'scp', 'sftp'], default='rsync',
                        help='Méthode de transfert (défaut: rsync)')
    parser.add_argument('--skip-build', action='store_true',
                        help='Ne pas rebuild avant déploiement')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulation sans transfert réel')
    parser.add_argument('--no-clean', action='store_true',
                        help='Ne pas nettoyer avant le build')
    
    args = parser.parse_args()
    
    print(f"📂 Projet: {SCRIPT_DIR}")
    print(f"📂 Travail: {WORK_DIR}")
    
    if args.init:
        create_default_config(args.config)
        return 0
    
    config = load_config(args.config)
    
    if args.host:
        config['server']['host'] = args.host
    if args.user:
        config['server']['user'] = args.user
    if args.port:
        config['server']['port'] = args.port
    if args.remote_path:
        config['server']['remote_path'] = args.remote_path
    
    if not config['server']['host'] or not config['server']['user']:
        print("❌ Configuration serveur manquante")
        print(f"   Créer deploy.toml avec: python {SCRIPT_DIR}/deploy.py --init")
        print("   Ou spécifier --host et --user")
        return 1
    
    print(f"🚀 Déploiement vers {config['server']['user']}@{config['server']['host']}")
    print(f"   Remote: {config['server']['remote_path']}")
    print(f"   Source: {resolve_build_path(config['build']['source'])}")
    print(f"   Output: {resolve_build_path(config['build']['output'])}")
    print(f"   Méthode: {args.method}")
    if args.dry_run:
        print("   ⚠️  Mode simulation (dry-run)")
    print()
    
    if not args.skip_build:
        if not build_courses(config, clean=not args.no_clean):
            print("❌ Échec du build")
            return 1
        print()
    
    deploy_methods = {
        'rsync': deploy_rsync,
        'scp': deploy_scp,
        'sftp': deploy_sftp,
    }
    
    success = deploy_methods[args.method](config, dry_run=args.dry_run)
    
    if success:
        print()
        print("✅ Déploiement terminé !")
        return 0
    else:
        print()
        print("❌ Échec du déploiement")
        return 1


if __name__ == '__main__':
    sys.exit(main())
