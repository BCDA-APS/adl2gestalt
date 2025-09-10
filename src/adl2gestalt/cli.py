"""Command-line interface for adl2gestalt."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click

from . import __version__
from .converter import MedmToGestaltConverter
from .gestalt_runner import (
    create_gestalt_workflow,
    run_gestalt_file,
    test_gestalt_conversion,
    validate_gestalt_file,
)
from .scanner import (
    get_conversion_summary,
    list_gestalt_files,
    list_medm_files,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def main():
    """ADL to Gestalt converter tools."""
    pass


@click.command()
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    default=True,
    help="Search recursively (default: True)",
)
@click.option("--count", "-c", is_flag=True, help="Show only count of files")
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
@click.argument(
    "folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    default=True,
    help="Search recursively (default: True)",
)
@click.option("--count", "-c", is_flag=True, help="Show only count of files")
def list_gestalt_command(folder: Path, recursive: bool, count: bool):
    """List all YAML files in a folder."""
    try:
        files = list_gestalt_files(folder, recursive)

        if count:
            click.echo(f"Found {len(files)} YAML files")
        else:
            if not files:
                click.echo("No YAML files found")
            else:
                click.echo(f"YAML files in {folder}:")
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
@click.argument(
    "medm-folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.argument(
    "gestalt-folder", type=click.Path(file_okay=False, dir_okay=True, path_type=Path)
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed status")
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    default=True,
    help="Search recursively (default: True)",
)
def status_command(
    medm_folder: Path, gestalt_folder: Path, verbose: bool, recursive: bool
):
    """Show conversion status for MEDM files."""
    try:
        summary = get_conversion_summary(medm_folder, gestalt_folder, recursive)

        # Display summary
        click.echo("Conversion Status Summary")
        click.echo("=" * 40)
        click.echo(f"MEDM folder:     {medm_folder}")
        click.echo(f"Gestalt folder:  {gestalt_folder}")
        click.echo(f"Total MEDM files: {summary['total_medm']}")
        click.echo(f"  ✅ Converted and up to date:  {len(summary['up_to_date'])}")
        click.echo(f"  ⚠️  Converted but outdated:    {summary['total_outdated']}")
        click.echo(f"  🔄 Needs conversion: {summary['total_needs_conversion']}")

        if verbose:
            if summary["up_to_date"]:
                click.echo("\n✅ Converted and up to date files:")
                for file in summary["up_to_date"]:
                    try:
                        display_path = file.relative_to(medm_folder)
                    except ValueError:
                        display_path = file
                    click.echo(f"  {display_path}")

            if summary["outdated"]:
                click.echo(
                    "\n⚠️  Converted but outdated files (MEDM newer than Gestalt):"
                )
                for file in summary["outdated"]:
                    try:
                        display_path = file.relative_to(medm_folder)
                    except ValueError:
                        display_path = file
                    click.echo(f"  {display_path}")

            if summary["needs_conversion"]:
                click.echo("\n🔄 Needs conversion:")
                for file in summary["needs_conversion"]:
                    try:
                        display_path = file.relative_to(medm_folder)
                    except ValueError:
                        display_path = file
                    click.echo(f"  {display_path}")

        # Return non-zero if there are outdated or needs conversion files
        if summary["total_outdated"] > 0 or summary["total_needs_conversion"] > 0:
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file/directory"
)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
@click.option("--batch", "-b", is_flag=True, help="Convert entire directory")
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    default=True,
    help="Search recursively in batch mode (default: True)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def convert_command(
    input: Path,
    output: Optional[Path],
    force: bool,
    batch: bool,
    recursive: bool,
    verbose: bool,
):
    """Convert MEDM files to Gestalt format."""
    try:
        # Set logging level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        converter = MedmToGestaltConverter()
        converted_count = 0
        error_count = 0

        if input.is_file():
            # Single file conversion
            if not input.suffix == ".adl":
                click.echo("Error: Input file must have .adl extension", err=True)
                sys.exit(1)

            # Determine output path
            if output is None:
                output_path = input.with_suffix(".yml")
            else:
                output_path = output
                if output_path.is_dir():
                    output_path = output_path / input.with_suffix(".yml").name

            # Check if output exists and force flag
            if output_path.exists() and not force:
                click.echo(f"Error: Output file exists: {output_path}")
                click.echo("Use --force to overwrite")
                sys.exit(1)

            # Convert file
            if verbose:
                click.echo(f"Converting {input} -> {output_path}")

            try:
                result = converter.convert_file(input, output_path)
                click.echo(f"✅ Successfully converted: {result}")
                converted_count = 1
            except Exception as e:
                click.echo(f"❌ Failed to convert {input}: {e}", err=True)
                error_count = 1

        elif input.is_dir():
            # Directory batch conversion
            if not batch:
                click.echo(
                    "Error: Input is a directory. Use --batch flag for batch conversion",
                    err=True,
                )
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

            click.echo(f"Found {len(medm_files)} MEDM files to convert")

            # Convert each file

            # Temporarily suppress logging during progress bar
            original_level = logging.getLogger().level
            logging.getLogger().setLevel(logging.WARNING)

            with click.progressbar(
                medm_files,
                label="Converting files",
                show_pos=True,
                show_percent=True,
            ) as files:
                for medm_file in files:
                    try:
                        # Calculate output path maintaining directory structure
                        rel_path = medm_file.relative_to(input)
                        output_path = output_dir / rel_path.with_suffix(".yml")

                        # Check if output exists and force flag
                        if output_path.exists() and not force:
                            click.echo(f"\n⏭️  Skipping existing: {output_path}")
                            continue

                        # Convert file
                        converter.convert_file(medm_file, output_path)
                        converted_count += 1

                        click.echo(f"\n✅ Converted: {medm_file} -> {output_path}")

                    except Exception as e:
                        error_count += 1
                        click.echo(f"\n❌ Failed: {medm_file}: {e}", err=True)

            # Restore original logging level
            logging.getLogger().setLevel(original_level)

            # Summary
            click.echo("\nConversion Summary:")
            click.echo(f"✅ Successfully converted: {converted_count}")
            if error_count > 0:
                click.echo(f"  ❌ Failed: {error_count}")

        else:
            click.echo(
                f"Error: Input path is neither file nor directory: {input}", err=True
            )
            sys.exit(1)

        # Exit with error code if any conversions failed
        if error_count > 0:
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("gestalt-file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["qt", "bob", "dm"]),
    default="qt",
    help="Output format (default: qt)",
)
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file path"
)
def generate_command(
    gestalt_file: Path,
    format: str,
    output: Optional[Path],
):
    """Generate UI file from Gestalt YAML using gestalt engine."""
    try:
        success, message = run_gestalt_file(gestalt_file, format, output)

        if success:
            click.echo(f"✅ {message}")
        else:
            click.echo(f"❌ {message}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error generating from {gestalt_file}: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument("gestalt-file", type=click.Path(exists=True, path_type=Path))
@click.option("--verbose", "-v", is_flag=True, help="Show detailed test results")
def test_gestalt_command(gestalt_file: Path, verbose: bool):
    """Test Gestalt file conversion to all supported formats."""
    try:

        # Run tests
        results = test_gestalt_conversion(gestalt_file)

        # Display results
        click.echo(f"\nTesting {gestalt_file}")
        click.echo("=" * 50)

        # Validation results
        if results["validation"]["valid"]:
            click.echo("✅ Gestalt parsing validation: PASSED")
        else:
            click.echo(
                f"❌ Gestalt parsing validation: FAILED - {results['validation']['error']}"
            )

        # Conversion results
        click.echo("\nFormat conversion tests:")
        for fmt, result in results["conversions"].items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            click.echo(f"  {fmt:>3}: {status}")

            if verbose:
                click.echo(f"      Message: {result['message']}")
                if result["success"]:
                    click.echo(f"      Output size: {result['output_size']} bytes")

        # Overall result
        if results["overall_success"]:
            click.echo(
                "\n✅ Overall: VALID GESTALT FILE (at least one format conversion works)\n"
            )
        else:
            click.echo("\n❌ Overall: INVALID GESTALT FILE")
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error testing {gestalt_file}: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument(
    "medm-folder",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.argument(
    "output-folder", type=click.Path(file_okay=False, dir_okay=True, path_type=Path)
)
@click.option(
    "--test/--no-test",
    default=True,
    help="Test generated Gestalt files (default: True)",
)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing files")
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    default=True,
    help="Process recursively (default: True)",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def workflow_command(
    medm_folder: Path,
    output_folder: Path,
    test: bool,
    force: bool,
    recursive: bool,
    verbose: bool,
):
    """Batch workflow: convert all MEDM files in folder to Gestalt and test them."""
    try:
        # Set logging level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Create output folder
        output_folder.mkdir(parents=True, exist_ok=True)

        # Find all MEDM files
        medm_files = list_medm_files(medm_folder, recursive)

        if not medm_files:
            click.echo("No MEDM files found")
            return

        click.echo(f"Processing {len(medm_files)} MEDM files")

        success_count = 0
        error_count = 0

        # Temporarily suppress logging during progress bar
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.WARNING)

        # Process each file
        with click.progressbar(
            medm_files,
            label="Processing workflow",
            show_pos=True,
            show_percent=True,
        ) as files:
            for medm_file in files:
                try:
                    # Calculate output path
                    rel_path = medm_file.relative_to(medm_folder)
                    output_file_dir = output_folder / rel_path.parent

                    # Check if output exists and force flag
                    gestalt_file = output_file_dir / f"{medm_file.stem}.yml"
                    if gestalt_file.exists() and not force:
                        click.echo(f"\n⏭️  Skipping existing: {gestalt_file}")
                        continue

                    # Run complete workflow
                    workflow_result = create_gestalt_workflow(
                        medm_file, output_file_dir, test
                    )

                    if workflow_result["overall_success"]:
                        success_count += 1
                        click.echo(
                            f"\n✅ {medm_file} -> {workflow_result['conversion']['gestalt_file']}"
                        )
                    else:
                        error_count += 1
                        if workflow_result["conversion"]["success"]:
                            # Conversion succeeded but testing failed
                            error_msg = "Testing failed"
                            if workflow_result["validation"].get("error"):
                                error_msg = workflow_result["validation"]["error"]
                        else:
                            error_msg = workflow_result["conversion"]["message"]
                        click.echo(f"❌ {medm_file}: {error_msg}", err=True)

                except Exception as e:
                    error_count += 1
                    click.echo(f"❌ {medm_file}: {e}", err=True)

        # Restore original logging level
        logging.getLogger().setLevel(original_level)

        # Summary
        click.echo("\nWorkflow Summary:")
        click.echo(f"  ✅ Successfully processed: {success_count}")
        if error_count > 0:
            click.echo(f"  ❌ Failed: {error_count}")

        # Exit with error code if any workflows failed
        if error_count > 0:
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error in workflow: {e}", err=True)
        sys.exit(1)


# Add commands to main group
main.add_command(list_medm_command, name="list-medm")
main.add_command(list_gestalt_command, name="list-gestalt")
main.add_command(status_command, name="status")
main.add_command(convert_command, name="convert")
main.add_command(generate_command, name="generate")
main.add_command(test_gestalt_command, name="test-gestalt")
main.add_command(workflow_command, name="workflow")


if __name__ == "__main__":
    main()
