"""Chapter 2 reproducible experiments. NumPy float64; teaching AD, no AD framework.

Graph supports elementwise arrays for batching, and its scalar-output reverse pass
is the same chain rule as a scalar computational graph. No symbolic rewriting.
"""
from pathlib import Path
import os, tempfile
# A literal '/tmp' becomes '<drive>:\tmp' on Windows, so take the platform
# temporary directory instead of assuming a POSIX root.
os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'sc_ch2_matplotlib'))
import json, platform, time, importlib.metadata, hashlib, sys, numbers
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parent
FIG = ROOT / 'ABC共用-图片'
SEED = 2026


def barycentric_weights(nodes):
    x = np.asarray(nodes, dtype=float)
    if x.ndim != 1 or x.size < 1 or not np.all(np.isfinite(x)):
        raise ValueError('nodes must be a finite nonempty 1-D array')
    delta = x[:, None] - x[None, :]
    np.fill_diagonal(delta, 1.)
    if np.any(delta == 0):
        raise ValueError('nodes must be distinct')
    # Common logarithmic scaling prevents products from over/underflowing.
    logw = -np.sum(np.log(np.abs(delta)), axis=1)
    return np.prod(np.sign(delta), axis=1) * np.exp(logw - logw.max())


def barycentric_evaluate(nodes, values, points):
    x, y, z = map(lambda a: np.asarray(a, dtype=float), (nodes, values, points))
    w = barycentric_weights(x)
    if y.shape != x.shape or not np.all(np.isfinite(y)) or not np.all(np.isfinite(z)):
        raise ValueError('finite values must match nodes; finite evaluation points required')
    flat = z.ravel()
    d = flat[:, None] - x[None, :]
    hit = d == 0
    safe = np.where(hit, 1., d)
    terms = w / safe
    # Node values are assigned directly, never as an inf/inf quotient.
    exact = hit.any(axis=1)
    out = np.empty(flat.size)
    out[~exact] = (terms[~exact] @ y) / terms[~exact].sum(axis=1)
    out[exact] = y[np.argmax(hit[exact], axis=1)]
    return out.reshape(z.shape)


def lagrange_direct(nodes, values, points):
    x, y, z = np.asarray(nodes), np.asarray(values), np.asarray(points)
    out = np.zeros_like(z, dtype=float)
    for j in range(len(x)):
        basis = np.ones_like(z, dtype=float)
        for k in range(len(x)):
            if k != j:
                basis *= (z-x[k])/(x[j]-x[k])
        out += y[j]*basis
    return out


def poly_design(points, degree, basis='power', interval=(-1., 1.)):
    x = np.asarray(points, dtype=float)
    a, b = interval
    # degrees are integers, not floats or booleans.
    if (isinstance(degree, bool) or not isinstance(degree, numbers.Integral)
            or degree < 0 or not b > a or x.ndim != 1 or not np.all(np.isfinite(x))):
        raise ValueError('finite vector, nonnegative integer degree and a<b required')
    degree = int(degree)
    t = (2*x-a-b)/(b-a)
    if basis == 'power':
        return np.vander(t, degree+1, increasing=True)
    if basis != 'chebyshev':
        raise ValueError('unknown basis')
    A = np.ones((len(t), degree+1))
    if degree:
        A[:, 1] = t
    for k in range(1, degree):
        A[:, k+1] = 2*t*A[:, k]-A[:, k-1]
    return A


def fit_polynomial(x, y, degree, basis='power', interval=(-1., 1.)):
    A = poly_design(x, degree, basis, interval)
    y = np.asarray(y, dtype=float)
    if y.shape != (len(x),) or not np.all(np.isfinite(y)):
        raise ValueError('finite data must match samples')
    c, _, rank, _ = np.linalg.lstsq(A, y, rcond=None)
    if rank < degree+1:
        raise ValueError('rank deficient design: coefficients are not unique')
    return c, A


