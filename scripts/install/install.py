import argparse
import logging
import shutil
import venv
from pathlib import Path
from typing import Dict, Optional

log = logging.getLogger("install")
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter('[%(levelname)s]: %(message)s'))
log.addHandler(log_handler)
log.setLevel(logging.INFO)

parser = argparse.ArgumentParser()

parser.add_argument('command', type=str, help='install,activate')
parser.add_argument('--workdir', type=str, required=True)
parser.add_argument('--source_code_dir', type=str, required=False)
parser.add_argument('--version', type=str, required=True)


def prepare_workdir(dirpath: str) -> Path:
    install_dir: Path = Path(dirpath)
    if not install_dir.is_absolute():
        log.error(f'workdir should be absolute path {install_dir}')
        exit(1)

    if not install_dir.exists():
        log.info(f"creating installation directory: {install_dir}")
        install_dir.mkdir()
    else:
        log.info(f'installation directory found: {install_dir}')

    return install_dir


def switch_symlink(version_dir: Path, symlink: Path) -> bool:
    if not symlink.is_symlink() and symlink.exists():
        log.error(f'nonsymlink file with name of working symlink ({symlink}) already exists')
        exit(1)

    current = symlink.resolve().__str__()
    if current == str(version_dir):
        log.info(f'required version: {version_dir.name} already installed')
        return False

    log.info(f'redirecting symlink {symlink}: {current} --> {version_dir}')
    tmpsymlink = Path(str(symlink) + '_tmp')
    tmpsymlink.symlink_to(version_dir)
    tmpsymlink.rename(symlink)

    return True



def install_files(source_code_dir: Path, version_dir: Path):
    log.info(f'copying project files into {version_dir}')
    shutil.copytree(
        source_code_dir.__str__(),
        version_dir.__str__(),
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".*", 'Makefile', '__pycache__', 'scripts', 'data'),
    )

    # prepare virtualenv dir
    venv_dir = version_dir.joinpath(".venv")
    log.info(f'setup wirtual enviroment into {venv_dir}')
    venv.create(venv_dir, clear=True, with_pip=True)


def switch_symlink_and_exit(version_dir: Path, symlink: Path):
    restart_required = switch_symlink(version_dir, symlink)
    if restart_required:
        exit(0)

    exit(2)


def extract_params_from_args(args) -> Dict[str, Path]:
    source_code_dir: Path = Path(args.source_code_dir or '')
    install_dir = prepare_workdir(args.workdir)
    symlink = install_dir.joinpath("bot")

    version_dir = install_dir.joinpath(args.version)

    return {
        'source_code_dir': source_code_dir,
        'version_dir': version_dir,
        'symlink': symlink,
    }


def command_install(args) -> None:
    params = extract_params_from_args(args)
    version_dir: Optional[Path] = params.get('version_dir')
    assert version_dir is not None, "arguments parsed incorrectly; version_dir didn't built"

    if version_dir.exists():
        log.info(f"current version directory {version_dir} already exists")
    else:
        log.info(f'creatiog version directory {version_dir}')
        version_dir.mkdir()

    source_code_dir = params.get('source_code_dir')
    if source_code_dir is None:
        log.error('--source_code_dir param required for install')
        exit(1)

    install_files(source_code_dir, version_dir)

    log.info(f'all required files installed successfully')

def command_enable(args) -> None:
    params = extract_params_from_args(args)
    symlink = params.get('symlink')
    version_dir = params.get('version_dir')
    assert symlink is not None and version_dir is not None, 'arguments parsed incorrectly; one of (or both) symlink {symlink} version_dir {version_dir} is None'
    switch_symlink(version_dir, symlink)

def main():
    args = parser.parse_args()

    if args.command == 'install':
        command_install(args)
    elif args.command == 'enable':
        command_enable(args)
    else:
        log.error(f'unknown command {args.command}')


main()
