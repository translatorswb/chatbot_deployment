import os
from git import Repo
from git import Git


# git_ssh_identity_file = '/home/faizan/code/chatbot/TWB/rasa/git/ssh_files/4.key'
# git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file


def commit_files():
    # ssh_executable = '/app/git/ssh_files/4.sh'


    # with Git().custom_environment(GIT_SSH=ssh_executable):
    repo_dir = os.getcwd()
    repo = Repo(repo_dir)


    file_list = [
        'data/nlu.md',
        'data/stories.md'
    ]

    import pdb; pdb.set_trace()

    commit_message = 'Autocommit'
    repo.index.add(file_list)
    repo.index.commit(commit_message)
    origin = repo.remote('origin')
    origin.push()