class Dual:
    """First order forward AD: value and directional derivative."""
    def __init__(self, value, d=0.): self.value, self.d = np.asarray(value), np.asarray(d)
    @staticmethod
    def lift(x): return x if isinstance(x, Dual) else Dual(x)
    def __add__(self, other):
        b=self.lift(other); return Dual(self.value+b.value, self.d+b.d)
    __radd__=__add__
    def __mul__(self, other):
        b=self.lift(other); return Dual(self.value*b.value, self.d*b.value+self.value*b.d)
    __rmul__=__mul__
    def sin(self): return Dual(np.sin(self.value), np.cos(self.value)*self.d)
    def exp(self):
        e=np.exp(self.value); return Dual(e,e*self.d)
    def tanh(self):
        t=np.tanh(self.value); return Dual(t,(1-t*t)*self.d)


class Jet2:
    """Second order forward AD; d2 is the derivative, not Taylor coefficient."""
    def __init__(self, value, d=0., d2=0.):
        self.value,self.d,self.d2=map(np.asarray,(value,d,d2))
    @staticmethod
    def lift(x): return x if isinstance(x,Jet2) else Jet2(x)
    def __add__(self,other):
        b=self.lift(other);return Jet2(self.value+b.value,self.d+b.d,self.d2+b.d2)
    __radd__=__add__
    def __mul__(self,other):
        b=self.lift(other)
        return Jet2(self.value*b.value,self.d*b.value+self.value*b.d,
                    self.d2*b.value+2*self.d*b.d+self.value*b.d2)
    __rmul__=__mul__
    def sin(self):
        v=self.value;return Jet2(np.sin(v),np.cos(v)*self.d,np.cos(v)*self.d2-np.sin(v)*self.d**2)
    def exp(self):
        e=np.exp(self.value);return Jet2(e,e*self.d,e*(self.d2+self.d**2))
    def tanh(self):
        t=np.tanh(self.value);s=1-t*t
        return Jet2(t,s*self.d,s*self.d2-2*t*s*self.d**2)


def _unbroadcast(gradient, shape):
    g=np.asarray(gradient)
    while g.ndim>len(shape): g=g.sum(axis=0)
    for axis,size in enumerate(shape):
        if size==1: g=g.sum(axis=axis,keepdims=True)
    return g.reshape(shape)


class Graph:
    """Auditable reverse AD; batch arrays, scalar loss, accumulated gradients."""
    def __init__(self, value, parents=()):
        self.value=np.asarray(value,dtype=np.float64)
        self.parents=parents;self.grad=np.zeros_like(self.value)
    @staticmethod
    def lift(x): return x if isinstance(x,Graph) else Graph(x)
    def __add__(self,other):
        b=self.lift(other)
        return Graph(self.value+b.value,((self,lambda g:_unbroadcast(g,self.value.shape)),
                                        (b,lambda g:_unbroadcast(g,b.value.shape))))
    __radd__=__add__
    def __mul__(self,other):
        b=self.lift(other)
        return Graph(self.value*b.value,((self,lambda g:_unbroadcast(g*b.value,self.value.shape)),
                                        (b,lambda g:_unbroadcast(g*self.value,b.value.shape))))
    __rmul__=__mul__
    def __neg__(self): return self*(-1.)
    def __sub__(self,other): return self+(-self.lift(other))
    def tanh(self):
        t=np.tanh(self.value);return Graph(t,((self,lambda g:g*(1-t*t)),))
    def sin(self): return Graph(np.sin(self.value),((self,lambda g:g*np.cos(self.value)),))
    def exp(self):
        e=np.exp(self.value);return Graph(e,((self,lambda g:g*e),))
    def sum(self,axis=None):
        def pull(g):
            return np.ones_like(self.value)* (np.expand_dims(g,axis) if axis is not None else g)
        return Graph(self.value.sum(axis=axis),((self,pull),))
    def mean(self): return self.sum()*(1./self.value.size)
    def backward(self):
        if self.value.ndim!=0: raise ValueError('backward requires scalar output')
        order=[];seen=set()
        def visit(node):
            if id(node) not in seen:
                seen.add(id(node))
                for parent,_ in node.parents: visit(parent)
                order.append(node)
        visit(self)
        for node in order:node.grad=np.zeros_like(node.value)
        self.grad=np.ones_like(self.value)
        for node in reversed(order):
            for parent,pull in node.parents:parent.grad+=pull(node.grad)


