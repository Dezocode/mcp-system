#!/usr/bin/env python3
"""
MCP Tools Path Migration Utility
Migrates existing MCP servers to the standardized mcp-tools location
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

import click


class MCPPathMigrator:
    """Handles migration of MCP servers to standardized paths"""
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.mcp_tools_path = self.repo_root / "mcp-tools"
        self.mcp_tools_path.mkdir(exist_ok=True)
        
        self.config_files = [
            self.repo_root / "configs" / ".mcp-servers.json",
            self.repo_root / ".mcp-server-config.json",
            self.repo_root / ".mcp-sync-config.json"
        ]
    
    def find_legacy_servers(self) -> Dict[str, str]:
        """Find servers with legacy paths that need migration"""
        legacy_servers = {}
        
        for config_file in self.config_files:
            if not config_file.exists():
                continue
                
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                for server_name, server_config in config.items():
                    if isinstance(server_config, dict) and 'path' in server_config:
                        path = server_config['path']
                        
                        # Check if path needs migration
                        if self._needs_migration(path):
                            legacy_servers[server_name] = path
                            
            except Exception as e:
                click.echo(f"Warning: Could not read {config_file}: {e}", err=True)
                
        return legacy_servers
    
    def _needs_migration(self, path: str) -> bool:
        """Check if a path needs migration to mcp-tools standard"""
        # Already in mcp-tools
        if path.startswith("mcp-tools/"):
            return False
            
        # Home directory paths
        if path.startswith("~/mcp-"):
            return True
            
        # Relative paths not in mcp-tools
        if not path.startswith("/") and not path.startswith("mcp-tools/"):
            server_path = Path(path)
            if server_path.exists() and server_path.is_dir():
                return True
                
        return False
    
    def migrate_server(self, server_name: str, old_path: str, dry_run: bool = False) -> bool:
        """Migrate a single server to mcp-tools location"""
        # Determine new path
        if old_path.startswith("~/mcp-"):
            # Extract server name from home path
            new_name = old_path[6:]  # Remove "~/mcp-"
        else:
            new_name = Path(old_path).name
            
        new_path = self.mcp_tools_path / new_name
        old_full_path = Path(old_path).expanduser().resolve()
        
        if dry_run:
            click.echo(f"Would migrate {server_name}:")
            click.echo(f"  From: {old_full_path}")
            click.echo(f"  To: {new_path}")
            return True
        
        # Check if source exists
        if not old_full_path.exists():
            click.echo(f"Warning: Source path does not exist: {old_full_path}", err=True)
            return False
            
        # Check if destination already exists
        if new_path.exists():
            click.echo(f"Warning: Destination already exists: {new_path}", err=True)
            return False
        
        try:
            # Copy the server directory
            shutil.copytree(old_full_path, new_path)
            click.echo(f"✅ Copied {server_name} to {new_path}")
            
            # Update configuration files
            self._update_config_files(server_name, old_path, f"mcp-tools/{new_name}")
            
            # Optionally remove old directory (with confirmation)
            if click.confirm(f"Remove old directory {old_full_path}?"):
                shutil.rmtree(old_full_path)
                click.echo(f"🗑️  Removed old directory: {old_full_path}")
            
            return True
            
        except Exception as e:
            click.echo(f"Error migrating {server_name}: {e}", err=True)
            return False
    
    def _update_config_files(self, server_name: str, old_path: str, new_path: str):
        """Update configuration files with new path"""
        for config_file in self.config_files:
            if not config_file.exists():
                continue
                
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                updated = False
                for name, server_config in config.items():
                    if (isinstance(server_config, dict) and 
                        'path' in server_config and 
                        server_config['path'] == old_path):
                        server_config['path'] = new_path
                        updated = True
                        
                if updated:
                    with open(config_file, 'w') as f:
                        json.dump(config, f, indent=2)
                    click.echo(f"📝 Updated {config_file}")
                    
            except Exception as e:
                click.echo(f"Warning: Could not update {config_file}: {e}", err=True)
    
    def validate_migration(self) -> bool:
        """Validate that all servers are properly migrated"""
        legacy_servers = self.find_legacy_servers()
        
        if not legacy_servers:
            click.echo("✅ All servers are using standardized paths")
            return True
        else:
            click.echo(f"⚠️  Found {len(legacy_servers)} servers with legacy paths:")
            for name, path in legacy_servers.items():
                click.echo(f"  - {name}: {path}")
            return False


@click.command()
@click.option('--server', help='Migrate specific server by name')
@click.option('--all', 'migrate_all', is_flag=True, help='Migrate all legacy servers')
@click.option('--dry-run', is_flag=True, help='Show what would be migrated without doing it')
@click.option('--validate', is_flag=True, help='Check migration status')
@click.option('--repo-root', type=click.Path(exists=True), help='Repository root path')
def main(server: Optional[str], migrate_all: bool, dry_run: bool, validate: bool, repo_root: Optional[str]):
    """Migrate MCP servers to standardized mcp-tools location"""
    
    root_path = Path(repo_root) if repo_root else Path.cwd()
    migrator = MCPPathMigrator(root_path)
    
    if validate:
        migrator.validate_migration()
        return
    
    # Find legacy servers
    legacy_servers = migrator.find_legacy_servers()
    
    if not legacy_servers:
        click.echo("✅ No legacy servers found - all servers are using standardized paths")
        return
    
    if server:
        # Migrate specific server
        if server not in legacy_servers:
            click.echo(f"Server '{server}' not found or already migrated", err=True)
            sys.exit(1)
            
        old_path = legacy_servers[server]
        success = migrator.migrate_server(server, old_path, dry_run)
        
        if success and not dry_run:
            click.echo(f"✅ Successfully migrated {server}")
        elif not success:
            sys.exit(1)
            
    elif migrate_all:
        # Migrate all legacy servers
        if dry_run:
            click.echo(f"Dry run - would migrate {len(legacy_servers)} servers:")
            
        success_count = 0
        for name, path in legacy_servers.items():
            if migrator.migrate_server(name, path, dry_run):
                success_count += 1
                
        if not dry_run:
            click.echo(f"✅ Successfully migrated {success_count}/{len(legacy_servers)} servers")
        else:
            click.echo(f"Dry run complete - {success_count} servers ready for migration")
            
    else:
        # Show available servers for migration
        click.echo(f"Found {len(legacy_servers)} servers with legacy paths:")
        for name, path in legacy_servers.items():
            click.echo(f"  - {name}: {path}")
            
        click.echo("\nUse --all to migrate all, or --server <name> to migrate specific server")
        click.echo("Use --dry-run to preview changes without applying them")


if __name__ == "__main__":
    main()