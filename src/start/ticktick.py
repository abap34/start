import requests

# ----- pydantic モデル定義 -----

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
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.ticktick.com/open/v1/project"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("プロジェクト一覧の取得に失敗しました:", response.status_code, response.text)
        return []

def get_project_data(project_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.ticktick.com/open/v1/project/{project_id}/data"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"プロジェクトデータの取得に失敗しました (projectId={project_id}):", response.status_code, response.text)
        return None

def display_projects_and_tasks(token):
    projects = get_all_projects(token)
    if not projects:
        print("プロジェクトが存在しません。")
        return

    for project in projects:
        project_id = project.get("id")
        project_name = project.get("name")
        print(f"【プロジェクト】 {project_name} (ID: {project_id})")
        project_data = get_project_data(project_id, token)
        if project_data:
            tasks = project_data.get("tasks", [])
            if tasks:
                print("  └─ タスク一覧:")
                for task in tasks:
                    print(f"      ・ {task.get('title')} (ID: {task.get('id')})")
            else:
                print("  └─ タスクはありません。")
        print("-" * 40)
