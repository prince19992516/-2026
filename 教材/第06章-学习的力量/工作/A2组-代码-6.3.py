import time, numpy as np
np.random.seed(0)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

# ================= 6.3 方法实现与运行 =================
# --- 数据生成计时：包住 网格/矩阵/系数抽取/求值，t_gen 为一次性总耗时 ---
t_gen = time.time()
# 传统求解器：二阶中心差分，矩阵与右端项网格
M_FINE, M_COARSE = 1024, 256
x_f = (np.arange(1,M_FINE+1))/(M_FINE+1); x_c=(np.arange(1,M_COARSE+1))/(M_COARSE+1)
def fd_inv(M):
    h=1/(M+1)
    A=(2*np.diag(np.ones(M))-np.diag(np.ones(M-1),1)-np.diag(np.ones(M-1),-1))/h**2
    return np.linalg.inv(A)
Ainv_f, Ainv_c = fd_inv(M_FINE), fd_inv(M_COARSE)

# 一族右端项：先抽一次系数，再在任意网格求值
KMAX, SENSOR = 8, 51
sensor_x=np.linspace(0,1,SENSOR); _k=np.arange(1,KMAX+1).astype(float); _dec=_k**-1.5
def gen_coef(n): return np.random.randn(n,KMAX)*_dec, np.random.randn(n,KMAX)*_dec
def eval_f(a,b,x):
    X=x[None,:]; KK=_k[:,None]
    return (a[:,:,None]*np.cos(2*np.pi*KK*X)[None]+b[:,:,None]*np.sin(2*np.pi*KK*X)[None]).sum(1)

N_TR, N_TE = 800, 200
ar,br = gen_coef(N_TR); U_tr=(Ainv_c@eval_f(ar,br,x_c).T).T; fs_tr=eval_f(ar,br,sensor_x)
ae,be = gen_coef(N_TE); U_te=(Ainv_f@eval_f(ae,be,x_f).T).T; fs_te=eval_f(ae,be,sensor_x)
U_ct=(Ainv_c@eval_f(ae,be,x_c).T).T
t_gen = time.time() - t_gen   # 数据生成总耗时（秒，含一次性求逆）

# --- DeepONet：branch 读采样值，trunk 读坐标，内积出解（手写两层 tanh MLP+Adam）---
P,H=32,64
def init(i,o): return np.random.randn(i,o)*np.sqrt(2/i), np.zeros(o)
W1b,b1b=init(SENSOR,H); W2b,b2b=init(H,P); W1t,b1t=init(1,H); W2t,b2t=init(H,P)
pr=[W1b,b1b,W2b,b2b,W1t,b1t,W2t,b2t]; m=[np.zeros_like(p) for p in pr]; v=[np.zeros_like(p) for p in pr]
def fwd(fs,xq):
    hb=np.tanh(fs@pr[0]+pr[1]); B=hb@pr[2]+pr[3]
    ht=np.tanh(xq@pr[4]+pr[5]); T=ht@pr[6]+pr[7]
    return B,hb,T,ht,B@T.T

x_tr=x_c[:,None]; U=U_tr; Xb=fs_tr
t0=time.time()
for ep in range(1,15001):
    B,hb,T,ht,Y=fwd(Xb,x_tr); D=(Y-U)/(U.shape[0]*U.shape[1])
    dT=D.T@B; dht=dT@pr[6].T*(1-ht**2)
    gW2t,gB2t=ht.T@dT,dT.sum(0); gW1t,gB1t=x_tr.T@dht,dht.sum(0)
    dB=D@T; dhb=dB@pr[2].T*(1-hb**2)
    gW2b,gB2b=hb.T@dB,dB.sum(0); gW1b,gB1b=Xb.T@dhb,dhb.sum(0)
    gs=[gW1b,gB1b,gW2b,gB2b,gW1t,gB1t,gW2t,gB2t]
    for i in range(8):
        m[i]=.9*m[i]+.1*gs[i]; v[i]=.999*v[i]+.001*gs[i]**2
        pr[i]-=1e-3*(m[i]/(1-.9**ep))/(np.sqrt(v[i]/(1-.999**ep))+1e-8)
t_train=time.time()-t0

# --- 推理计时：包住对 200 个测试函数的预测 ---
t0=time.time(); _,_,_,_,U_pred=fwd(fs_te,x_f[:,None]); t_infer=time.time()-t0

print("train relL2=%.3e"%(np.linalg.norm(Y-U)/np.linalg.norm(U)))
print("time: data-gen=%.3e s/%d func | train=%.3e s | infer=%.3e ms/%d func"
      %(t_gen, N_TR+N_TE, t_train, t_infer*1000, N_TE))

# ================= 6.3 误差图表与比较 =================
# --- 误差统计（与原版一致）---
err_d=np.linalg.norm(U_pred-U_te,axis=1)/np.linalg.norm(U_te,axis=1)
U_cti=np.stack([np.interp(x_f,x_c,r) for r in U_ct])
err_fd=np.linalg.norm(U_cti-U_te,axis=1)/np.linalg.norm(U_te,axis=1)
print("DeepONet 测试 relL2 均值=%.3e 中位=%.3e"%(err_d.mean(),np.median(err_d)))
print("FD 粗网格 relL2 均值=%.3e"%err_fd.mean())

# --- fig1：左=解曲线对比，右=误差箱线（与原版一致）---
fig,ax=plt.subplots(1,2,figsize=(11,4))
ax[0].plot(x_f,U_te[0],"k-",lw=2,label="truth(FD1024)"); ax[0].plot(x_f,U_pred[0],"r--",label="DeepONet")
ax[0].plot(x_f,U_cti[0],"b:",label="FD256"); ax[0].set_xlabel("x"); ax[0].set_ylabel("u(x)")
ax[0].legend(fontsize=8)
ax[1].boxplot([err_d,err_fd],tick_labels=["DeepONet","FD coarse"]); ax[1].set_yscale("log")
ax[1].set_ylabel("relative L2 (log)"); plt.tight_layout(); plt.savefig("fig1.png",dpi=130)

# --- fig2_cost：成本柱状图（data gen 与 infer 用 ms，train 用 s；对数轴）---
data_ms = t_gen/(N_TR+N_TE)*1000      # 每函数数据生成毫秒
train_s = t_train                     # 训练秒（一次性）
infer_ms= t_infer*1000/N_TE           # 每函数推理毫秒
labels = ["data gen (per func)", "train (once, s)", "DeepONet infer (per func)"]
vals   = [data_ms, train_s, infer_ms]
colors = ["#9ca3af", "#f59e0b", "#14b8a6"]   # 灰 / 橙 / 青绿
fig,ax=plt.subplots(figsize=(7,5))
bars=ax.bar(labels,vals,color=colors,width=0.55)
ax.set_yscale("log"); ax.set_title("cost: generate data vs train vs infer")
ax.set_ylabel("time (ms, train in s)")
for b,v in zip(bars,vals):
    ax.text(b.get_x()+b.get_width()/2, v, f"{v:.2g}", ha="center", va="bottom", fontsize=9)
ax.set_ylim(1e-3,1e3)
plt.tight_layout(); plt.savefig("fig2_cost.png",dpi=130)

print("saved: fig1.png, fig2_cost.png")
