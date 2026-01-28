from controlUI import git_app
from gitback import GitRepo
def main():
    print("Hello from git-update-management!")
    git_app(Git=GitRepo()).run()


if __name__ == "__main__":
    main()