def composite(x): return (x*x).sin()+x.exp()

def network_graph(x, params):
    a,w,b,c=params
    return (a*(Graph(np.asarray(x)[:,None])*w+b).tanh()).sum(axis=1)+c


def network_analytic(x,params):
    a,w,b,c=params
    t=np.tanh(np.asarray(x)[:,None]*w+b);s=1-t*t
    return c+(a*t).sum(axis=1),(a*w*s).sum(axis=1),(-2*a*w*w*t*s).sum(axis=1)


def network_jet(x,params):
    a,w,b,c=params
    out=Jet2(np.zeros_like(x)+c)
    xx=Jet2(x, np.ones_like(x))
    for aj,wj,bj in zip(a,w,b):out=out+aj*(wj*xx+bj).tanh()
    return out.value,out.d,out.d2


def network_loss(params,x,y):
    nodes=[Graph(p) for p in params]
    r=network_graph(x,nodes)-y
    loss=(r*r).mean();loss.backward()
    return float(loss.value),[p.grad.copy() for p in nodes]


def train_network(steps=14000,width=12):
    rng=np.random.default_rng(SEED)
    x=np.linspace(-1.,1.,81);y=np.sin(np.pi*x)
    params=[rng.normal(0.,.3,width),rng.normal(0.,1.,width),rng.normal(0.,.4,width),np.array(0.)]
    m=[np.zeros_like(p) for p in params];v=[np.zeros_like(p) for p in params]
    history=[];start=time.perf_counter()
    for step in range(1,steps+1):
        loss,grads=network_loss(params,x,y)
        # Deliberate two-stage learning-rate schedule, fixed before evaluation.
        rate=.01 if step<=8000 else .002
        for j,g in enumerate(grads):
            m[j]=.9*m[j]+.1*g;v[j]=.999*v[j]+.001*g*g
            params[j]-=rate*(m[j]/(1-.9**step))/(np.sqrt(v[j]/(1-.999**step))+1e-8)
        if step==1 or step%200==0:history.append([step,loss])
    final,_=network_loss(params,x,y)
    return params,x,y,history,final,time.perf_counter()-start


def _savefig(name):
    FIG.mkdir(exist_ok=True,parents=True)
    plt.tight_layout();plt.savefig(FIG/name,dpi=160);plt.close()


def interpolation_experiment():
    f=lambda x:1/(1+25*x*x)
    z=-1+2*(np.arange(6001)+.371)/6001
    rows=[];plt.figure(figsize=(9,4))
    for n in (8,16,32):
        for kind in ('equispaced','Chebyshev zeros'):
            x=np.linspace(-1,1,n+1) if kind=='equispaced' else np.cos((2*np.arange(n+1)+1)*np.pi/(2*n+2))
            y=f(x);p=barycentric_evaluate(x,y,z)
            assert np.array_equal(barycentric_evaluate(x,y,x),y)
            err=float(np.max(np.abs(p-f(z))))
            rows.append(dict(n=n,nodes=kind,grid_max_error=err,node_max_error=0.))
            plt.semilogy(z,np.maximum(abs(p-f(z)),1e-17),label=f'{kind}, n={n}')
    plt.xlabel('x');plt.ylabel('absolute error');plt.legend(fontsize=7,ncol=2)
    _savefig('experiment-runge-errors.png')
    plt.figure(figsize=(9,4))
    plt.plot(z,f(z),'k',label='Runge function')
    for kind in ('equispaced','Chebyshev zeros'):
        n=16;x=np.linspace(-1,1,n+1) if kind=='equispaced' else np.cos((2*np.arange(n+1)+1)*np.pi/(2*n+2))
        plt.plot(z,barycentric_evaluate(x,f(x),z),label=kind);plt.plot(x,f(x),'o',ms=3)
    plt.ylim(-1.5,2);plt.xlabel('x');plt.ylabel('value');plt.legend();_savefig('experiment-runge-nodes.png')
    x=np.array([-1.,0.,1.]);q=lambda z:2*z*z-z+3
    checks=np.array([-.73,.23,.89])
    np.testing.assert_allclose(barycentric_evaluate(x,q(x),checks),q(checks),atol=3e-15,rtol=3e-15)
    np.testing.assert_allclose(lagrange_direct(x,q(x),checks),q(checks),atol=3e-15,rtol=3e-15)
    bad=0
    for xx,yy in [([0.,0.],[1.,2.]),([0.,1.],[1.]),([0.,np.nan],[1.,2.])]:
        try:barycentric_evaluate(xx,yy,[.5])
        except ValueError:bad+=1
    assert bad==3
    return dict(rows=rows,grid_size=len(z),grid='shifted uniform interior grid of [-1,1], offset=.371, exact analytic target',baseline='2x^2-x+3 at three nonnodes; direct Lagrange; 3 invalid inputs rejected')


