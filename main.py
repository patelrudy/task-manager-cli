# main.py

import sys
import shlex
from argparse import ArgumentParser
from colorama import init, Fore, Style
from task_manager import parse_task_arguments
from config_manager import configure
from utils import (
    auto_export_check, export_tasks, print_help, print_suggestions, clear_screen, print_error
)

# Initialize colorama
init()

def main():
    while True:
        try:
            if len(sys.argv) > 1:
                args = parse_arguments(sys.argv[1:])
                if args is None:
                    # Parsing failed; exit
                    break
                if 'func' in args:
                    auto_export_check()
                    args.func(args)
                else:
                    print("Invalid command.")
                    print_suggestions(sys.argv[1:])
                break  # Exit after processing command-line arguments
            else:
                # Interactive mode
                print(
                    Fore.CYAN +
                    "Entering interactive mode. Type 'help' for commands, 'clear' to clear the screen, or 'exit' to quit."
                    + Style.RESET_ALL
                )
                while True:
                    try:
                        user_input = input(">> ").strip()
                        if user_input.lower() in ['exit', 'quit']:
                            print("Exiting...")
                            break
                        elif user_input.lower() == 'help':
                            print_help()
                        elif user_input.lower() == 'clear':
                            clear_screen()
                        elif user_input:
                            args = parse_arguments(shlex.split(user_input))
                            if args is None:
                                continue  # Parsing failed; prompt user again
                            if 'func' in args:
                                auto_export_check()
                                args.func(args)
                            else:
                                print("Invalid command.")
                                print_suggestions(shlex.split(user_input))
                        else:
                            continue
                    except Exception as e:
                        print_error(e)
        except Exception as e:
            print_error(e)
            break  # Exit if an exception occurs during command-line processing

def parse_arguments(arguments):
    parser = ArgumentParser(description='Task Manager CLI', add_help=False)
    subparsers = parser.add_subparsers(dest='command')

    # Task command
    parser_task = subparsers.add_parser('task', help='Task operations')
    parse_task_arguments(parser_task)

    # Configure
    parser_config = subparsers.add_parser('config', help='Configure settings')
    parser_config.add_argument(
        '--auto_export', type=bool, nargs='?', const=True,
        help='Enable or disable auto export'
    )
    parser_config.add_argument(
        '--export_path', type=str, help='Set the export directory path'
    )
    parser_config.add_argument(
        '--date_input_mode', type=str, choices=['smart', 'strict'], help='Set date input mode'
    )
    parser_config.set_defaults(func=configure)

    # Manual Export
    parser_export = subparsers.add_parser('export', help='Manually export tasks')
    parser_export.set_defaults(func=lambda args: export_tasks())

    # Clear Command
    parser_clear = subparsers.add_parser('clear', help='Clear the terminal screen')
    parser_clear.set_defaults(func=clear_screen)

    try:
        args = parser.parse_args(arguments)
    except SystemExit:
        print(Fore.RED + "Invalid command or arguments." + Style.RESET_ALL)
        print_suggestions(arguments)
        return None

    return args

if __name__ == '__main__':
    main()
