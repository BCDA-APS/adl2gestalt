"""Command-line interface for adl2gestalt."""

import click
import sys
from pathlib import Path
from typing import Optional
import logging

from . import __version__
from .scanner import (
    list_medm_files,
    list_gestalt_files,
    identify_pending_conversions,
    get_conversion_summary,
)
from .converter import MedmToGestaltConverter


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def main():
    """ADL to Gestalt converter tools."""
    pass


@click.command()
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('--recursive', '-r', is_flag=True, default=True, help='Search recursively (default: True)')
@click.option('--count', '-c', is_flag=True, help='Show only count of files')
def list_medm_command(folder: Path, recursive: bool, count: bool):
    """List all MEDM files in a folder."""
    try:
        files = list_medm_files(folder, recursive)
        
        if count:
            click.echo(f"Found {len(files)} MEDM files")
        else:
            if not files:
                click.echo("No MEDM files found")
            else:
                click.echo(f"MEDM files in {folder}:")
                for file in files:
                    # Show relative path if under folder, otherwise absolute
                    try:
                        display_path = file.relative_to(folder)
                    except ValueError:
                        display_path = file
                    click.echo(f"  {display_path}")
                click.echo(f"\nTotal: {len(files)} files")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('--recursive', '-r', is_flag=True, default=True, help='Search recursively (default: True)')
