from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import DataTable, Footer, Header, Static
from textual.screen import Screen, ModalScreen
from textual import log
import random

def randstr(n):
    return ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=n))

from .auth import get_access_token
from .ticktick import get_all_projects, get_project_data
from .ticktick import Task as TickTickTas

class TaskDetailScreen(ModalScreen):
    """Modal screen to display task details."""

    def __init__(self, task):
        super().__init__()
        self.target_task = task

    def compose(self) -> ComposeResult:
        """Create the content for the modal."""
        yield Container(
            Static(
                f"Title: {self.target_task.title}\n\n"
                f"Status: {'Completed' if self.target_task.status == 2 else 'Pending'}\n\n"
                f"Content: {self.target_task.content or 'No content'}\n\n"
                f"Start Date: {self.target_task.startDate or 'Not set'}\n\n"
                f"Due Date: {self.target_task.dueDate or 'Not set'}\n\n",
                id="task-details"
            ),
            id="modal-container"
        )

    def on_key(self, event):
        """Close the modal on Escape key."""
        if event.key == "escape":
            self.app.pop_screen()


class TickTickApp(App):
    """The main TickTick TUI application."""
    
    CSS_PATH = "tui.css"
    BINDINGS = [("space", "show_task_details", "Show Details"), ("q", "quit", "Quit")]
    
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.tasks: list[TickTickTask] = []
        
    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        yield DataTable(id="tasks-table")
        yield Footer()
        
    def on_mount(self):
        """Load the data when the app starts."""
        self.load_tasks()
        
    def load_tasks(self):
        """Load all tasks from all projects."""
        try:
            # Get all projects
            projects = get_all_projects(self.token)
            
            # Get all tasks from all projects
            all_tasks = []
            for project in projects:
                project_data = get_project_data(project.id, self.token)
                if project_data and project_data.tasks:
                    all_tasks.extend(project_data.tasks)
            
            self.tasks = all_tasks
            
            # Update the table
            self.update_tasks_table()
        except Exception as e:
            self.notify(f"Error loading tasks: {e}", severity="error")
    
    def update_tasks_table(self):
        """Update the tasks table with data."""
        table = self.query_one("#tasks-table", DataTable)
        
        # Clear and set up columns
        table.clear(columns=True)
        table.add_columns("Title", "Status", "Due Date")
        
        # Add rows for each task
        for task in self.tasks:
            status = "Completed" if task.status == 2 else "Pending"
            due_date = task.dueDate.strftime("%Y-%m-%d") if task.dueDate else "-"
            
            table.add_row(
                task.title,
                status,
                due_date,
                key=task.id + randstr(5)  
            )
        
        # Set cursor type to row for better selection
        table.cursor_type = "row"
    
    def show_task_details(self, task):
        """Show details for the selected task."""
        self.push_screen(TaskDetailScreen(task))
    
    def action_show_task_details(self):
        """Action to show details for the currently selected task (bound to space key)."""
        table = self.query_one("#tasks-table", DataTable)
        if table.cursor_row is not None:
            # 修正: get_row_at が返すのは list なので、row_key を正しく取得する
            task_id = self.tasks[table.cursor_row].id

            log.info(f"Showing details for task: {task_id}")
            
            # Find the task
            selected_task = next((t for t in self.tasks if t.id == task_id), None)
            
            if selected_task:
                # Show task details
                self.show_task_details(selected_task)


def main():
    """Entry point for the application."""
    token = get_access_token()
    app = TickTickApp(token)
    app.run()


if __name__ == "__main__":
    main()