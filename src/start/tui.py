import random

from textual import log
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label, Pretty, Rule, Static

from .auth import get_access_token
from .ticktick import Task as TickTickTask
from .ticktick import get_all_projects, get_project_data, get_task


class TaskDetailView(Container):
    """A container to display task details in a structured way."""

    def __init__(self, id=None):
        super().__init__(id=id)
        self.target_tasks: list[TickTickTask] = []

    def compose(self) -> ComposeResult:
        """Compose the container with initial content."""
        yield Label("Task Detail", id="task-detail-title")
        yield Rule()
        yield Label("Title:", id="task-title")
        yield Label("Status:", id="task-status")
        yield Label("Dates:", id="task-dates")
        yield Static("Content:", id="task-content")

    def update_task(self, task: TickTickTask) -> None:
        """Update all child widgets with task information."""
        self.target_tasks = task

        # Update title
        self.query_one("#task-title", Label).update("[b]" + task.title + "[/b]")

        # Update status with appropriate class
        status_text = "✅ Completed" if task.status == 2 else "📝 Pending"
        status_classes = ["completed"] if task.status == 2 else ["pending"]
        self.query_one("#task-status", Label).update(f"Status: {status_text}")
        self.query_one("#task-status", Label).set_classes(status_classes)

        # Update dates
        start_date = (
            task.startDate.strftime("%Y-%m-%d %H:%M") if task.startDate else "Not set"
        )
        due_date = (
            task.dueDate.strftime("%Y-%m-%d %H:%M") if task.dueDate else "Not set"
        )
        self.query_one("#task-dates", Label).update(
            f"Start: {start_date}\nDue: {due_date}"
        )

        # Update content
        content = task.content or "No content available"
        self.query_one("#task-content", Static).update(content)


class TickTickApp(App):
    """The main TickTick TUI application."""

    CSS_PATH = "tui.css"
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.target_tasks: list[TickTickTask] = []

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        yield Horizontal(
            # 左側: タスク一覧
            DataTable(id="tasks-table"),
            # 右側: タスク詳細
            TaskDetailView(id="task-detail-container"),
            id="main-content",
        )
        yield Footer()

    def on_mount(self):
        """Load the data when the app starts."""
        self.load_tasks()

    def load_tasks(self):
        """Load all tasks from all projects."""
        try:
            # Get all projects
            projects = get_all_projects(token)

            # Get all tasks from all projects
            all_tasks = []
            for project in projects:
                project_data = get_project_data(project.id, token)
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

            table.add_row(task.title, status, due_date, key=task.id)

        # Set cursor type to row for better selection
        table.cursor_type = "row"

    def on_data_table_row_selected(self, event):
        """Handle row selection in the tasks table."""
        # Get the selected task ID from the row key
        task_id = event.row_key

        # Find the task in the tasks list
        selected_task = next((t for t in self.target_tasks if t.id == task_id), None)

        if selected_task:
            # Update the details view
            detail_view = self.query_one("#task-detail-container", TaskDetailView)
            detail_view.update_task(selected_task)
            log.info(f"Selected task: {selected_task.title}")

    def on_data_table_cursor_changed(self, event):
        """Handle cursor movement in the tasks table."""
        # Get the table
        table = self.query_one("#tasks-table", DataTable)

        # Get row key at current cursor position
        if table.cursor_row is not None:
            task_id = table.get_row_key(table.cursor_row)

            # Find the task in the tasks list
            selected_task = next(
                (t for t in self.target_tasks if t.id == task_id), None
            )

            if selected_task:
                # Update the details view
                detail_view = self.query_one("#task-detail-container", TaskDetailView)
                detail_view.update_task(selected_task)
                log.info(f"Cursor moved to task: {selected_task.title}")


token = get_access_token()

def main():
    """Entry point for the application."""
    app = TickTickApp()
    app.title = "Start Over!"
    app.run()


if __name__ == "__main__":
    main()