def least_squares_experiment():
    rng=np.random.default_rng(SEED);x=np.linspace(-1,1,41);truth=lambda t:np.exp(t)
    noise=rng.normal(0.,.015,len(x));y=truth(x)+noise;z=-1+2*(np.arange(2001)+.371)/2001
    rows=[];pred=[]
    for basis in ('power','chebyshev'):
        c,A=fit_polynomial(x,y,12,basis);p=poly_design(z,12,basis)@c;pred.append(p)
        Q,R=np.linalg.qr(A,mode='reduced');cq=np.linalg.solve(R,Q.T@y)
        disagreement=float(np.max(abs(poly_design(z,12,basis)@cq-p)))
        assert disagreement<1e-9
        rows.append(dict(basis=basis,condition_2=float(np.linalg.cond(A)),residual_2=float(np.linalg.norm(A@c-y)),grid_max_error=float(np.max(abs(p-truth(z)))),qr_prediction_max_difference=disagreement))
    basis_difference=float(np.max(abs(pred[0]-pred[1])))
    assert basis_difference<1e-9
    # Independent exact line fit: symmetry gives c0=2, c1=3.
    cs,_=fit_polynomial(np.array([-1.,0.,1.]),np.array([-1.,2.,5.]),1)
    np.testing.assert_allclose(cs,[2.,3.],atol=2e-15,rtol=2e-15)
    try:fit_polynomial(np.array([0.,0.,1.]),np.ones(3),2)
    except ValueError:pass
    else:raise AssertionError('rank deficiency must be reported')
    # Same polynomial space: transformed [100,102] data agree with [-1,1].
    scaled,_=fit_polynomial(x+101,y,12,'chebyshev',(100.,102.))
    np.testing.assert_allclose(poly_design(z+101,12,'chebyshev',(100.,102.))@scaled,pred[1],atol=2e-12,rtol=2e-12)
    plt.figure(figsize=(9,4));plt.plot(x,y,'o',ms=3,label='noisy samples');plt.plot(z,truth(z),'k',label='exp(x)')
    for basis,p in zip(('power','Chebyshev'),pred):plt.plot(z,p,label=f'{basis}, degree 12')
    plt.xlabel('x');plt.ylabel('value');plt.legend();_savefig('experiment-least-squares.png')
    # Overfitting comparison changes degree only, keeping these samples fixed.
    degree_rows=[]
    for d in (3,12,30):
        c,A=fit_polynomial(x,y,d,'chebyshev');p=poly_design(z,d,'chebyshev')@c
        degree_rows.append(dict(degree=d,residual_2=float(np.linalg.norm(A@c-y)),grid_max_error=float(np.max(abs(p-truth(z))))))
    return dict(rows=rows,degree_comparison=degree_rows,samples=41,degree=12,noise_std=.015,basis_prediction_max_difference=basis_difference,normal_equations_solved=False,scaling_interval=[100.,102.],rank_deficient_rejected=True)


def trapezoid_square(n):
    if not isinstance(n,int) or isinstance(n,bool) or n<1:raise ValueError('n must be positive integer')
    x=np.linspace(0.,1.,n+1);y=x*x;h=1./n
    return h*(.5*y[0]+y[1:-1].sum()+.5*y[-1])


