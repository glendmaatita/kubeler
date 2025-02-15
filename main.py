import argparse
from scripts.installer import Installer

# available command: kubeler --installer=./installer.yaml --kube-config=~/kube/config
def main():
    parser = argparse.ArgumentParser(description="Installer script")
    parser.add_argument('--installer', type=str, default='./installer.yaml', help='Path to the config YAML file')
    parser.add_argument('--kube-config', type=str, default='~/kube/config', help='Path to the config YAML file')

    args = parser.parse_args()
    installer = Installer(installer=args.installer, kube_config=args.kube_config)
    installer.install()

if __name__ == "__main__":
    main()
