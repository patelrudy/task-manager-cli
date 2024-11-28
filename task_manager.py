import datetime
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

def list_tasks(args=None):
    tasks = load_tasks()
    display_tasks(tasks)

def filter_tasks(args):
    tasks = load_tasks()
    filters = {
        'due': args.due,
        'priority': args.priority,
        'name_prefix': args.name_prefix,
        'tag': args.tag,
        'desc_contains': args.desc_contains
    }
    tasks = apply_filters(tasks, filters)
    display_tasks(tasks)

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
    config = load_config()
    date_input_mode = config.get('date_input_mode', 'strict')
    due_filter = filters.get('due')

    if due_filter:
        try:
            due_date = parse_due_date(due_filter, date_input_mode)
        except ValueError as ve:
            print(Fore.RED + str(ve) + Style.RESET_ALL)
            return []
        filtered_tasks = [t for t in filtered_tasks if t['due_date'] == due_date]

    if filters.get('priority'):
        filtered_tasks = [t for t in filtered_tasks if t['priority'].lower() == filters['priority'].lower()]

    if filters.get('name_prefix'):
        filtered_tasks = [t for t in filtered_tasks if t['name'].startswith(filters['name_prefix'])]

    if filters.get('tag'):
        filtered_tasks = [t for t in filtered_tasks if t['tag'].lower() == filters['tag'].lower()]

    if filters.get('desc_contains'):
        filtered_tasks = [t for t in filtered_tasks if filters['desc_contains'].lower() in t['description'].lower()]

    return filtered_tasks

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
