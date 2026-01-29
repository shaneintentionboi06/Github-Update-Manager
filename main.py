from controlUI import GitApp
from gitback import GitRepo
def main():
    print("Hello from git-update-management!")
    GitApp(Git=GitRepo()).run()


if __name__ == "__main__":
    main()
