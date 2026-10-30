"""Execute a notebook with this script's Python, starting a clean kernel.

Usage: /path/to/course/python tools/execute_notebook.py path/to/notebook.ipynb
The kernelspec is temporary: it does not modify the user's Jupyter configuration.
"""
from pathlib import Path
import argparse, json, os, sys, tempfile

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('notebook',type=Path)
    args=parser.parse_args()
    path=args.notebook.resolve()
    with tempfile.TemporaryDirectory(prefix='ch2-kernel-') as temp:
        kernels=Path(temp)/'kernels'/'ch2-course'
        kernels.mkdir(parents=True)
        (kernels/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Python (Scientific Computation 2026)','language':'python'}))
        old=os.environ.get('JUPYTER_PATH','')
        os.environ['JUPYTER_PATH']=temp+(os.pathsep+old if old else '')
        # '/tmp' is not a POSIX-only assumption: on Windows it resolves to the
        # root of the current drive, so use the platform temporary directory.
        os.environ.setdefault('MPLCONFIGDIR', os.path.join(tempfile.gettempdir(), 'sc_ch2_matplotlib'))
        import nbformat
        from nbclient import NotebookClient
        nb=nbformat.read(path,as_version=4)
        for cell in nb.cells:
            if cell.cell_type=='code':cell.outputs=[];cell.execution_count=None
        client=NotebookClient(nb,timeout=180,kernel_name='ch2-course',resources={'metadata':{'path':str(path.parent)}})
        client.execute()
        nbformat.write(nb,path)
        errors=[o for c in nb.cells if c.cell_type=='code' for o in c.outputs if o.output_type=='error']
        if errors:raise RuntimeError(f'{len(errors)} error outputs')
        print(f'Executed and saved: {path}; code cells={sum(c.cell_type=="code" for c in nb.cells)}; errors=0')

if __name__=='__main__':main()
