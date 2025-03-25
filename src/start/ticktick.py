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

class TaskCreate(BaseModel):
    title: str
    projectId: str
    content: Optional[str] = None
    desc: Optional[str] = None
    isAllDay: Optional[bool] = None
    startDate: Optional[datetime] = None
    dueDate: Optional[datetime] = None
    timeZone: Optional[str] = None
    reminders: Optional[List[str]] = None
    repeatFlag: Optional[str] = None
    priority: Optional[int] = None
    sortOrder: Optional[int] = None

class TaskUpdate(BaseModel):
    id: str
    projectId: str
    title: Optional[str] = None
    content: Optional[str] = None
    desc: Optional[str] = None
    isAllDay: Optional[bool] = None
    startDate: Optional[datetime] = None
    dueDate: Optional[datetime] = None
    timeZone: Optional[str] = None
    reminders: Optional[List[str]] = None
    repeatFlag: Optional[str] = None
    priority: Optional[int] = None
    sortOrder: Optional[int] = None

class ProjectCreate(BaseModel):
    name: str
    color: Optional[str] = None
    sortOrder: Optional[int] = 0
    viewMode: Optional[str] = None
    kind: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    sortOrder: Optional[int] = None
    viewMode: Optional[str] = None
    kind: Optional[str] = None

def _api_get(url: str, token: str) -> Optional[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            print(f"Failed to parse response: {e}")
            return None
    else:
        print(f"API GET failed: {response.status_code} {response.text}")
        return None

def _api_post(url: str, token: str, json_data: dict) -> Optional[dict]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=json_data)
    if response.status_code in (200, 201):
        try:
            return response.json()
        except Exception as e:
            print(f"Failed to parse POST response: {e}")
            return None
    else:
        print(f"API POST failed: {response.status_code} {response.text}")
        return None

def _api_delete(url: str, token: str) -> bool:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    if response.status_code in (200, 204):
        return True
    else:
        print(f"API DELETE failed: {response.status_code} {response.text}")
        return False

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
        print(f"Failed to parse projects: {e}")
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
        print(f"Failed to parse project data (projectId={project_id}): {e}")
        return None

def get_task(project_id: str, task_id: str, token: str) -> Optional[Task]:
    url = f"https://api.ticktick.com/open/v1/project/{project_id}/task/{task_id}"
    data = _api_get(url, token)
    if data is None:
        return None
    try:
        return Task.parse_obj(data)
    except Exception as e:
        print(f"Failed to parse task: {e}")
        return None

def create_task(task: TaskCreate, token: str) -> Optional[Task]:
    url = "https://api.ticktick.com/open/v1/task"
    data = _api_post(url, token, task.dict(exclude_unset=True))
    if data is None:
        return None
    try:
        return Task.parse_obj(data)
    except Exception as e:
        print(f"Failed to parse created task: {e}")
        return None

def update_task(task_id: str, task: TaskUpdate, token: str) -> Optional[Task]:
    url = f"https://api.ticktick.com/open/v1/task/{task_id}"
    data = _api_post(url, token, task.dict(exclude_unset=True))
    if data is None:
        return None
    try:
        return Task.parse_obj(data)
    except Exception as e:
        print(f"Failed to parse updated task: {e}")
        return None

def complete_task(project_id: str, task_id: str, token: str) -> bool:
    url = f"https://api.ticktick.com/open/v1/project/{project_id}/task/{task_id}/complete"
    data = _api_post(url, token, {})
    return data is not None

def delete_task(project_id: str, task_id: str, token: str) -> bool:
    url = f"https://api.ticktick.com/open/v1/project/{project_id}/task/{task_id}"
    return _api_delete(url, token)

def get_project_by_id(project_id: str, token: str) -> Optional[Project]:
    url = f"https://api.ticktick.com/open/v1/project/{project_id}"
    data = _api_get(url, token)
    if data is None:
        return None
    try:
        return Project.parse_obj(data)
    except Exception as e:
        print(f"Failed to parse project: {e}")
        return None

def create_project(project: ProjectCreate, token: str) -> Optional[Project]:
    url = "https://api.ticktick.com/open/v1/project"
    data = _api_post(url, token, project.dict(exclude_unset=True))
    if data is None:
        return None
    try:
        return Project.parse_obj(data)
    except Exception as e:
        print(f"Failed to parse created project: {e}")
        return None

def update_project(project_id: str, project: ProjectUpdate, token: str) -> Optional[Project]:
    url = f"https://api.ticktick.com/open/v1/project/{project_id}"
    data = _api_post(url, token, project.dict(exclude_unset=True))
    if data is None:
        return None
    try:
        return Project.parse_obj(data)
    except Exception as e:
        print(f"Failed to parse updated project: {e}")
        return None

def delete_project(project_id: str, token: str) -> bool:
    url = f"https://api.ticktick.com/open/v1/project/{project_id}"
    return _api_delete(url, token)
