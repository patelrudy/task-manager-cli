import datetime
from colorama import Fore, Style
from utils import load_tasks, save_tasks, load_config
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

def update_task(args):
    tasks = load_tasks()
    task_found = False
    for task in tasks:
        if task['id'] == args.id:
            task_found = True
            if args.name:
                task['name'] = args.name
            if args.due:
                try:
                    due_date = parse_due_date(args.due, load_config().get('date_input_mode', 'strict'))
                    task['due_date'] = due_date
                except ValueError as ve:
                    print(Fore.RED + str(ve) + Style.RESET_ALL)
                    return
            if args.desc:
                task['description'] = args.desc
            if args.tag:
                task['tag'] = args.tag
            if args.priority:
                task['priority'] = args.priority
            if args.status:
                if args.status.lower() in ['not started', 'in progress', 'review', 'completed']:
                    task['status'] = args.status.lower()
                else:
                    print(Fore.RED + "Invalid status. Choose from 'not started', 'in progress', 'review', 'completed'." + Style.RESET_ALL)
                    return
            save_tasks(tasks)
            print(Fore.GREEN + "Task updated successfully!" + Style.RESET_ALL)
            break
    if not task_found:
        print(Fore.RED + f"Task with ID {args.id} not found." + Style.RESET_ALL)
        print("Type 'help' for more information.")

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
        print("Type 'help' for more information.")

def apply_filters(tasks, filters):
    filtered_tasks = tasks
    config = load_config()
    date_input_mode = config.get('date_input_mode', 'strict')
    due_filter = filters.get('due')

    if due_filter:
        try:
            start_date, end_date = parse_filter_due_date(due_filter)
        except ValueError as ve:
            print(Fore.RED + str(ve) + Style.RESET_ALL)
            return []
        filtered_tasks = [
            t for t in filtered_tasks
            if start_date <= datetime.datetime.strptime(t['due_date'], '%Y-%m-%d').date() <= end_date
        ]

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
                due_date = infer_month_and_year(day, today)
            except ValueError:
                raise ValueError("Invalid day. Please enter a valid day (01-31).")
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

def parse_filter_due_date(due_str):
    today = datetime.date.today()
    due_str_lower = due_str.lower()

    if due_str_lower in ['today', 'tdy']:
        start_date = end_date = today
    elif due_str_lower in ['tomorrow', 'tmrw']:
        start_date = end_date = today + datetime.timedelta(days=1)
    elif due_str_lower in ['overmorrow', 'dat']:
        start_date = end_date = today + datetime.timedelta(days=2)
    elif due_str_lower in ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                           'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec']:
        month_str_to_int = {
            'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6,
            'jul':7, 'aug':8, 'sep':9, 'sept':9, 'oct':10, 'nov':11, 'dec':12
        }
        month = month_str_to_int[due_str_lower]
        year = today.year
        start_date = datetime.date(year, month, 1)
        if month == 12:
            end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    elif due_str.isdigit() and len(due_str) == 4:
        # Assume it's a year
        year = int(due_str)
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
    else:
        # Try parsing as date
        try:
            due_date = parse_due_date(due_str, load_config().get('date_input_mode', 'strict'))
            due_date_obj = datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
            start_date = end_date = due_date_obj
        except ValueError:
            raise ValueError("Invalid due date filter format.")

    return start_date, end_date

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
