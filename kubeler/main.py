import argparse
from .scripts.installer import Installer
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser(description="Installer script")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Subcommands')

    # Create a subparser for the 'install' command
    install_parser = subparsers.add_parser('install', help='Install command')
    install_parser.add_argument('--installer', type=str, default='./installer.yaml', help='Path to the config YAML file')
    install_parser.add_argument('--kube-config', type=str, default='~/kube/config', help='Path to the kube config file')

    args = parser.parse_args()

    # load .env
    load_dotenv()

    if args.command == 'install':
        installer = Installer(installer=args.installer, kube_config=args.kube_config)
        installer.install()

if __name__ == "__main__":
    main()
