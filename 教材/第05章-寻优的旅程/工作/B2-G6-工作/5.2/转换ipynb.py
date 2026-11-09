# -*- coding: utf-8 -*-
"""把 B2组-验证-源码.py（# %% 分隔，# %% [md] 为 Markdown 单元格）转换为 B2组-验证.ipynb。"""
import nbformat as nbf

src = open('B2组-验证-源码.py', encoding='utf-8').read()
lines = src.split('\n')

cells = []
cur_type, cur_lines = None, []
for ln in lines:
    if ln.startswith('# %%'):
        if cur_type is not None:
            cells.append((cur_type, cur_lines))
        cur_type = 'markdown' if '[md]' in ln else 'code'
        cur_lines = []
    else:
        cur_lines.append(ln)
if cur_type is not None:
    cells.append((cur_type, cur_lines))

nb = nbf.v4.new_notebook()
nb.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}
nb.metadata['language_info'] = {'name': 'python'}
for ctype, clines in cells:
    if ctype == 'markdown':
        # 去掉每行前缀 "# "（或 "#"）
        md = []
        for l in clines:
            if l.startswith('# '):
                md.append(l[2:])
            elif l == '#':
                md.append('')
            else:
                md.append(l)
        nb.cells.append(nbf.v4.new_markdown_cell('\n'.join(md)))
    else:
        nb.cells.append(nbf.v4.new_code_cell('\n'.join(clines)))

nbf.write(nb, 'B2组-验证.ipynb')
print('cells:', len(nb.cells), [c.cell_type for c in nb.cells])
