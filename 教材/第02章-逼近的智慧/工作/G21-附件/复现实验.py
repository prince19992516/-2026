from pathlib import Path
import os, sys, subprocess, json
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpec

BASE=Path(__file__).resolve().parent
OUT=BASE.parent
os.environ['JUPYTER_RUNTIME_DIR']=str(BASE/'.runtime')
os.environ['IPYTHONDIR']=str(BASE/'.ipython')
os.environ['MPLCONFIGDIR']=str(BASE/'.matplotlib')
os.environ['PYTHONIOENCODING']='utf-8'
for x in ['.runtime','.ipython','.matplotlib']:(BASE/x).mkdir(exist_ok=True)
km=KernelManager(kernel_name='python3')
km._kernel_spec=KernelSpec(argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
                          display_name='Python 3 (G21)',language='python')
path=OUT/'A2组-实验.ipynb'
nb=nbformat.read(path,as_version=4)
client=NotebookClient(nb,km=km,timeout=300,resources={'metadata':{'path':str(OUT)}},allow_errors=False)
try:
    client.execute()
finally:
    nbformat.write(nb,path)
    logs=[]
    for i,c in enumerate(nb.cells):
        if c.cell_type!='code':continue
        logs.append(f'=== Code cell {i}, execution {c.execution_count} ===')
        for o in c.outputs:
            if o.output_type=='stream':logs.append(o.text)
            elif o.output_type=='error':logs.append('\n'.join(o.traceback))
    (OUT/'数据'/'A2组-执行日志.txt').write_text('\n'.join(logs),encoding='utf-8')
errors=[o for c in nb.cells if c.cell_type=='code' for o in c.outputs if o.output_type=='error']
assert not errors
assert all(c.execution_count is not None for c in nb.cells if c.cell_type=='code')
nbformat.validate(nb)
print((OUT/'数据'/'A2组-实测摘要.json').read_text(encoding='utf-8'))
print('Notebook clean-kernel execution and validation passed.')
