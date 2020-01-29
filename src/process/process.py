import subprocess
from typing import List, Tuple


def invoke(cmd: List[str]) -> Tuple[int, str, str]:
    ret = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = ret.stdout.decode('UTF-8')
    stderr = ret.stderr.decode('UTF-8')
    return ret.returncode, stdout, stderr
