from .auth import get_access_token
from .ticktick import display_projects_and_tasks

def main():
    token = get_access_token()
    display_projects_and_tasks(token)

if __name__ == "__main__":
    main()
