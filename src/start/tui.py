from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Static
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive

from .ticktick import get_all_projects, Project
from .auth import get_access_token


class ProjectListView(ListView):
    """A ListView to display projects."""

    class ProjectSelected(Message):
        """Message sent when a project is selected."""
        def __init__(self, project: Project) -> None:
            self.project = project
            super().__init__()

    def __init__(self, projects: list[Project], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.projects = projects
        self.update_projects()

    def update_projects(self) -> None:
        """Populate the ListView with projects."""
        self.clear()
        for project in self.projects:
            self.append(ListItem(Static(project.name), id=project.id))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection of a project."""
        project_id = event.item.id
        selected_project = next((p for p in self.projects if p.id == project_id), None)
        if selected_project:
            self.post_message(self.ProjectSelected(selected_project))


class TickTickTUI(App):
    """Main TUI application for TickTick."""

    CSS_PATH = "tui.css"  # Optional: Add a CSS file for styling
    BINDINGS = [("q", "quit", "Quit")]

    token = reactive("")

    def __init__(self, token: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.token = token
        self.projects = []

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()
        yield Container(
            ProjectListView(self.projects, id="project-list"),
            id="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load data and initialize the UI."""
        self.load_projects()

    def load_projects(self) -> None:
        """Fetch projects from the API."""
        try:
            self.projects = get_all_projects(self.token)
            project_list = self.query_one(ProjectListView)
            project_list.projects = self.projects
            project_list.update_projects()
        except Exception as e:
            self.log(f"Failed to load projects: {e}")

    def on_project_list_view_project_selected(self, message: ProjectListView.ProjectSelected) -> None:
        """Handle project selection."""
        self.log(f"Selected project: {message.project.name}")


def main():
    """Main entry point for the TUI."""
    token = get_access_token()  # Authenticate and get the access token
    app = TickTickTUI(token)
    app.run()


if __name__ == "__main__":
    main()