@click.option('--count', '-c', is_flag=True, help='Show only count of files')
def list_gestalt_command(folder: Path, recursive: bool, count: bool):
    """List all Gestalt files in a folder."""
    try:
        files = list_gestalt_files(folder, recursive)
        
        if count:
            click.echo(f"Found {len(files)} Gestalt files")
        else:
            if not files:
                click.echo("No Gestalt files found")
            else:
                click.echo(f"Gestalt files in {folder}:")
                for file in files:
                    try:
                        display_path = file.relative_to(folder)
                    except ValueError:
                        display_path = file
                    click.echo(f"  {display_path}")
                click.echo(f"\nTotal: {len(files)} files")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument('medm-folder', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.argument('gestalt-folder', type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
@click.option('--verbose', '-v', is_flag=True, help='Show detailed status')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Search recursively (default: True)')
def status_command(medm_folder: Path, gestalt_folder: Path, verbose: bool, recursive: bool):
    """Show conversion status for MEDM files."""
    try:
        # Ensure gestalt folder exists for checking
        gestalt_folder.mkdir(parents=True, exist_ok=True)
        
        summary = get_conversion_summary(medm_folder, gestalt_folder, recursive)
        
        # Display summary
        click.echo(f"Conversion Status Summary")
        click.echo(f"=" * 40)
        click.echo(f"MEDM folder:     {medm_folder}")
        click.echo(f"Gestalt folder:  {gestalt_folder}")
        click.echo(f"Total MEDM files: {summary['total_medm']}")
        click.echo(f"  ✅ Up to date:  {len(summary['up_to_date'])}")
        click.echo(f"  ⚠️  Outdated:    {summary['total_outdated']}")
        click.echo(f"  ❌ Pending:     {summary['total_pending']}")
        
        if verbose:
            if summary['up_to_date']:
                click.echo(f"\n✅ Up to date files:")
                for file in summary['up_to_date']:
                    try:
                        display_path = file.relative_to(medm_folder)
                    except ValueError:
                        display_path = file
                    click.echo(f"  {display_path}")
            
            if summary['outdated']:
                click.echo(f"\n⚠️  Outdated files (MEDM newer than Gestalt):")
                for file in summary['outdated']:
                    try:
                        display_path = file.relative_to(medm_folder)
                    except ValueError:
                        display_path = file
                    click.echo(f"  {display_path}")
            
            if summary['pending']:
                click.echo(f"\n❌ Pending conversion:")
                for file in summary['pending']:
                    try:
                        display_path = file.relative_to(medm_folder)
                    except ValueError:
                        display_path = file
                    click.echo(f"  {display_path}")
        
        # Return non-zero if there are pending or outdated files
        if summary['total_pending'] > 0 or summary['total_outdated'] > 0:
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument('input', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Output file/directory')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing files')
@click.option('--batch', '-b', is_flag=True, help='Convert entire directory')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Search recursively in batch mode (default: True)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-error output')
def convert_command(
    input: Path,
    output: Optional[Path],
    force: bool,
    batch: bool,
    recursive: bool,
    verbose: bool,
    quiet: bool
):
    """Convert MEDM files to Gestalt format."""
    try:
        # Set logging level
        if quiet:
            logging.getLogger().setLevel(logging.ERROR)
        elif verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        converter = MedmToGestaltConverter()
        converted_count = 0
        error_count = 0
        
        if input.is_file():
            # Single file conversion
            if not input.suffix == '.adl':
                click.echo(f"Error: Input file must have .adl extension", err=True)
                sys.exit(1)
            
            # Determine output path
            if output is None:
                output_path = input.with_suffix('.yml')
            else:
                output_path = output
                if output_path.is_dir():
                    output_path = output_path / input.with_suffix('.yml').name
            
            # Check if output exists and force flag
            if output_path.exists() and not force:
                click.echo(f"Error: Output file exists: {output_path}")
                click.echo("Use --force to overwrite")
                sys.exit(1)
            
            # Convert file
            if not quiet:
                click.echo(f"Converting {input} -> {output_path}")
            
            try:
                result = converter.convert_file(input, output_path)
                if not quiet:
                    click.echo(f"✅ Successfully converted: {result}")
                converted_count = 1
            except Exception as e:
                click.echo(f"❌ Failed to convert {input}: {e}", err=True)
                error_count = 1
        
        elif input.is_dir():
            # Directory batch conversion
            if not batch:
                click.echo("Error: Input is a directory. Use --batch flag for batch conversion", err=True)
                sys.exit(1)
            
            # Determine output directory
            if output is None:
                output_dir = input
            else:
                output_dir = output
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # Find all MEDM files
            medm_files = list_medm_files(input, recursive)
            
            if not medm_files:
                click.echo("No MEDM files found")
                return
            
            if not quiet:
                click.echo(f"Found {len(medm_files)} MEDM files to convert")
            
            # Convert each file
            with click.progressbar(medm_files, label='Converting files', 
                                 show_pos=True, show_percent=True,
                                 disabled=quiet) as files:
                for medm_file in files:
                    try:
                        # Calculate output path maintaining directory structure
                        rel_path = medm_file.relative_to(input)
                        output_path = output_dir / rel_path.with_suffix('.yml')
                        
                        # Check if output exists and force flag
                        if output_path.exists() and not force:
                            if verbose:
                                click.echo(f"⏭️  Skipping existing: {output_path}")
                            continue
                        
                        # Convert file
                        converter.convert_file(medm_file, output_path)
                        converted_count += 1
                        
                        if verbose:
                            click.echo(f"✅ Converted: {medm_file} -> {output_path}")
                    
                    except Exception as e:
                        error_count += 1
                        if not quiet:
                            click.echo(f"❌ Failed: {medm_file}: {e}", err=True)
            
            # Summary
            if not quiet:
                click.echo(f"\nConversion Summary:")
                click.echo(f"  ✅ Successfully converted: {converted_count}")
                if error_count > 0:
                    click.echo(f"  ❌ Failed: {error_count}")
        
        else:
            click.echo(f"Error: Input path is neither file nor directory: {input}", err=True)
            sys.exit(1)
        
        # Exit with error code if any conversions failed
        if error_count > 0:
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Add commands to main group
main.add_command(list_medm_command, name='list-medm')
main.add_command(list_gestalt_command, name='list-gestalt')
main.add_command(status_command, name='status')
main.add_command(convert_command, name='convert')


if __name__ == '__main__':
    main()