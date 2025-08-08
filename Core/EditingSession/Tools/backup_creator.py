#!/usr/bin/env python3
"""
⛧ Backup Creator ⛧
Alma's Mystical File Guardian

Créateur de sauvegardes horodatées avec compression et métadonnées.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import argparse
import shutil
import sys
import json
import gzip
from datetime import datetime
from pathlib import Path


def safe_read_file_content(file_path):
    """Lecture sécurisée d'un fichier."""
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"Fichier inexistant: {file_path}"}
        
        if not os.path.isfile(file_path):
            return {"success": False, "error": f"Le chemin n'est pas un fichier: {file_path}"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {"success": True, "content": content}
    
    except PermissionError:
        return {"success": False, "error": f"Permission refusée: {file_path}"}
    except UnicodeDecodeError:
        return {"success": False, "error": f"Erreur d'encodage: {file_path}"}
    except Exception as e:
        return {"success": False, "error": f"Erreur lecture: {e}"}


def generate_backup_name(original_path, timestamp=None, suffix="backup", extension=None):
    """Génère un nom de backup horodaté."""
    if timestamp is None:
        timestamp = datetime.now()
    
    path_obj = Path(original_path)
    name_without_ext = path_obj.stem
    original_ext = path_obj.suffix
    
    # Format timestamp : YYYY-MM-DD_HH-MM-SS
    time_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Extension finale
    if extension:
        final_ext = extension if extension.startswith('.') else f'.{extension}'
    else:
        final_ext = original_ext
    
    backup_name = f"{name_without_ext}_{suffix}_{time_str}{final_ext}"
    return backup_name


def create_backup_metadata(original_path, backup_path, compressed=False, notes=""):
    """Crée les métadonnées du backup."""
    original_stat = os.stat(original_path)
    backup_stat = os.stat(backup_path)
    
    metadata = {
        "backup_info": {
            "created_at": datetime.now().isoformat(),
            "created_by": "Alma Backup Creator",
            "version": "1.0"
        },
        "original_file": {
            "path": str(Path(original_path).absolute()),
            "name": os.path.basename(original_path),
            "size_bytes": original_stat.st_size,
            "modified_time": datetime.fromtimestamp(original_stat.st_mtime).isoformat(),
            "checksum": None  # TODO: Ajouter MD5/SHA256 si nécessaire
        },
        "backup_file": {
            "path": str(Path(backup_path).absolute()),
            "name": os.path.basename(backup_path),
            "size_bytes": backup_stat.st_size,
            "compressed": compressed,
            "compression_ratio": round(backup_stat.st_size / original_stat.st_size, 3) if compressed else 1.0
        },
        "notes": notes
    }
    
    return metadata


def create_file_backup(file_path, backup_dir=None, compress=False, keep_structure=False, 
                      notes="", metadata=True, overwrite=False):
    """
    Crée une sauvegarde d'un fichier.
    
    Args:
        file_path: Chemin vers le fichier à sauvegarder
        backup_dir: Répertoire de destination (défaut: même répertoire)
        compress: Compresser avec gzip
        keep_structure: Conserver la structure de répertoires
        notes: Notes à ajouter aux métadonnées
        metadata: Créer un fichier de métadonnées JSON
        overwrite: Écraser si le backup existe déjà
    
    Returns:
        Dict avec résultats de la sauvegarde
    """
    
    # Vérification du fichier source
    if not os.path.exists(file_path):
        return {"success": False, "error": f"Fichier source inexistant: {file_path}"}
    
    if not os.path.isfile(file_path):
        return {"success": False, "error": f"Le chemin n'est pas un fichier: {file_path}"}
    
    # Détermination du répertoire de backup
    if backup_dir is None:
        backup_dir = os.path.dirname(file_path) or "."
    
    # Création du répertoire de backup si nécessaire
    os.makedirs(backup_dir, exist_ok=True)
    
    # Génération du nom de backup
    timestamp = datetime.now()
    backup_extension = ".gz" if compress else None
    backup_name = generate_backup_name(file_path, timestamp, extension=backup_extension)
    
    # Chemin complet du backup
    if keep_structure:
        # Conserver la structure relative
        rel_path = os.path.relpath(file_path)
        backup_path = os.path.join(backup_dir, rel_path + f"_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}")
        if compress:
            backup_path += ".gz"
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    else:
        backup_path = os.path.join(backup_dir, backup_name)
    
    # Vérification de l'écrasement
    if os.path.exists(backup_path) and not overwrite:
        return {"success": False, "error": f"Le backup existe déjà: {backup_path}"}
    
    try:
        # Création du backup
        if compress:
            # Backup compressé
            with open(file_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            # Backup simple
            shutil.copy2(file_path, backup_path)
        
        # Création des métadonnées
        metadata_path = None
        metadata_content = None
        if metadata:
            metadata_content = create_backup_metadata(file_path, backup_path, compress, notes)
            metadata_path = backup_path + ".meta.json"
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_content, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "original_file": file_path,
            "backup_file": backup_path,
            "metadata_file": metadata_path,
            "compressed": compress,
            "size_original": os.path.getsize(file_path),
            "size_backup": os.path.getsize(backup_path),
            "compression_ratio": round(os.path.getsize(backup_path) / os.path.getsize(file_path), 3) if compress else 1.0,
            "timestamp": timestamp.isoformat(),
            "metadata": metadata_content
        }
    
    except PermissionError as e:
        return {"success": False, "error": f"Permission refusée: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Erreur lors de la création du backup: {e}"}


def restore_backup(backup_path, restore_path=None, verify_metadata=True):
    """
    Restaure un fichier depuis un backup.
    
    Args:
        backup_path: Chemin vers le fichier de backup
        restore_path: Chemin de restauration (défaut: chemin original)
        verify_metadata: Vérifier les métadonnées si disponibles
    
    Returns:
        Dict avec résultats de la restauration
    """
    
    if not os.path.exists(backup_path):
        return {"success": False, "error": f"Backup inexistant: {backup_path}"}
    
    # Lecture des métadonnées si disponibles
    metadata_path = backup_path + ".meta.json"
    metadata = None
    if verify_metadata and os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception as e:
            return {"success": False, "error": f"Erreur lecture métadonnées: {e}"}
    
    # Détermination du chemin de restauration
    if restore_path is None:
        if metadata and "original_file" in metadata:
            restore_path = metadata["original_file"]["path"]
        else:
            # Tentative de déduction depuis le nom du backup
            backup_name = os.path.basename(backup_path)
            # Suppression du timestamp et suffixe
            original_name = backup_name.split('_backup_')[0]
            if backup_path.endswith('.gz'):
                original_name += os.path.splitext(backup_path)[0].split('.')[-1]
            restore_path = os.path.join(os.path.dirname(backup_path), original_name)
    
    try:
        # Restauration
        if backup_path.endswith('.gz'):
            # Backup compressé
            with gzip.open(backup_path, 'rb') as f_in:
                with open(restore_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            # Backup simple
            shutil.copy2(backup_path, restore_path)
        
        return {
            "success": True,
            "backup_file": backup_path,
            "restored_file": restore_path,
            "metadata_used": metadata is not None,
            "metadata": metadata
        }
    
    except Exception as e:
        return {"success": False, "error": f"Erreur lors de la restauration: {e}"}


def list_backups(directory=".", pattern="*_backup_*"):
    """Liste les backups dans un répertoire."""
    from glob import glob
    
    backup_files = glob(os.path.join(directory, pattern))
    backups = []
    
    for backup_file in backup_files:
        metadata_file = backup_file + ".meta.json"
        metadata = None
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except:
                pass
        
        backup_info = {
            "backup_file": backup_file,
            "metadata_file": metadata_file if os.path.exists(metadata_file) else None,
            "size": os.path.getsize(backup_file),
            "created": datetime.fromtimestamp(os.path.getctime(backup_file)).isoformat(),
            "metadata": metadata
        }
        
        backups.append(backup_info)
    
    # Tri par date de création (plus récent en premier)
    backups.sort(key=lambda x: x["created"], reverse=True)
    
    return backups


def format_backup_results(results):
    """Formate les résultats de backup pour affichage."""
    if not results["success"]:
        return f"❌ Erreur: {results['error']}"
    
    output = []
    output.append(f"✅ Backup créé avec succès !")
    output.append(f"📁 Original: {results['original_file']}")
    output.append(f"💾 Backup: {results['backup_file']}")
    
    if results.get('metadata_file'):
        output.append(f"📋 Métadonnées: {results['metadata_file']}")
    
    output.append(f"📊 Taille: {results['size_original']} → {results['size_backup']} bytes")
    
    if results['compressed']:
        ratio = results['compression_ratio']
        savings = round((1 - ratio) * 100, 1)
        output.append(f"🗜️ Compression: {ratio:.3f} ({savings}% d'économie)")
    
    output.append(f"🕐 Horodatage: {results['timestamp']}")
    
    return "\n".join(output)


def main():
    """Interface en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="⛧ Créateur de sauvegardes - Outil d'Alma ⛧"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande create
    create_parser = subparsers.add_parser('create', help='Créer un backup')
    create_parser.add_argument('file', help='Fichier à sauvegarder')
    create_parser.add_argument('-d', '--backup-dir', help='Répertoire de destination')
    create_parser.add_argument('-c', '--compress', action='store_true', help='Compresser avec gzip')
    create_parser.add_argument('-s', '--keep-structure', action='store_true', help='Conserver la structure')
    create_parser.add_argument('-n', '--notes', default='', help='Notes pour les métadonnées')
    create_parser.add_argument('--no-metadata', action='store_true', help='Ne pas créer de métadonnées')
    create_parser.add_argument('--overwrite', action='store_true', help='Écraser si existe')
    
    # Commande restore
    restore_parser = subparsers.add_parser('restore', help='Restaurer un backup')
    restore_parser.add_argument('backup', help='Fichier de backup')
    restore_parser.add_argument('-t', '--target', help='Chemin de restauration')
    restore_parser.add_argument('--no-verify', action='store_true', help='Ne pas vérifier les métadonnées')
    
    # Commande list
    list_parser = subparsers.add_parser('list', help='Lister les backups')
    list_parser.add_argument('-d', '--directory', default='.', help='Répertoire à scanner')
    list_parser.add_argument('-p', '--pattern', default='*_backup_*', help='Pattern de recherche')
    
    parser.add_argument('--debug', action='store_true', help='Mode debug')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.debug:
        print(f"⛧ Backup Creator - Commande: {args.command}")
        print()
    
    if args.command == 'create':
        results = create_file_backup(
            file_path=args.file,
            backup_dir=args.backup_dir,
            compress=args.compress,
            keep_structure=args.keep_structure,
            notes=args.notes,
            metadata=not args.no_metadata,
            overwrite=args.overwrite
        )
        
        formatted_output = format_backup_results(results)
        print(formatted_output)
        
        sys.exit(0 if results["success"] else 1)
    
    elif args.command == 'restore':
        results = restore_backup(
            backup_path=args.backup,
            restore_path=args.target,
            verify_metadata=not args.no_verify
        )
        
        if results["success"]:
            print(f"✅ Restauration réussie !")
            print(f"💾 Backup: {results['backup_file']}")
            print(f"📁 Restauré: {results['restored_file']}")
            if results["metadata_used"]:
                print(f"📋 Métadonnées utilisées: ✅")
        else:
            print(f"❌ Erreur: {results['error']}")
        
        sys.exit(0 if results["success"] else 1)
    
    elif args.command == 'list':
        backups = list_backups(args.directory, args.pattern)
        
        if not backups:
            print(f"📂 Aucun backup trouvé dans {args.directory}")
        else:
            print(f"📂 Backups trouvés dans {args.directory}:")
            print("⛧" + "═" * 60)
            
            for backup in backups:
                print(f"💾 {os.path.basename(backup['backup_file'])}")
                print(f"   📊 Taille: {backup['size']} bytes")
                print(f"   🕐 Créé: {backup['created']}")
                if backup['metadata']:
                    orig = backup['metadata'].get('original_file', {})
                    print(f"   📁 Original: {orig.get('name', 'N/A')}")
                print()
        
        sys.exit(0)


if __name__ == "__main__":
    main()
