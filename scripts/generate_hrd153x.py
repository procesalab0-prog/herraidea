"""HRD 1533 / 1534 / 1535 channel-post visual study. Metres; dimensions are provisional, not fabrication data.
Stdlib-only glTF 2.0 exporter with named components and a reversible explosion clip.
"""
from pathlib import Path
import math, struct, json, subprocess, shutil, os
CORNER=os.environ.get('HRD_CORNER')=='1'
OUT=Path(__file__).resolve().parents[1]/'assets/projects/hrd-153x/hrd-153x.glb'
if CORNER: OUT=OUT.with_name('hrd-153x-esquina.glb')
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
    if kind in ('plate','profile','profilecorner','saddle'):
        node = os.environ.get('NODE') or shutil.which('node') or str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node')
        data=json.loads(subprocess.check_output([node,str(Path(__file__).with_name('generate_hrd153x_shapes.mjs')),kind,*map(str,dims)],text=True))
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

# Common photographic study; code-to-configuration mapping remains unconfirmed.
part('Perfil_acanalado','profilecorner' if CORNER else 'profile',(.06,.89,.06),(0,.455,0),delta=(0,.16,0))
part('Base_cuadrada_4_agujeros','plate',(.105,.105,.008),(0,.004,0),delta=(0,-.09,0))
for sign,side in [(-1,'left'),(1,'right')]:
    for front in [-1,1]:
        part(f'Empaque_{side}_{front}','box',(.016,.86,.003),(sign*.025,.455,front*.0065),mat=2,delta=(sign*.12,.16,front*.05),role='lining',side=side)
    part('Apoyo_vidrio_'+side,'box',(.016,.012,.012),(sign*.025,.038,0),mat=2,delta=(sign*.12,-.03,0),role='lining',side=side)
part('Collarin_superior','cyl',(.015,.026,.010,'y'),(0,.913,0),delta=(0,.29,0))
part('Vela_ajustable','cyl',(.010,.065,.006,'y'),(0,.951,0),delta=(0,.36,0))
part('Eje_articulacion','cyl',(.005,.028,0,'z'),(0,.975,0),mat=1,delta=(0,.40,.08))
for sign in [-1,1]:
    part(f'Oreja_articulada_{sign}','box',(.014,.024,.004),(0,.987,sign*.012),delta=(0,.48,sign*.05))
part('Cuna_curva_dos_agujeros','saddle',(.075,.035,.003),(0,.998,0),delta=(0,.48,0))
for sign,side in [(-1,'left'),(1,'right')]:
    part('Contexto_vidrio_'+side,'box',(.605,.846,.010),(sign*.3195,.467,0),mat=3,delta=(sign*.20,.14,.20),role='context')
part('Contexto_pasamanos','cyl',(.0254,1.32,.0224,'x'),(0,1.0234,0),delta=(0,.64,0),role='context')
if CORNER:
    for n in nodes:
        if n['extras'].get('role')=='lining' and n['extras'].get('side')=='right':
            x,y,z=n['translation']; n['translation']=[z,y,-x]
            n['rotation']=[0,math.sin(math.pi/4),0,math.cos(math.pi/4)]
    tracks=[] # Calculator-only corner assembly.
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
