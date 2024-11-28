# task_manager.py

import datetime
from argparse import ArgumentParser
from colorama import Fore, Style
from utils import load_tasks, save_tasks, print_help, load_config
from display import display_tasks

def add_task(args):
    tasks = load_tasks()
    config = load_config()
    date_input_mode = config.get('date_input_mode', 'strict')

    try:
        due_date = parse_due_date(args.due, date_input_mode)
    except ValueError as ve:
        print(Fore.RED + str(ve) + Style.RESET_ALL)
        return

    # Add the task
    task = {
        'id': (tasks[-1]['id'] + 1) if tasks else 1,
        'name': args.name,
        'due_date': due_date,
        'description': args.desc if args.desc else '',
        'tag': args.tag if args.tag else '',
        'priority': args.priority if args.priority else 'normal',
        'status': 'not started'
    }
    tasks.append(task)
    save_tasks(tasks)
    print(Fore.GREEN + "Task added successfully!" + Style.RESET_ALL)

def parse_due_date(due_str, date_input_mode):
    today = datetime.date.today()

    if date_input_mode == 'smart':
        if len(due_str) == 8:
            # Full date: YYYYMMDD
            try:
                due_date = datetime.datetime.strptime(due_str, '%Y%m%d').date()
            except ValueError:
                raise ValueError("Invalid date format. Please use YYYYMMDD.")
        elif len(due_str) == 4:
            # Month and day: MMDD
            try:
                month_day = datetime.datetime.strptime(due_str, '%m%d').date()
            except ValueError:
                raise ValueError("Invalid date format. Please use MMDD for month and day.")
            due_date = infer_year(month_day, today)
        elif len(due_str) == 2:
            # Day only: DD
            try:
                day = int(due_str)
                if not 1 <= day <= 31:
                    raise ValueError
            except ValueError:
                raise ValueError("Invalid day. Please enter a valid day (01-31).")
            due_date = infer_month_and_year(day, today)
        else:
            raise ValueError("Invalid date format. Please use DD, MMDD, or YYYYMMDD.")
    else:
        # Strict mode: only accept YYYYMMDD
        if len(due_str) != 8:
            raise ValueError("Invalid date format. Please use YYYYMMDD.")
        try:
            due_date = datetime.datetime.strptime(due_str, '%Y%m%d').date()
        except ValueError:
            raise ValueError("Invalid date. Please enter a valid date in YYYYMMDD format.")

    return due_date.strftime('%Y-%m-%d')

def infer_year(month_day, today):
    month = month_day.month
    day = month_day.day
    year = today.year

    try:
        due_date = datetime.date(year, month, day)
    except ValueError:
        raise ValueError("Invalid date.")

    if due_date < today:
        # If the date has already passed this year, assume next year
        due_date = datetime.date(year + 1, month, day)

    return due_date

def infer_month_and_year(day, today):
    month = today.month
    year = today.year

    # Try current month
    try:
        due_date = datetime.date(year, month, day)
    except ValueError:
        # Invalid day for current month, try next month
        month += 1
        if month > 12:
            month = 1
            year += 1
        try:
            due_date = datetime.date(year, month, day)
        except ValueError:
            raise ValueError("Invalid day for any month.")

    if due_date < today:
        # If the date has already passed this month, move to next month
        month += 1
        if month > 12:
            month = 1
            year += 1
        try:
            due_date = datetime.date(year, month, day)
        except ValueError:
            raise ValueError("Invalid day for any month.")

    return due_date

def list_tasks(args):
    tasks = load_tasks()
    if args.list or args.filter:
        filters = args.filter if args.filter else []
        tasks = apply_filters(tasks, filters)
        display_tasks(tasks)
    else:
        print("Please specify '--list' or '--filter' to display tasks.")
        print_help()
        return

def update_status(args):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == args.id:
            task['status'] = args.status
            save_tasks(tasks)
            print(Fore.GREEN + "Task status updated!" + Style.RESET_ALL)
            return
    print(Fore.RED + "Task not found." + Style.RESET_ALL)
    print_help()

def delete_task(args):
    tasks = load_tasks()
    task_found = False
    for task in tasks:
        if task['id'] == args.id:
            tasks.remove(task)
            task_found = True
            save_tasks(tasks)
            print(Fore.GREEN + f"Task ID {args.id} deleted successfully!" + Style.RESET_ALL)
            break
    if not task_found:
        print(Fore.RED + f"Task with ID {args.id} not found." + Style.RESET_ALL)
        print_help()

def apply_filters(tasks, filters):
    filtered_tasks = tasks
    for i in range(0, len(filters), 2):
        if i + 1 >= len(filters):
            print(Fore.RED + "Invalid filter arguments." + Style.RESET_ALL)
            print_help()
            return []
        key = filters[i].lower()
        value = filters[i + 1]
        if key == 'due_date':
            filtered_tasks = [t for t in filtered_tasks if t['due_date'] == value]
        elif key == 'priority':
            filtered_tasks = [t for t in filtered_tasks if t['priority'].lower() == value.lower()]
        elif key == 'name_prefix':
            filtered_tasks = [t for t in filtered_tasks if t['name'].startswith(value)]
        elif key == 'tag':
            filtered_tasks = [t for t in filtered_tasks if t['tag'].lower() == value.lower()]
        elif key == 'desc_contains':
            filtered_tasks = [t for t in filtered_tasks if value.lower() in t['description'].lower()]
        else:
            print(Fore.RED + f"Unknown filter key: {key}" + Style.RESET_ALL)
            print_help()
            return []
    return filtered_tasks

def parse_task_arguments(parser_task):
    parser_task.add_argument('--list', '-l', action='store_true', help='List all tasks')
    parser_task.add_argument('--filter', '-f', nargs='*', help='Filter criteria')
    parser_task.add_argument('--add', '-a', action='store_true', help='Add a new task')
    parser_task.add_argument('--update', '-u', action='store_true', help='Update a task')
    parser_task.add_argument('--delete', '-d', action='store_true', help='Delete a task')
    parser_task.set_defaults(func=determine_task_action)

    # Add task arguments
    parser_task.add_argument('name', nargs='?', help='Task name')
    parser_task.add_argument('--due', required=False, help='Due date')
    parser_task.add_argument('--desc', help='Task description')
    parser_task.add_argument('--tag', help='Task tag')
    parser_task.add_argument('--priority', help='Task priority')

    # Update and Delete task arguments
    parser_task.add_argument('--id', type=int, help='Task ID')
    parser_task.add_argument('--status', choices=['completed', 'started', 'in-progress'], help='New status')

def determine_task_action(args):
    if args.add:
        if args.name and args.due:
            add_task(args)
        else:
            print(Fore.RED + "Task name and --due date are required for adding a task." + Style.RESET_ALL)
            print_help()
    elif args.update:
        if args.id and args.status:
            update_status(args)
        else:
            print(Fore.RED + "--id and --status are required for updating a task." + Style.RESET_ALL)
            print_help()
    elif args.delete:
        if args.id:
            delete_task(args)
        else:
            print(Fore.RED + "--id is required for deleting a task." + Style.RESET_ALL)
            print_help()
    elif args.list or args.filter:
        list_tasks(args)
    else:
        print("Please specify an action: --add, --update, --delete, --list, or --filter.")
        print_help()
