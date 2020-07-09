import subprocess

def launch_app(executable, args=None, env=None):
    print(executable, args, env)
    cmd = [executable]
    if args:
        cmd.extend(args)
    subprocess.Popen(cmd, env=env)
