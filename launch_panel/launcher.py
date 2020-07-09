"""
Simple script to launch applications
"""
import subprocess
from pathlib import Path


def launch_app(executable, args=None, env=None, shell=False, cwd=None):
    """Launch application with all parameters"""
    # collect command
    cmd = [executable]
    if args:
        cmd.extend(args)
    # prepare env
    env = prepare_env(env)
    # prepare work dir
    if cwd:
        cwd = Path(cwd).expanduser().absolute().as_posix()
    # start process
    subprocess.Popen(cmd, env=env, shell=shell, cwd=cwd)


def prepare_env(env):
    """Prepare env fo starting"""
    if env is None:
        return env
    if not isinstance(env, dict):
        raise TypeError('Env must be dict')
    return {k: str(v) for k, v in env.items()}    # all values must be string