# utils.py

import os
import json
import platform
import datetime
from colorama import Fore, Style
from difflib import get_close_matches

# Define the config directory
CONFIG_DIR = 'config'
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

TASK_FILE = os.path.join(CONFIG_DIR, 'tasks.json')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    with open(TASK_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASK_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def load_config():
    default_config = {
        'auto_export': False,
        'export_path': os.getcwd(),
        'date_input_mode': 'strict'
    }
    if not os.path.exists(CONFIG_FILE):
        return default_config
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    # Ensure all default keys are present
    for key, value in default_config.items():
        config.setdefault(key, value)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def auto_export_check():
    config = load_config()
    if not config.get('auto_export', False):
        return
    last_export_date_str = config.get('last_export_date')
    if last_export_date_str:
        last_export_date = datetime.datetime.strptime(last_export_date_str, '%Y-%m-%d').date()
    else:
        last_export_date = None

    today = datetime.date.today()
    last_sunday = today - datetime.timedelta(days=today.weekday() + 1 % 7)
    weeks_to_export = []

    if last_export_date:
        delta_weeks = ((today - last_export_date).days) // 7
        for i in range(1, delta_weeks + 1):
            export_date = last_export_date + datetime.timedelta(weeks=i)
            weeks_to_export.append(export_date)
    else:
        # First time export
        export_date = last_sunday
        weeks_to_export.append(export_date)

    for export_date in weeks_to_export:
        export_tasks(export_date)
        # Update the last export date
        config['last_export_date'] = export_date.strftime('%Y-%m-%d')
        save_config(config)

def export_tasks(export_date=None):
    tasks = load_tasks()
    config = load_config()
    export_path = config.get('export_path', os.getcwd())
    if not export_date:
        export_date = datetime.date.today()
    filename = f"tasks_export_{export_date}.json"
    filepath = os.path.join(export_path, filename)
    # Ensure the export directory exists
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    with open(filepath, 'w') as f:
        json.dump(tasks, f, indent=4)
    # Remove completed tasks
    incomplete_tasks = [t for t in tasks if t['status'] != 'completed']
    save_tasks(incomplete_tasks)
    print(Fore.GREEN + f"Tasks exported to {filepath}" + Style.RESET_ALL)
    print(Fore.GREEN + "Completed tasks have been removed from the main task list." + Style.RESET_ALL)

def clear_screen(args=None):
    """Clears the terminal screen."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_help():
    help_text = """
Available commands:

- task add "name" --due DATE [--desc "description"] [--tag "tag"] [--priority "priority"]
    Add a new task.
    DATE can be in the following formats:
        - YYYYMMDD (e.g., 20231015)
        - MMDD (e.g., 1015) if 'date_input_mode' is set to 'smart'
        - DD (e.g., 15) if 'date_input_mode' is set to 'smart'
    Examples:
        task add "Write Report" --due 20231015 --desc "Write the annual report" --tag work --priority high
        task add "Team Meeting" --due 1016

- task list
    List all tasks.
    Example:
        task list

- task filter [--due DATE] [--priority PRIORITY] [--name_prefix PREFIX] [--tag TAG] [--desc_contains SUBSTRING]
    Filter tasks based on criteria.
    DATE can also be:
        - 'today' or 'tdy' for today's date
        - 'tomorrow' or 'tmrw' for tomorrow's date
        - 'overmorrow' or 'dat' for the day after tomorrow
        - Month abbreviations (e.g., 'jan', 'feb', 'mar', etc.) to filter tasks due in that month
        - 4-digit year (e.g., '2023') to filter tasks due in that year
    Examples:
        task filter --priority high
        task filter --due 20231015
        task filter --due today
        task filter --due feb

- task update --id ID --status STATUS
    Update the status of a task.
    Status options:
        - completed
        - started
        - in-progress
    Example:
        task update --id 1 --status completed

- task delete --id ID
    Delete a task.
    Example:
        task delete --id 2

- config [--auto_export True|False] [--export_path "/path/to/directory"] [--date_input_mode smart|strict]
    Configure settings.
    Examples:
        config --auto_export True
        config --export_path "~/exports"
        config --date_input_mode smart

- export
    Manually export tasks.
    Example:
        export

- clear
    Clear the terminal screen.

- help
    Show this help message.

- exit
    Exit the application.
"""
    print(help_text)

def print_suggestions(user_input):
    commands = ['task', 'config', 'export', 'clear', 'help', 'exit']
    task_commands = ['add', 'list', 'filter', 'update', 'delete']
    options = ['--due', '-d', '--priority', '-p', '--name_prefix', '-n', '--tag', '-t', '--desc_contains', '-s']
    input_command = user_input[0] if user_input else ''
    suggestions = get_close_matches(input_command, commands + task_commands + options, n=1, cutoff=0.6)
    if suggestions:
        print(Fore.YELLOW + f"Did you mean '{suggestions[0]}'?" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Unknown command or arguments." + Style.RESET_ALL)
    print_help()

def print_error(e):
    print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)
    print_help()