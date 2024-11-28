# display.py

import datetime
from colorama import Fore, Style

def display_tasks(tasks):
    if not tasks:
        print(Fore.YELLOW + "No tasks found." + Style.RESET_ALL)
        return

    # Sort tasks by due date and then by priority
    priority_map = {'high': 1, 'normal': 2, 'low': 3}
    tasks.sort(key=lambda x: (
        datetime.datetime.strptime(x['due_date'], '%Y-%m-%d').date(),
        priority_map.get(x['priority'].lower(), 2)
    ))

    for task in tasks:
        due_date = datetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
        today = datetime.date.today()
        color = Fore.WHITE
        style = Style.NORMAL

        # Determine color based on status
        if task['status'] == 'completed':
            color = Fore.GREEN
        elif task['status'] in ['in progress', 'review']:
            color = Fore.YELLOW
        else:
            # Determine color based on due date
            if due_date < today:
                color = Fore.RED  # Past due
            elif due_date == today:
                color = Fore.RED  # Due today
            elif due_date == today + datetime.timedelta(days=1):
                color = Fore.LIGHTRED_EX  # Due tomorrow (Orange-like color)
            else:
                # If the color is not red or orange, check priority
                if task['priority'].lower() == 'high':
                    style = Style.BRIGHT
                    color = Fore.MAGENTA  # High priority tasks
                elif task['priority'].lower() == 'low':
                    style = Style.DIM

        # Orange takes precedence over yellow
        if color == Fore.LIGHTRED_EX and task['status'] in ['in progress', 'review']:
            color = Fore.LIGHTRED_EX

        print(
            color + style +
            f"ID: {task['id']}, Name: {task['name']}, Due: {task['due_date']}, "
            f"Priority: {task['priority']}, Status: {task['status']}"
            + Style.RESET_ALL
        )
        print(f"   Description: {task['description']}")
        print(f"   Tag: {task['tag']}")
        print('-' * 50)
