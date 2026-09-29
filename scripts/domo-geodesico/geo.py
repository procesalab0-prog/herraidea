import numpy as np, itertools
def icosa():
    p=(1+5**.5)/2
    V=[(-1,p,0),(1,p,0),(-1,-p,0),(1,-p,0),(0,-1,p),(0,1,p),(0,-1,-p),(0,1,-p),(p,0,-1),(p,0,1),(-p,0,-1),(-p,0,1)]
    F=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
    V=np.array(V,float); V/=np.linalg.norm(V,axis=1)[:,None]
    # rotar para que el vértice 0 quede arriba
    a=V[0]; z=np.array([0,0,1.]); v=np.cross(a,z); s=np.linalg.norm(v); c=a@z
    K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]]); Rm=np.eye(3)+K+K@K*((1-c)/s**2)
    return (Rm@V.T).T, F
def geodesic(freq):
    V,F=icosa(); pts={}; faces=[]
    def key(p): return tuple(np.round(p,6))
    idx=lambda p: pts.setdefault(key(p/np.linalg.norm(p)), len(pts))
    for a,b,c in F:
        A,B,C=V[a],V[b],V[c]; g={}
        for i in range(freq+1):
            for j in range(freq+1-i):
                k=freq-i-j; g[i,j]=idx((A*i+B*j+C*k)/freq)
        for i in range(freq):
            for j in range(freq-i):
                faces.append((g[i,j],g[i+1,j],g[i,j+1]))
                if i+j<freq-1: faces.append((g[i+1,j],g[i+1,j+1],g[i,j+1]))
    P=np.array(sorted(pts,key=pts.get))
    return P, faces
if __name__=='__main__':
    for f in (3,4):
        P,Fc=geodesic(f)
        zs=np.round(P[:,2],4); lv=sorted(set(zs),reverse=True)
        print(f'{f}V: {len(P)} vértices, {len(Fc)} caras')
        for z in lv: print('   z=%.4f  n=%d  altura/D si corte aquí=%.3f'%(z,(zs==z).sum(),(1-z)/2))
