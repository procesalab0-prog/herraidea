"""HRD 1221 flat crossbar visual study. Metres; dimensions are provisional, not fabrication data.
Stdlib-only glTF 2.0 exporter with named components and a reversible explosion clip.
"""
from pathlib import Path
import math, struct, json, subprocess, shutil, os
OUT=Path(__file__).resolve().parents[1]/'assets/projects/hrd-1221/hrd-1221.glb'
buf=bytearray(); views=[]; accessors=[]; meshes=[]; nodes=[]; geometry={}; tracks=[]
def acc(values,kind,ctype=5126,target=None):
    while len(buf)%4: buf.append(0)
    count={'SCALAR':1,'VEC3':3}[kind]; off=len(buf)
    flat=[v for row in values for v in row] if count>1 else values
    buf.extend(struct.pack('<'+('f' if ctype==5126 else 'I')*len(flat),*flat))
    view={'buffer':0,'byteOffset':off,'byteLength':len(buf)-off}
    if target: view['target']=target
    views.append(view)
    a={'bufferView':len(views)-1,'componentType':ctype,'count':len(values),'type':kind}
    if kind=='VEC3':
        a.update(min=[min(v[i] for v in values) for i in range(3)],max=[max(v[i] for v in values) for i in range(3)])
    else: a.update(min=[min(values)],max=[max(values)])
    accessors.append(a); return len(accessors)-1

def shape(kind,dims):
    verts=[]; norms=[]; inds=[]
    def quad(a,b,c,d,n):
        k=len(verts);verts.extend([a,b,c,d]);norms.extend([n]*4);inds.extend([k,k+1,k+2,k,k+2,k+3])
    if kind=='plate':
        node = os.environ.get('NODE') or shutil.which('node') or str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
        data=json.loads(subprocess.check_output([node,str(Path(__file__).with_name('generate_hrd1223_base.mjs')),*map(str,dims)],text=True))
        verts=[tuple(data['positions'][i:i+3]) for i in range(0,len(data['positions']),3)]
        norms=[tuple(data['normals'][i:i+3]) for i in range(0,len(data['normals']),3)]
        inds=list(range(len(verts)))
    elif kind=='box':
        x,y,z=[v/2 for v in dims]
        quad((-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z),(0,0,1))
        quad((x,-y,-z),(-x,-y,-z),(-x,y,-z),(x,y,-z),(0,0,-1))
        quad((x,-y,z),(x,-y,-z),(x,y,-z),(x,y,z),(1,0,0))
        quad((-x,-y,-z),(-x,-y,z),(-x,y,z),(-x,y,-z),(-1,0,0))
        quad((-x,y,z),(x,y,z),(x,y,-z),(-x,y,-z),(0,1,0))
        quad((-x,-y,-z),(x,-y,-z),(x,-y,z),(-x,-y,z),(0,-1,0))
    else:
        r,h,inner,axis=dims; seg=48
        def point(rad,a,y):
            p=(rad*math.cos(a),y,rad*math.sin(a))
            return p if axis=='y' else ((p[1],p[2],p[0]) if axis=='x' else (p[2],p[0],p[1]))
        for i in range(seg):
            a=i*2*math.pi/seg;b=(i+1)*2*math.pi/seg
            k=len(verts)
            verts.extend([point(r,a,-h/2),point(r,a,h/2),point(r,b,h/2),point(r,b,-h/2)])
            norms.extend([point(1,a,0),point(1,a,0),point(1,b,0),point(1,b,0)])
            inds.extend([k,k+1,k+2,k,k+2,k+3])
            for s in [-1,1]:
                pts=[point(inner,a,s*h/2),point(inner,b,s*h/2),point(r,b,s*h/2),point(r,a,s*h/2)]
                if s<0: pts.reverse()
                quad(*pts,point(0,0,s))
            if inner:
                k=len(verts);verts.extend([point(inner,a,-h/2),point(inner,b,-h/2),point(inner,b,h/2),point(inner,a,h/2)])
                norms.extend([point(-1,a,0),point(-1,b,0),point(-1,b,0),point(-1,a,0)])
                inds.extend([k,k+1,k+2,k,k+2,k+3])
    return {'POSITION':acc(verts,'VEC3',target=34962),'NORMAL':acc(norms,'VEC3',target=34962)},acc(inds,'SCALAR',5125,34963)

def part(name,kind,dims,pos,mat=0,delta=(0,0,0),role='post',side=None):
    key=(kind,tuple(dims),mat)
    if key not in geometry:
        attrs,idx=shape(kind,dims)
        meshes.append({'name':name,'primitives':[{'attributes':attrs,'indices':idx,'material':mat}]})
        geometry[key]=len(meshes)-1
    node={'name':name,'mesh':geometry[key],'translation':list(pos),'extras':{'role':role}}
    if side: node['extras']['side']=side
    nodes.append(node)
    if any(delta): tracks.append((len(nodes)-1,pos,tuple(pos[i]+delta[i] for i in range(3))))

