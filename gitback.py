import git,csv,os
class GitRepo:
    def __init__(self):
        self.PATH = r'data/Repositories.csv'
        self.fieldnames = ['ID','Name','Path']
        self.Actor = git.Actor('Isaac Paul','shane.isaacpaul@gmail.com')
        self.repo_pool,self.repo_count = self.get_repos()
    def check_update(self,ID):
        Repo = self.repo_pool[ID][1]
        Repo.index.update() 
        if Repo.git.status().split()[6] == 'up':
            return False
        elif Repo.git.status().split()[6] == 'behind':
            return True
        else:
            return None
    def init_repo(self,path,url):
        if os.path.exists(path):
            Repository = git.Repo.init(path,mkdir=False)
            #Attaching to the remote (Github Repository)
            try: 
                Repository.create_remote('origin',url)
            except git.GitCommandError as err:
                if err.stderr == 'error: remote origin already exists.':
                    Repository.delete_remote('origin')
                    Repository.create_remote('origin')
            #Writing the Annoncement
            with open(path + r'/GitManage.txt','w') as file:
                file.write('This Directory can be updated using Git Management ;)')
            Repository.git.add('.')
            Repository.git.commit(m='Adding files to the Remote')
            Repository.git.push('-u','origin','master')
            return Repository
        else:
            raise FileNotFoundError
    def start_new_csv(self):
        with open(self.PATH,'w',newline='') as file:
            Writer = csv.writer(file)
            Writer.writerow(self.fieldnames) #self.fieldnames = ['ID','Name','Path'] 
    def get_repos(self):
        Repodict = {}
        Repocount = 0
        try:
            with open(self.PATH,'r',newline='') as file:
                Reader = csv.reader(file)
                for i in Reader:
                    if i != [] and i != self.fieldnames:
                        # print(i)
                        try:
                            Repodict[i[0]] = (i[1],git.Repo(i[2]),i[2])
                            Repocount += 1
                        except git.exc.InvalidGitRepositoryError as err:
                            print(f'.git Folder is gone :( {i}')
        except FileNotFoundError:
            print('File Was Not Found. Creating New Repo')
            self.start_new_csv()
        finally:
            return Repodict,Repocount
    def add_repo(self,name,path,url):
        Repository = self.init_repo(path,url)
        ID = self.repo_count 
        self.repo_count += 1
        self.repo_pool[str(ID)] = Repository
        with open(self.PATH,'a',newline='') as file:
            Writer = csv.writer(file)
            Writer.writerow((ID,name,path))
        return ID
    def add_connect_remote(self,ID,url):
        Repo = self.repo_pool[ID][1]
        try:
            Repo.create_remote('origin',url)
        except git.GitCommandError as err:
            if err.stderr == 'error: remote origin already exists.':
                Repo.delete_remote('origin')
                Repo.create_remote('origin',url)
    def pull_changes(self,ID):
        Repo = self.repo_pool[ID][1]
        Repo.git.pull()
    def remove_repo(self,ID):
        #Remove from the Pool
        Pool = self.repo_pool
        Pool.pop(ID)
        #change the count
        self.repo_count -= 1
        #Rewrite the csv file 
        with open(self.PATH,'w',newline='') as file:
            Writer = csv.writer(file)
            Writer.writerow(self.fieldnames)
            for i,j in Pool.items(): Writer.writerow((i,j[0],j[2]))
    def rollback(self,ID):
        Repo = self.repo_pool[ID][1]
        message = Repo.git.revert('HEAD')
        Repo.git.push()
        return message    
            
            
            
        
if __name__ == '__main__':
    Gito = GitRepo()
    # print(Gito.repo_pool)
    print(Gito.check_update('0'))
    input('Wait.....')
    print(Gito.check_update('0'))
    # Gito.start_new_csv()
    # ID = Gito.add_repo(name='Demo OpenLP',path=r'C:\Users\shAne\AppData\Roaming\openlp\data',url='https://github.com/shaneintentionboi06/laughing-octo-umbrella.git')
    # print(Gito.repo_pool)
    # Gito.check_update('0')
    # Gito.pull_changes('1')
    # Gito.remove_repo('0')
    # if Gito.check_update("1"):
    #     print('There is an Update')
    #     print('pulling changes')
    #     Gito.pull_changes('1')
    # else:
    #     print("There is no Update")