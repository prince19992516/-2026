"""B1-丙 独立对照：PyTorch autograd / detach / 不可导点（验证者补充，非原稿代码）。"""
import json
from pathlib import Path

import numpy as np
import torch

OUT = Path(__file__).resolve().parent
torch.set_default_dtype(torch.float64)
res = {}

x = torch.tensor(0.7, requires_grad=True)

# F1 = sin(x^2)+exp(x)
y1 = torch.sin(x ** 2) + torch.exp(x)
g1 = torch.autograd.grad(y1, x, create_graph=True)[0]
g1_2 = torch.autograd.grad(g1, x)[0]
res["F1"] = dict(
    value=float(y1),
    grad=float(g1),
    analytic_grad=float(2 * 0.7 * np.cos(0.49) + np.exp(0.7)),
    grad_error=float(abs(g1 - (2 * 0.7 * np.cos(0.49) + np.exp(0.7)))),
    second=float(g1_2),
    analytic_second=float(2 * np.cos(0.49) - 4 * 0.49 * np.sin(0.49) + np.exp(0.7)),
)

# F2 = sin(x^2)+x*exp(x)
x2 = torch.tensor(0.7, requires_grad=True)
y2 = torch.sin(x2 ** 2) + x2 * torch.exp(x2)
g2 = torch.autograd.grad(y2, x2, create_graph=True)[0]
res["F2"] = dict(
    value=float(y2),
    grad=float(g2),
    analytic_grad=float(2 * 0.7 * np.cos(0.49) + (1 + 0.7) * np.exp(0.7)),
    grad_error=float(abs(g2 - (2 * 0.7 * np.cos(0.49) + 1.7 * np.exp(0.7)))),
)

# 201-point check, exactly as A2 notebook
grid = torch.linspace(-1, 1, 201, requires_grad=True)
gv = torch.sin(grid ** 2) + torch.exp(grid)
gd = torch.autograd.grad(gv, grid, grad_outputs=torch.ones_like(gv))[0]
ana = 2 * grid.detach().numpy() * np.cos(grid.detach().numpy() ** 2) + np.exp(grid.detach().numpy())
res["grid201"] = dict(max_error=float(np.max(np.abs(gd.detach().numpy() - ana))))

# detach
xd = torch.tensor(0.7, requires_grad=True)
det = (xd * xd).detach() * 3.0
try:
    gdet = torch.autograd.grad(det, xd, allow_unused=True)[0]
except Exception as e:  # pragma: no cover
    gdet = f"ERROR: {e}"
res["detach"] = dict(
    grad_on_detached_branch=(None if gdet is None else (gdet if isinstance(gdet, str) else float(gdet))),
    grad_if_not_detached=float(torch.autograd.grad((xd * xd) * 3.0, xd)[0]),
    note="detach 后该分支不向 x 回传；这不是实现错误，但必须在报告中说明",
)

# non-differentiable points
xr = torch.tensor(0.0, requires_grad=True)
torch.relu(xr).backward()
res["relu_at_0"] = dict(torch_grad=float(xr.grad), left=0.0, right=1.0)

xa = torch.tensor(0.0, requires_grad=True)
torch.abs(xa).backward()
res["abs_at_0"] = dict(torch_grad=float(xa.grad), left=-1.0, right=1.0)

# elementwise JVP with ones: show it is sum of Jacobian rows, valid for elementwise F
res["grad_outputs_note"] = (
    "grad_outputs=ones_like(gv) 计算的是 J^T·1；对逐元素 F 它等于逐元素导数，"
    "对耦合输出则不等于逐元素导数。A2 的 201 点检查只对逐元素 F 成立。"
)

with open(OUT / "B1组-丙-torch实测.json", "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=2)
print(json.dumps(res, ensure_ascii=False, indent=2))
