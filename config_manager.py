# config_manager.py

import os
from colorama import Fore, Style
from utils import load_config, save_config, print_help

def configure(args):
    config = load_config()
    updated = False

    if args.auto_export is not None:
        config['auto_export'] = args.auto_export
        updated = True
        print(Fore.GREEN + f"Auto export set to {args.auto_export}." + Style.RESET_ALL)

    if args.export_path:
        export_path = os.path.expanduser(args.export_path)
        if not os.path.exists(export_path):
            create_dir = input(f"Directory '{export_path}' does not exist. Create it? (y/n): ").strip().lower()
            if create_dir == 'y':
                os.makedirs(export_path)
                print(Fore.GREEN + f"Directory '{export_path}' created." + Style.RESET_ALL)
            else:
                print(Fore.RED + "Export path not set. Directory does not exist." + Style.RESET_ALL)
                print_help()
                return
        config['export_path'] = export_path
        updated = True
        print(Fore.GREEN + f"Export path set to '{export_path}'." + Style.RESET_ALL)

    if args.date_input_mode:
        if args.date_input_mode.lower() in ['smart', 'strict']:
            config['date_input_mode'] = args.date_input_mode.lower()
            updated = True
            print(Fore.GREEN + f"Date input mode set to '{config['date_input_mode']}'." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Invalid date input mode. Choose 'smart' or 'strict'." + Style.RESET_ALL)
            print_help()
            return

    if updated:
        save_config(config)
        print(Fore.GREEN + "Configuration updated!" + Style.RESET_ALL)
    else:
        # Display current configuration
        print("Current configuration:")
        print(f"  Auto export: {config.get('auto_export', False)}")
        print(f"  Export path: {config.get('export_path', os.getcwd())}")
        print(f"  Date input mode: {config.get('date_input_mode', 'strict')}")