def differentiation_experiment():
    rows=[]
    for n in (4,8,16,32,64):
        val=trapezoid_square(n);err=val-1/3
        np.testing.assert_allclose(err,1/(6*n*n),rtol=1e-12,atol=1e-16)
        rows.append(dict(N=n,T_N=val,signed_error_I_minus_T=-err,absolute_error=err))
    x=.7;value=np.sin(x*x)+np.exp(x);d1=2*x*np.cos(x*x)+np.exp(x)
    d2=2*np.cos(x*x)-4*x*x*np.sin(x*x)+np.exp(x)
    dual=composite(Dual(x,1.));jet=composite(Jet2(x,1.));gx=Graph(x);out=composite(gx);out.backward()
    for d in (dual.d,jet.d,gx.grad):np.testing.assert_allclose(d,d1,rtol=2e-15,atol=2e-15)
    np.testing.assert_allclose(jet.d2,d2,rtol=3e-15,atol=3e-15)
    np.testing.assert_allclose(jet.value,value,rtol=2e-15,atol=2e-15)
    hs=np.logspace(-1,-16,61);fun=lambda t:np.sin(t*t)+np.exp(t)
    forward=np.array([(fun(x+h)-fun(x))/h for h in hs]);central=np.array([(fun(x+h)-fun(x-h))/(2*h) for h in hs])
    plt.figure(figsize=(8,4));plt.loglog(hs,abs(forward-d1),'o-',ms=2,label='forward difference');plt.loglog(hs,abs(central-d1),'o-',ms=2,label='central difference');plt.axhline(max(abs(float(dual.d)-d1),np.finfo(float).eps),c='k',ls='--',label='AD / rounding scale')
    plt.xlabel('step h');plt.ylabel('absolute derivative error');plt.legend();_savefig('experiment-difference-steps.png')
    return dict(trapezoid=rows,x=x,F=value,analytic_d1=d1,analytic_d2=d2,dual_d1=float(dual.d),reverse_d1=float(gx.grad),jet_d2=float(jet.d2),manual_reverse=dict(bar_exp=1.,bar_sin=1.,bar_square=float(np.cos(x*x)),bar_x=float(np.exp(x)+2*x*np.cos(x*x))),difference=dict(h=hs.tolist(),forward_error=abs(forward-d1).tolist(),central_error=abs(central-d1).tolist(),best_central_h=float(hs[np.argmin(abs(central-d1))]),best_central_error=float(np.min(abs(central-d1)))))


