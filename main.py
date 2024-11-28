import sys
import shlex
from argparse import ArgumentParser
from colorama import init, Fore, Style
from task_manager import (
    add_task, list_tasks, update_task, delete_task, filter_tasks
)
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
                    print(Fore.RED + "Invalid command." + Style.RESET_ALL)
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
                                print(Fore.RED + "Invalid command." + Style.RESET_ALL)
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
    task_subparsers = parser_task.add_subparsers(dest='task_command')

    # Add command
    parser_add = task_subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('name', help='Task name')
    parser_add.add_argument('--due', '-d', required=True, help='Due date')
    parser_add.add_argument('--desc', '-s', help='Task description')
    parser_add.add_argument('--tag', '-t', help='Task tag')
    parser_add.add_argument('--priority', '-p', help='Task priority')
    parser_add.set_defaults(func=add_task)

    # List command
    parser_list = task_subparsers.add_parser('list', help='List all tasks')
    parser_list.set_defaults(func=list_tasks)

    # Filter command
    parser_filter = task_subparsers.add_parser('filter', help='Filter tasks')
    parser_filter.add_argument('--due', '-d', help='Filter by due date')
    parser_filter.add_argument('--priority', '-p', help='Filter by priority')
    parser_filter.add_argument('--name_prefix', '-n', help='Filter by name prefix')
    parser_filter.add_argument('--tag', '-t', help='Filter by tag')
    parser_filter.add_argument('--desc_contains', '-s', help='Filter by description substring')
    parser_filter.set_defaults(func=filter_tasks)

    # Update command
    parser_update = task_subparsers.add_parser('update', help='Update a task')
    parser_update.add_argument('--id', type=int, required=True, help='Task ID')
    parser_update.add_argument('--name', help='New task name')
    parser_update.add_argument('--due', '-d', help='New due date')
    parser_update.add_argument('--desc', help='New task description')  # No short flag
    parser_update.add_argument('--tag', '-t', help='New task tag')
    parser_update.add_argument('--priority', '-p', help='New task priority')
    parser_update.add_argument('--status', '-s', choices=['not started', 'in progress', 'review', 'completed'], help='New status')
    parser_update.set_defaults(func=update_task)

    # Delete command
    parser_delete = task_subparsers.add_parser('delete', help='Delete a task')
    parser_delete.add_argument('--id', type=int, required=True, help='Task ID')
    parser_delete.set_defaults(func=delete_task)

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

    # Help Command
    parser_help = subparsers.add_parser('help', help='Show help message')
    parser_help.set_defaults(func=lambda args: print_help())

    try:
        args = parser.parse_args(arguments)
    except SystemExit:
        print(Fore.RED + "Invalid command or arguments." + Style.RESET_ALL)
        print("Type 'help' for more information.")
        return None

    return args

if __name__ == '__main__':
    main()
