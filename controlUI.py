from textual.app import App,ComposeResult,on
from textual.screen import Screen,ModalScreen
from textual.containers import ScrollableContainer,Container,VerticalScroll
from textual.widgets import Header,Footer,TextArea,Button,Static,Input

class Git_repo(Container):
    
    def compose(self):
        yield Button('Update',variant='success',classes='up button',disabled=True)
        yield Static('Old Text', classes='message')
        yield Static('Other Text', classes='message')
        yield Button('remove', classes='remove button')
        yield Button('Rollback',variant='error', classes='roll button')
    
    @on(Button.Pressed,'.up')
    def apply_update(self): 
        ID = self.id.lstrip('I')
        try:
            self.app.Git_Connect.pull_changes(ID)
            self.app.notify('New Changes Applied',severity='information')
            self.update_status()
        except Exception as err:
            self.app.notify('Error: Maybe Latest Update is Pulled',severity='error')
    def update_status(self):
        ID = self.id.lstrip('I')
        if self.app.Git_Connect.check_update(ID):
            self.query_one('.up',Button).disabled = False
    def on_mount(self):
        self.update_status()
        message = self.query_one('.message',Static)
        message.update(self.name)
    @on(Button.Pressed,'.remove')
    def remove_instance(self): 
        self.app.push_screen(Delete_Screen(name=self.id))
    @on(Button.Pressed,'.roll')
    def rollback(self):
        ID = self.id.lstrip('I')
        try: 
            Message = self.app.Git_Connect.rollback(ID)
            self.app.notify(Message)
        except Exception as err:
            self.app.notify('Error: Something Went Wrong')
class Delete_Screen(ModalScreen): 
    def compose(self):
        yield Delete_Dialog(name=self.name)
        yield Footer()
class Delete_Dialog(Container):
    BINDINGS = [('escape','pop_screen','Go Back')]
    def compose(self):
        yield Static('Do You really want to remove this Repository?')
        yield Button('Yes',variant='warning',classes='yes')
        yield Button('No',variant='default',classes='no')
    
    @on(Button.Pressed,'.no')
    def action_pop_screen(self):
        self.app.pop_screen()
    
    @on(Button.Pressed,'.yes')
    def delete_instance(self):
        self.app.Git_Connect.remove_repo(self.name.lstrip('I'))
        ID = '#' + self.name
        Scroll = self.app.query_one('.Scroll_menu',ScrollableContainer)
        Scroll.remove_children(ID)
        self.app.pop_screen()
        self.app.notify(f'Repo Number {ID} has been Removed')

class Add_Dialog(Container):
    BINDINGS = [('escape','Cancel','Go Back')]
    def compose(self):
        yield Static('Repository Details',classes='message')
        yield Input(placeholder='Name',valid_empty=False,classes='in name')
        yield Input(placeholder='Path',valid_empty=False,classes='in path')
        yield Input(placeholder='Repository URL',valid_empty=False,classes='in url')
        yield Button('Add',classes='button add',variant= 'success')
        yield Button('Cancel',classes='button Cancel',variant='error')
    
    @on(Button.Pressed,'.add')
    def submit(self):
        Name = self.query_one('.name',Input).value
        Path = self.query_one('.path',Input).value
        Url = self.query_one('.url',Input).value
        try:
            ID = self.app.Git_Connect.add_repo(name=Name,path=Path,url=Url)
            self.app.notify('Repository added Successfully')
            Scroll = self.app.query_one('.Scroll_menu',ScrollableContainer)
            ID = 'I'+ str(ID)
            Scroll.mount(Git_repo(id=ID,name=Name))
            self.app.pop_screen()
        except PermissionError as err:
            self.app.notify(f'Permission Denied: Please close {err.filename}',severity='error')
        except FileNotFoundError as err:
            self.app.notify('The Path Does not Exist :(')
        except git.GitCommandError as err:
            (f'Git Error: {err.stderr}')
        except Exception as err:
            self.app.notify(f'Unknown Error: Well X__X')

    @on(Button.Pressed,'.Cancel')
    def action_Cancel(self):
        self.app.pop_screen()
class Add_Screen(ModalScreen):
    def compose(self):
        yield Add_Dialog(classes='Add Dialog')
        
class git_app(App):
    CSS_PATH='style.css'
    BINDINGS = [('a','key_a','Add Repository'),('r','key_r','Refresh Repositories')]
    
    def __init__(self,Git, driver_class = None, css_path = None, watch_css = False, ansi_color = False):
        self.Git_Connect = Git
        super().__init__(driver_class, css_path, watch_css, ansi_color)
    
    def compose(self):
        yield Header()
        yield ScrollableContainer(classes='Scroll_menu')
        yield Footer()
        
    def on_mount(self):
        Scroll = self.app.query_one('.Scroll_menu',ScrollableContainer)
        Pool = self.Git_Connect.repo_pool
        for ID,others in Pool.items():
            sID = 'I' + ID
            Scroll.mount(Git_repo(id=sID,name=others[0],classes='repo'))
    def key_a(self):
        self.app.push_screen(Add_Screen(classes='Add TScreen'))
    def key_r(self):
        Scroll = self.query_one('.Scroll_menu',ScrollableContainer)
        Repos = Scroll.query_children('.repo')
        for i in Repos: i.update_status()
        self.app.notify('Refreshed',severity='information')
        
    
class test_app(App):
    def compose(self):
        yield Header()
        self.app.push_screen(Add_Screen())
        yield Footer()
if __name__ == '__main__':
    from gitback import GitRepo,git
    Git_Connect = GitRepo()
    git_app(Git=Git_Connect).run()
    # test_app().run()