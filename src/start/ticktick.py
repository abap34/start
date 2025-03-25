import os
from datetime import datetime
from typing import List, Optional, Callable, Any, TypeVar, cast
import requests
from pydantic import BaseModel


class Project(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    sortOrder: Optional[int] = None
    closed: Optional[bool] = None
    groupId: Optional[str] = None
    viewMode: Optional[str] = None
    permission: Optional[str] = None
    kind: Optional[str] = None

class Task(BaseModel):
    id: str
    projectId: str
    title: str
    isAllDay: Optional[bool] = None
    completedTime: Optional[datetime] = None
    content: Optional[str] = None
    desc: Optional[str] = None
    dueDate: Optional[datetime] = None
    reminders: Optional[List[str]] = None
    priority: Optional[int] = None
    repeatFlag: Optional[str] = None
    sortOrder: Optional[int] = None
    startDate: Optional[datetime] = None
    status: Optional[int] = None
    timeZone: Optional[str] = None

class ProjectData(BaseModel):
    project: Project
    tasks: List[Task] = []
    columns: Optional[List[dict]] = None

def _api_get(url: str, token: str) -> Optional[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            print(f"レスポンスのパースに失敗しました: {e}")
            return None
    else:
        print(f"API GET 失敗: {response.status_code} {response.text}")
        return None

# ----- ダミーデータ定義 -----

def get_dummy_all_projects(token: str) -> List[Project]:
    return [
        Project(id="dummy1", name="Dummy Project 1", color="#FF0000", sortOrder=1),
        Project(id="dummy2", name="Dummy Project 2", color="#00FF00", sortOrder=2),
    ]

def get_dummy_project_data(project_id: str, token: str) -> Optional[ProjectData]:
    dummy_tasks = [
        Task(
            id="task1",
            projectId=project_id,
            title="Dummy Task 1",
            status=0,
            content="Memo for Dummy Task 1",
            startDate=datetime.now(),
            dueDate=datetime.now(),
        ),
        Task(
            id="task2",
            projectId=project_id,
            title="Dummy Task 2",
            status=2,
            content="Memo for Dummy Task 2",
            startDate=datetime.now(),
            dueDate=datetime.now(),
        ),
    ]
    dummy_project = Project(
        id=project_id,
        name=f"Dummy Project {project_id}",
        color="#123456",
        sortOrder=1
    )
    return ProjectData(project=dummy_project, tasks=dummy_tasks, columns=[])

def use_dummy() -> bool:
    return os.getenv("DEV") is not None

F = TypeVar("F", bound=Callable[..., Any])

def mock(dummy_func: F) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        def wrapper(*args, **kwargs):
            if use_dummy():
                return dummy_func(*args, **kwargs)
            return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator

@mock(get_dummy_all_projects)
def get_all_projects(token: str) -> List[Project]:
    url = "https://api.ticktick.com/open/v1/project"
    data = _api_get(url, token)
    if data is None:
        return []
    try:
        return [Project.parse_obj(item) for item in data]
    except Exception as e:
        print("プロジェクトのパースに失敗しました:", e)
        return []

@mock(get_dummy_project_data)
def get_project_data(project_id: str, token: str) -> Optional[ProjectData]:
    url = f"https://api.ticktick.com/open/v1/project/{project_id}/data"
    data = _api_get(url, token)
    if data is None:
        return None
    try:
        return ProjectData.model_validate(data)
    except Exception as e:
        print(f"プロジェクトデータのパースに失敗しました (projectId={project_id}):", e)
        return None

def display_projects_and_tasks(token: str) -> None:
    projects = get_all_projects(token)
    if not projects:
        print("プロジェクトが存在しません。")
        return

    for project in projects:
        print(f"【プロジェクト】 {project.name} (ID: {project.id})")
        project_data = get_project_data(project.id, token)
        if project_data:
            if project_data.tasks:
                print("  └─ タスク一覧:")
                for task in project_data.tasks:
                    status_str = "Completed" if task.status == 2 else "Normal"
                    memo = task.content or ""
                    print(f"      ・ {task.title} (ID: {task.id}) - Status: {status_str}, Memo: {memo}")
            else:
                print("  └─ タスクはありません。")
        else:
            print("  └─ プロジェクトデータの取得に失敗しました。")
        print("-" * 40)