# Circular hollow body and round base from the CAD silhouette.
part('Cuerpo_tubo','cyl',(.0254,.89,.0224,'y'),(0,.455,0),delta=(0,.18,0))
part('Base_circular_3_agujeros','plate',(.052,.01,.04,.0045),(0,.005,0),delta=(0,-.08,0))
part('Tapa_superior','cyl',(.0254,.006,.0062,'y'),(0,.903,0),delta=(0,.29,0))
part('Nucleo_superior','cyl',(.009,.064,.0062,'y'),(0,.934,0),delta=(0,.32,0))
part('Vela_pasamanos','cyl',(.006,.056,0,'y'),(0,.974,0),delta=(0,.38,0))
part('Cuna_pasamanos','box',(.055,.005,.033),(0,1.003,0),delta=(0,.49,0))
for y,label in [(.21,'inferior'),(.78,'superior')]:
    lift=.10 if label=='superior' else -.04
    # Each level is ONE continuous flat strip, centrally fastened to the tube.
    part('Solera_'+label,'box',(.23,.026,.006),(0,y,.0284),delta=(0,lift,.15),role='crossbar')
    part('Fijacion_central_'+label,'cyl',(.005,.012,0,'z'),(0,y,.0344),mat=1,delta=(0,lift,.24),role='barfix')
    for sign,side in [(-1,'left'),(1,'right')]:
        prefix=f'Disco_{label}_{side}'
        part(prefix+'_posterior','cyl',(.018,.011,.0035,'z'),(sign*.10,y,.0405),delta=(sign*.12,lift,.27),role='arm',side=side)
        part(prefix+'_junta_posterior','cyl',(.017,.002,.0035,'z'),(sign*.10,y,.047),mat=2,delta=(sign*.12,lift,.31),role='arm',side=side)
        part(prefix+'_junta_frontal','cyl',(.017,.002,.0035,'z'),(sign*.10,y,.061),mat=2,delta=(sign*.12,lift,.43),role='arm',side=side)
        part(prefix+'_tapa','cyl',(.018,.008,.0035,'z'),(sign*.10,y,.066),mat=1,delta=(sign*.12,lift,.49),role='arm',side=side)
        part(prefix+'_tornillo','cyl',(.004,.023,0,'z'),(sign*.10,y,.061),mat=1,delta=(sign*.12,lift,.56),role='arm',side=side)
# Context panes intentionally do not represent a shop drawing or drilled glass specification.
for s,side in [(-1,'left'),(1,'right')]:
    part('Contexto_vidrio_'+side,'box',(.605,.855,.012),(s*.3275,.5175,.054),mat=3,delta=(s*.12,.05,.38),role='context')
part('Contexto_pasamanos','cyl',(.0254,1.32,.0224,'x'),(0,1.031,0),delta=(0,.66,0),role='context')
materials=[
 {'name':'Acero satinado','pbrMetallicRoughness':{'baseColorFactor':[.64,.69,.73,1],'metallicFactor':.88,'roughnessFactor':.28}},
 {'name':'Acero pulido','pbrMetallicRoughness':{'baseColorFactor':[.78,.81,.84,1],'metallicFactor':.95,'roughnessFactor':.19}},
 {'name':'Junta elastomero','pbrMetallicRoughness':{'baseColorFactor':[.028,.032,.035,1],'metallicFactor':0,'roughnessFactor':.85}},
 {'name':'Vidrio referencia','pbrMetallicRoughness':{'baseColorFactor':[.70,.88,.87,.24],'metallicFactor':0,'roughnessFactor':.10},'alphaMode':'BLEND','doubleSided':True}
]
times=acc([0.,1.5,3.],'SCALAR'); samplers=[];channels=[]
for idx,start,end in tracks:
    mid=tuple((start[i]+end[i])/2 for i in range(3))
    samplers.append({'input':times,'output':acc([start,mid,end],'VEC3'),'interpolation':'LINEAR'})
    channels.append({'sampler':len(samplers)-1,'target':{'node':idx,'path':'translation'}})
gltf={'asset':{'version':'2.0','generator':'Herraidea parametric visual study; provisional dimensions'},'scene':0,'scenes':[{'nodes':list(range(len(nodes)))}],'nodes':nodes,'meshes':meshes,'materials':materials,'animations':[{'name':'Despiece','samplers':samplers,'channels':channels}],'buffers':[{'byteLength':len(buf)}],'bufferViews':views,'accessors':accessors}
js=json.dumps(gltf,separators=(',',':')).encode();js+=b' '*((-len(js))%4);buf+=b'\0'*((-len(buf))%4)
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(js)+8+len(buf))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(buf),0x004e4942)+buf)
print(f'{OUT}: {len(nodes)} components, {len(tracks)} animated, {OUT.stat().st_size} bytes')
