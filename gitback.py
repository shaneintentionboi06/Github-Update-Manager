import git,csv,os
class GitRepo:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.PATH = os.path.join(base_dir,'data','repositories.csv')
        self.fieldnames = ['ID','Name','Path']
        self.repo_pool,self.repo_count = self.get_repos()
    def check_update(self,ID):
        repo = self.repo_pool[ID][1]
        repo.remotes.origin.fetch()
        if repo.head.commit.authored_date < repo.remotes.origin.refs.master.commit.authored_date:
            return True
        elif repo.head.commit.authored_date == repo.remotes.origin.refs.master.commit.authored_date :
            return False
        else:
            return None
    def init_repo(self,path,url):
        if os.path.exists(path):
            repository = git.Repo.init(path,mkdir=False)
            #Attaching to the remote (Github repository)
            try: 
                repository.create_remote('origin',url)
            except git.GitCommandError as err:
                if err.stderr == 'error: remote origin already exists.':
                    repository.delete_remote('origin')
                    repository.create_remote('origin')
            #Writing the Annoncement
            with open(path + r'/GitManage.txt','w') as file:
                file.write('This Directory can be updated using Git Management ;)')
            repository.git.add('.')
            repository.git.commit(m='Adding files to the Remote')
            repository.git.push('-u','origin','master')
            return repository
        else:
            raise FileNotFoundError
    def start_new_csv(self):
        data_dir = os.path.dirname(self.PATH)
        if not os.path.exists(data_dir): os.mkdir(data_dir)
        with open(self.PATH,'w',newline='') as file:
            Writer = csv.writer(file)
            Writer.writerow(self.fieldnames) #self.fieldnames = ['ID','Name','Path'] 
    def get_repos(self):
        repodict = {}
        repocount = 0
        try:
            with open(self.PATH,'r',newline='') as file:
                Reader = csv.reader(file)
                for i in Reader:
                    if i != [] and i != self.fieldnames:
                        # print(i)
                        try:
                            repodict[i[0]] = (i[1],git.Repo(i[2]),i[2])
                            repocount += 1
                        except git.exc.InvalidGitRepositoryError as err:
                            print(f'.git Folder is gone :( {i}')
        except FileNotFoundError:
            print('File Was Not Found. Creating New repo')
            self.start_new_csv()
        finally:
            return repodict,repocount
    def add_repo(self,name,path,url):
        repository = self.init_repo(path,url)
        ID = self.repo_count 
        self.repo_count += 1
        self.repo_pool[str(ID)] = repository
        with open(self.PATH,'a',newline='') as file:
            Writer = csv.writer(file)
            Writer.writerow((ID,name,path))
        return ID
    def add_connect_remote(self,ID,url):
        repo = self.repo_pool[ID][1]
        try:
            repo.create_remote('origin',url)
        except git.GitCommandError as err:
            if err.stderr == 'error: remote origin already exists.':
                repo.delete_remote('origin')
                repo.create_remote('origin',url)
    def pull_changes(self,ID):
        repo = self.repo_pool[ID][1]
        repo.git.pull()
    def remove_repo(self,ID):
        #Remove from the pool
        pool = self.repo_pool
        pool.pop(ID)
        #change the count
        self.repo_count -= 1
        #Rewrite the csv file 
        with open(self.PATH,'w',newline='') as file:
            Writer = csv.writer(file)
            Writer.writerow(self.fieldnames)
            for i,j in pool.items(): Writer.writerow((i,j[0],j[2]))
    def rollback(self,ID):
        repo = self.repo_pool[ID][1]
        message = repo.git.revert('HEAD')
        repo.git.push()
        return message    
            
        
if __name__ == '__main__':
    Gito = GitRepo()
    # print(Gito.repo_pool)
    
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