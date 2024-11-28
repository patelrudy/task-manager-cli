import datetime
from colorama import Fore, Style

def display_tasks(tasks):
    if not tasks:
        print(Fore.YELLOW + "No tasks found." + Style.RESET_ALL)
        return

    # Sort tasks by due date
    tasks.sort(key=lambda x: x['due_date'])

    for task in tasks:
        due_date = datetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
        today = datetime.date.today()
        color = Fore.WHITE
        style = Style.NORMAL

        # Determine color based on due date
        if due_date < today:
            color = Fore.RED  # Past due
        elif due_date == today:
            color = Fore.RED  # Due today
        elif due_date == today + datetime.timedelta(days=1):
            color = Fore.YELLOW  # Due tomorrow

        # If the color is not red or yellow, check priority
        if color == Fore.WHITE:
            if task['priority'].lower() == 'high':
                style = Style.BRIGHT
                color = Fore.MAGENTA  # High priority tasks
            elif task['priority'].lower() == 'low':
                style = Style.DIM

        print(
            color + style +
            f"ID: {task['id']}, Name: {task['name']}, Due: {task['due_date']}, "
            f"Priority: {task['priority']}, Status: {task['status']}"
            + Style.RESET_ALL
        )
        print(f"   Description: {task['description']}")
        print(f"   Tag: {task['tag']}")
        print('-' * 50)
