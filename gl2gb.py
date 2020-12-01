#!/usr/bin/env python

import time
import os
from subprocess import run, DEVNULL
import tarfile
import gitlab
import paramiko
from rich.progress import Progress

progress = Progress(transient=True)
progress.start()

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()

# TODO: Change the next five lines to match your needs.
GITLAB_HOST = 'https://gitlab.com'
GITLAB_TOKEN = 'PersonalAccessToken_api'
GITBLIT_HOST = 'gitblit'  # Change: Gitblit host address
GITBLIT_PORT = 29419  # Change: Gitblit ssh port
GITBLIT_USER = 'user'
GITBLIT_DIR = '/'  # or 'project_name/' or f'~{GITBLIT_USER}' for private

# No changes needed
GITBLIT_URI = f'ssh://{GITBLIT_USER}@{GITBLIT_HOST}:{GITBLIT_PORT}'

gl = gitlab.Gitlab(GITLAB_HOST, private_token=GITLAB_TOKEN)
ssh.connect(GITBLIT_HOST, port=GITBLIT_PORT)

os.makedirs('./exports', exist_ok=True)
os.makedirs('./repos', exist_ok=True)

progress.log('Fetching project list...')
for project in progress.track(gl.projects.list(all=True)):
    if os.path.exists(f'repos/{project.path}.done'):
        progress.log(f'{project.name}: Already exported and cloned')
        continue

    progress.log(f'{project.name}: Creating export...')
    export = project.exports.create()
    export.refresh()
    while export.export_status != 'finished':
        time.sleep(0.25)
        export.refresh()

    progress.log(f'{project.name}: Downloading export...')
    with open(f'exports/{project.path}.tgz', 'wb') as f:
        export.download(streamed=True, action=f.write)

    # progress.log(f'Preparing {project.name} for re-import')
    with tarfile.open(f'exports/{project.path}.tgz', 'r:gz') as t:
        progress.log(f'{project.name}: Extracting ./project.bundle...')
        try:
            t.extract('./project.bundle')
        except KeyError:
            continue

        progress.log(f'{project.name}: Cloning into bare repository...')
        ret = run(['/usr/bin/git', 'clone', '--mirror', './project.bundle',
                   f'repos/{project.path}'],
                  stderr=DEVNULL, stdout=DEVNULL)

        progress.log(f'{project.name}: Creating new repository...')
        ssh.exec_command(f'gb repos new {GITBLIT_DIR}/{project.path}')

        progress.log(f'{project.name}: Setting remote...')
        ret = run(['/usr/bin/git', '--git-dir', f'repos/{project.path}',
                   'remote', 'set-url', 'origin',
                   f'{GITBLIT_URI}/{GITBLIT_DIR}/{project.path}'],
                  stderr=DEVNULL, stdout=DEVNULL)

        progress.log(f'{project.name}: Pushing local repository to remote...')
        ret = run(['/usr/bin/git', '--git-dir', f'repos/{project.path}',
                   'push'],
                  stderr=DEVNULL, stdout=DEVNULL)

        os.remove('./project.bundle')
        os.rename(f'repos/{project.path}', f'repos/{project.path}.done')

progress.stop()
