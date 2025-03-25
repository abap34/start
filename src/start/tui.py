from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import DataTable, Footer, Header, Static
from textual.screen import Screen
from textual import log
import random

def randstr(n):
    return ''.join(random.choices("abcdefghijklmnopqrstuvwxyz", k=n))

from .auth import get_access_token
from .ticktick import get_all_projects, get_project_data
from .ticktick import Task as TickTickTask


class TickTickApp(App):
    """The main TickTick TUI application."""
    
    CSS_PATH = "tui.css"
    BINDINGS = [("q", "quit", "Quit")]
    
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.target_tasks = []
        
    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        yield Horizontal(
            # 左側: タスク一覧
            DataTable(id="tasks-table"),
            # 右側: タスク詳細
            Static("タスクを選択すると詳細が表示されます", id="task-details"),
            id="main-content"
        )
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
            
            self.target_tasks = all_tasks
            
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
        for i, task in enumerate(self.target_tasks):
            status = "Completed" if task.status == 2 else "Pending"
            due_date = task.dueDate.strftime("%Y-%m-%d") if task.dueDate else "-"
            
            table.add_row(
                task.title,
                status,
                due_date,
                key=task.id  # task.id だけを使用して、ランダム文字列は追加しない
            )
        
        # Set cursor type to row for better selection
        table.cursor_type = "row"
    
    def update_task_details(self, task):
        """Update the task details panel with the selected task information."""
        details = self.query_one("#task-details", Static)
        details.update(
            f"Title: {task.title}\n\n"
            f"Status: {'Completed' if task.status == 2 else 'Pending'}\n\n"
            f"Content: {task.content or 'No content'}\n\n"
            f"Start Date: {task.startDate or 'Not set'}\n\n"
            f"Due Date: {task.dueDate or 'Not set'}\n\n"
        )
    
    def on_data_table_row_selected(self, event):
        """Handle row selection in the tasks table."""
        # Get the selected task ID from the row key
        task_id = event.row_key
        
        # Find the task in the tasks list
        selected_task = next((t for t in self.target_tasks if t.id == task_id), None)
        
        if selected_task:
            # Update the details panel
            self.update_task_details(selected_task)
            log.info(f"Selected task: {selected_task.title}")


def main():
    """Entry point for the application."""
    token = get_access_token()
    app = TickTickApp(token)
    app.title = "Start Over!"
    app.run()



if __name__ == "__main__":
    main()