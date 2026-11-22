"""Resolve locally installed Python; never launch the packaged editor as Python."""
import shutil,subprocess,sys
def python_command(preference="Auto"):
    if preference not in ("Auto","3.12","3.14"):raise ValueError("Invalid Python version")
    for v in (("3.12","3.14") if preference=="Auto" else (preference,)):
        cmds=[]
        if sys.platform=="win32" and shutil.which("py"):cmds.append(["py","-"+v])
        if not getattr(sys,"frozen",False):cmds.append([sys.executable])
        cmds.extend([p] for x in ("python"+v,"python3","python") if (p:=shutil.which(x)))
        for cmd in cmds:
            try:
                r=subprocess.run(cmd+["-c","import sys;print('%d.%d'%sys.version_info[:2])"],capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0)
                if r.returncode==0 and r.stdout.strip()==v:return cmd
            except (OSError,subprocess.TimeoutExpired):pass
    raise RuntimeError("Install Python 3.12 or 3.14 for script execution.")
