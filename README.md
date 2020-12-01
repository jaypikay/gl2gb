# GitLab to GitBlit Migration

## Install

Install requirements globally (requires root): 

    python -m pip install -r requirements.txt

Install requirements for your user:

    python -m pip install --user -r requirements.txt


## Configure

Modify the variables to your needs:

  * GITLAB_HOST = 'https://gitlab.com'
  * GITLAB_TOKEN = 'PersonalAccessToken_api'
  * GITBLIT_HOST = 'gitblit'  # Change: Gitblit host address
  * GITBLIT_PORT = 29419  # Change: Gitblit ssh port
  * GITBLIT_USER = 'user'
  * GITBLIT_DIR = '/'  # or 'project_name/' or f'~{GITBLIT_USER}' for private


## Run

    python gl2gb.py