def network_experiment():
    params,x,y,history,loss,elapsed=train_network()
    z=-1+2*(np.arange(2001)+.371)/2001
    assert np.min(abs(z[:,None]-x[None,:]))>1e-12
    values=network_analytic(z,params);jets=network_jet(z,params)
    checks=[float(np.max(abs(a-b))) for a,b in zip(values,jets)]
    for a,b in zip(values,jets):np.testing.assert_allclose(a,b,atol=3e-13,rtol=3e-13)
    truths=[np.sin(np.pi*z),np.pi*np.cos(np.pi*z),-np.pi**2*np.sin(np.pi*z)]
    errors=[float(np.max(abs(a-b))) for a,b in zip(values,truths)]
    # Directional parameter gradient has an independently written analytic formula.
    L,grads=network_loss(params,x,y);a,w,b,c=params;t=np.tanh(x[:,None]*w+b);r=(c+(a*t).sum(axis=1))-y;s=1-t*t
    analytic=[2*(r[:,None]*t).mean(axis=0),2*(r[:,None]*a*s*x[:,None]).mean(axis=0),2*(r[:,None]*a*s).mean(axis=0),np.array(2*r.mean())]
    gradient_errors=[float(np.max(abs(g-ga))) for g,ga in zip(grads,analytic)]
    for g,ga in zip(grads,analytic):np.testing.assert_allclose(g,ga,atol=3e-14,rtol=3e-12)
    rng=np.random.default_rng(2026);directions=[rng.normal(size=p.shape) for p in params];norm=np.sqrt(sum(np.sum(d*d) for d in directions));directions=[d/norm for d in directions]
    exact_direction=sum(np.sum(g*d) for g,d in zip(grads,directions));h=1e-5
    loss_value=lambda pp:float(np.mean((network_analytic(x,pp)[0]-y)**2))
    diff=(loss_value([p+h*d for p,d in zip(params,directions)])-loss_value([p-h*d for p,d in zip(params,directions)]))/(2*h)
    assert abs(diff-exact_direction)<1e-8
    plt.figure(figsize=(10,7))
    for k in range(3):
        plt.subplot(3,1,k+1);plt.plot(z,truths[k],'k',label='analytic target');plt.plot(z,values[k],label='trained network');plt.ylabel(('u','du/dx','d2u/dx2')[k]);plt.legend(fontsize=7)
    plt.xlabel('x');_savefig('experiment-network-derivatives.png')
    plt.figure(figsize=(8,4));hh=np.array(history);plt.semilogy(hh[:,0],hh[:,1]);plt.xlabel('Adam step');plt.ylabel('training mean square loss');_savefig('experiment-network-loss.png')
    # eps*sin(k*x) has small values and non-small derivatives, independently of fitting.
    k=100;eps=1/k**2
    plt.figure(figsize=(9,4))
    for j,series in enumerate((eps*np.sin(k*z),eps*k*np.cos(k*z),-eps*k*k*np.sin(k*z))):plt.plot(z,series,label=f'error derivative order {j}')
    plt.xlabel('x');plt.ylabel('counterexample error');plt.legend();_savefig('experiment-high-frequency.png')
    relu_h=.01
    relu=lambda v:np.maximum(0.,v)
    relu_away=(relu(np.array([-.7,.6])+relu_h)-2*relu(np.array([-.7,.6]))+relu(np.array([-.7,.6])-relu_h))/relu_h**2
    np.testing.assert_allclose(relu_away,0.,atol=1e-11,rtol=0.)
    relu_kink=[float((relu(h)-2*relu(0.)+relu(-h))/h**2) for h in (.1,.01,.001)]
    np.testing.assert_allclose(relu_kink,[10.,100.,1000.],atol=1e-10,rtol=1e-13)
    return dict(seed=SEED,device='CPU',dtype='float64',width=int(w.size),parameter_count=int(sum(p.size for p in params)),training_points=81,test_points=2001,test_grid='shifted uniform interior grid, offset=.371, disjoint from training points',steps=14000,optimizer='Adam beta1=.9 beta2=.999 eps=1e-8; learning rate .01 for 8000 steps then .002',training_scope='all a,w,b,c jointly; value-only loss',final_loss=loss,train_grid_max_error=float(np.max(abs(network_analytic(x,params)[0]-y))),independent_grid_max_errors=dict(value=errors[0],first_derivative=errors[1],second_derivative=errors[2]),jet_vs_analytic_max_differences=checks,reverse_vs_analytic_parameter_gradient_max_differences=gradient_errors,directional_gradient=dict(reverse=float(exact_direction),central_difference=float(diff),h=h,absolute_difference=float(abs(diff-exact_direction))),history=history,training_seconds=elapsed,params={name:p.tolist() for name,p in zip(('a','w','b','c'),params)},counterexamples=dict(high_frequency=dict(k=k,epsilon=eps,continuous_sup_errors=[eps,eps*k,eps*k*k]),relu=dict(formula='max(0,x): derivative 0 for x<0 and 1 for x>0; not differentiable at 0',second_difference_away=relu_away.tolist(),kink_second_difference=relu_kink,kink_steps=[.1,.01,.001])))


def environment():
    packages={k:importlib.metadata.version(k) for k in ('numpy','matplotlib','nbformat','nbclient','ipykernel','jupyter_client')}
    return dict(python=platform.python_version(),interpreter=sys.executable,module_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),platform=platform.platform(),packages=packages,seed=SEED,dtype='float64',device='CPU',extra_installs=[],ad_implementation='self-contained teaching Dual/Graph/Jet2 in ch2_numerics.py')


def run_all():
    results={'interpolation':interpolation_experiment(),'least_squares':least_squares_experiment(),'differentiation':differentiation_experiment(),'network':network_experiment()}
    (ROOT/'实验结果.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'环境版本.json').write_text(json.dumps(environment(),ensure_ascii=False,indent=2)+'\n')
    return results

if __name__=='__main__':
    results=run_all()
    print(json.dumps({k:(v if k!='network' else {kk:vv for kk,vv in v.items() if kk not in ('history','params')}) for k,v in results.items()},ensure_ascii=False,indent=2))
