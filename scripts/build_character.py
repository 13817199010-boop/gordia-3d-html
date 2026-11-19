"""Blender 4.3: blender -b --python-exit-code 1 --python scripts/build_character.py"""
import bpy
import math
from math import sin, cos, pi, sqrt
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'models'
VIEWS = ROOT / 'renders'
for folder in (OUT, VIEWS):
    folder.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 12
scene.cycles.use_denoising = False
scene.view_settings.view_transform = 'AgX'
scene.render.resolution_x = 680
scene.render.resolution_y = 880
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.world = bpy.data.worlds.new('Softbox ambient')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.54,.60,.72,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .65
current = None

def group(name):
    global current
    current = bpy.data.collections.new(name)
    scene.collection.children.link(current)

def material(name, rgb, rough=.45, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb,1)
    m.use_nodes = True
    bs = m.node_tree.nodes['Principled BSDF']
    for key, val in [('Base Color',(*rgb,1)),('Metallic',metallic),('Roughness',rough)]:
        bs.inputs[key].default_value = val
    return m

skin=material('Porcelain • warm',(.98,.695,.61),.75)
ink=material('Lashes • charcoal',(.012,.006,.013))
lip=material('Rose • lip',(.42,.088,.105))
pearl=material('Ivory • parade silk',(.91,.89,.90),.33)
white=material('Catchlight', (1,.97,.90))
black=material('Onyx • patent',(.016,.018,.029),.24,.25)
cloth=material('Officer wool',(.021,.022,.034),.61)
hair=material('Graphite hair',(.045,.044,.061),.34)
silver=material('Silver-grey hair',(.134,.142,.173),.35)
wine=material('Velvet • oxblood',(.23,.008,.032),.52)
red=material('Carmine satin',(.59,.013,.046),.32)
ruby=material('Ruby iris',(.47,.012,.025),.24)
gold=material('Champagne brass',(.74,.49,.20),.30,.73)
lightgold=material('Polished edges',(.94,.72,.35),.24,.65)
meshmat=material('Smoke • hosiery',(.33,.242,.24),.65)
blue=material('Ribbon • midnight blue',(.02,.046,.15))
steel=material('Gunmetal',(.16,.17,.19),.24,.72)

def attach(o,name,mat):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    current.objects.link(o)
    o.data.materials.append(mat)
    return o

def mesh(name,vs,fs,mat,sub=0):
    data=bpy.data.meshes.new(name)
    data.from_pydata(vs,[],fs); data.update()
    o=bpy.data.objects.new(name,data); current.objects.link(o); data.materials.append(mat)
    for p in data.polygons: p.use_smooth=True
    if sub:
        mod=o.modifiers.new('Rounded seams','SUBSURF'); mod.levels=sub
        mod.render_levels=sub
    return o

def oval(name,loc,scale,mat,tilt=0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=loc)
    o=attach(bpy.context.object,name,mat);o.scale=scale;o.rotation_euler.y=tilt
    for p in o.data.polygons:p.use_smooth=True
    return o

def loft(name,rows,mat,n=24,sub=1,slope=0):
    # Each horizontal ring encodes centre x, y, height and two radii.
    vs=[(x+a*cos(2*pi*j/n),y+b*sin(2*pi*j/n),z+slope*a*cos(2*pi*j/n))
        for x,y,z,a,b in rows for j in range(n)]
    fs=[tuple(reversed(range(n)))]
    for i in range(len(rows)-1):
        for j in range(n):
            k=i*n+j; l=i*n+(j+1)%n
            fs.append((k,l,l+n,k+n))
    fs.append(tuple(range(len(vs)-n,len(vs))))
    return mesh(name,vs,fs,mat,sub)

def cord(name,pts,r,mat):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D'
    data.resolution_u=8;data.bevel_depth=r;data.bevel_resolution=2;data.use_fill_caps=True
    sp=data.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
    for bp,p in zip(sp.bezier_points,pts):
        bp.co=p;bp.handle_left_type=bp.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,data);current.objects.link(o);data.materials.append(mat)
    return o

def badge(name,x,y,z,w,h,mat):
    return mesh(name,[(x-w,y,z),(x,y,z-h),(x+w,y,z),(x,y,z+h),(x,y-.055,z)],
                [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],mat)

def centered(name,profile,mat,**kw):
    return loft(name,[(0,y,z,a,b) for z,a,b,y in profile],mat,**kw)

group('01 • Face and eyes')
centered('Face | jaw to crown',[(6.23,.06,.07,-.13),(6.32,.22,.20,-.09),(6.50,.385,.315,-.045),
 (6.75,.475,.387,.0),(7.02,.50,.41,.015),(7.26,.46,.385,.018),(7.44,.32,.29,.02),(7.52,.10,.12,.02)],skin,n=40,sub=2)
centered('Neck',[(5.94,.20,.20,0),(6.12,.158,.163,0),(6.48,.18,.17,0)],skin)
centered('Choker',[(6.135,.17,.174,0),(6.15,.175,.18,0),(6.205,.17,.175,0)],black)
oval('Nose tip',(0,-.373,6.64),(.046,.058,.052),skin)
cord('Mouth • rose bow',[(-.093,-.322,6.478),(-.025,-.344,6.483),(0,-.347,6.477),(.029,-.342,6.483),(.088,-.324,6.489)],.009,lip)
for s in (-1,1):
    oval('Ear',(s*.447,.004,6.72),(.077,.065,.145),skin)
    # Convex almond with outer corner receding around the cheek.
    def eyept(u,v):
        return (s*(.209+.157*u),-.389+.088*u+.014*u*u,6.853+.043*u+v)
    vs=[eyept(0,0)]
    for j in range(32):
        t=2*pi*j/32; vs.append(eyept(cos(t),sin(t)*(.085 if sin(t)>0 else .061)))
    vs[0]=(vs[0][0],vs[0][1]-.023,vs[0][2])
    mesh('Eyes • almond',vs,[(0,1+j,1+(j+1)%32) for j in range(32)],pearl)
    for name,dx,dy,dz,scale,mat in [('Iris',0,-.018,0,(.071,.020,.069),ruby),('Pupil',0,-.035,0,(.029,.009,.048),ink),('Glint',-.022,-.049,.027,(.016,.007,.017),white)]:
        x,y,z=eyept(dx/.157,0)
        o=oval(name,(x,y+dy,z+dz),scale,mat);o.rotation_euler.z=s*.48
    for label,sign,r in [('Upper lash',1,.019),('Lower line',-1,.007)]:
        pts=[eyept(cos(t*pi/8),sign*sin(t*pi/8)*(.082 if sign==1 else .061)) for t in range(9)]
        cord(label,pts,r,ink)
    cord('Winged lash',[eyept(.74,.055),eyept(1,.009),eyept(1.20,.037)],.014,ink)
    cord('Brow',[eyept(-.85,.135),eyept(.16,.151),eyept(.83,.114)],.019,hair)

group('02 • Hair and bows')
# Crown overlaps the brow only at the sides. Fringe is built strand by strand.
oval('UNVERIFIED_Hair • occipital mass',(0,.17,6.96),(.508,.38,.56),hair)
def lock(name,rows,mat): return loft(name,rows,mat,n=12,sub=2)
for s in (-1,1):
    for j in range(5):
        u=j/4
        rows=[(s*.40,.16+u*.09,7.19,.15,.14),(s*(.51+.11*u),.20+.08*u,6.78,.19,.12),
              (s*(.70+.17*u),.28+.15*u,5.98,.19-.035*u,.10),(s*(.78+.27*u),.35+.24*u,5.04,.17,.09),
              (s*(.71+.37*u),.30+.27*u,4.02,.15,.08),(s*(.65+.48*u),.12+.37*u,3.32+.32*u,.13,.06),
              (s*(.91+.37*u),-.04+.32*u,3.11+.42*u,.017,.012)]
        lock('Hair • long tapered layer',rows,[wine,hair,silver,hair,hair][j])
    for j in range(3):
        u=j/2
        lock('Hair • cheek curl',[(s*(.37+.09*u),-.16,7.31,.142,.104),(s*(.44+.07*u),-.20,7.04,.13,.10),
             (s*(.43+.09*u),-.24,6.76,.105,.085),(s*(.40+.09*u),-.26,6.52,.087,.058),
             (s*(.29+.09*u),-.30,6.40-.04*u,.05,.04),(s*(.24+.07*u),-.35,6.45-.09*u,.008,.008)], [wine,hair,silver][j])
    for j in range(2):
        # Folded ribbon loops taper into the temple knot.
        o=oval('Bows • folded loop',(s*(.51+.044*j),-.019,7.05+.19*j),(.17,.093,.118),red,s*(-.65+.98*j))
        cord('Bows • fold',[(s*.48,-.105,7.11),(s*.55,-.108,7.10+.09*j),(s*.62,-.066,7.05+.18*j)],.012,wine)
    oval('Bows • knot',(s*.49,-.094,7.12),(.083,.07,.09),wine)
    lock('Bows • streamer',[(s*.50,.01,7.11,.09,.06),(s*.61,.08,6.95,.098,.039),(s*.65,.11,6.70,.085,.027),(s*.70,.10,6.57,.013,.018)],red)
for j,(base,tip,height) in enumerate([(-.31,-.36,6.84),(-.21,-.29,6.78),(-.09,-.19,6.89),(.055,-.073,6.73),(.19,.02,6.84),(.32,.18,6.96),(.40,.31,6.99)]):
    lock('Hair • swept fringe',[(base+.05,-.19,7.41,.122,.081),(base+.045,-.31,7.24,.145,.092),
          (base,-.364+.07*abs(base),7.095,.115,.076),(tip+.045,-.406+.16*abs(tip),height+.10,.081,.049),
          (tip,-.413+.20*abs(tip),height,.008,.01)],silver if j in (0,5) else hair)

group('03 • Shako')
slope=.23
centered('Cap • angled crown',[(7.16,.505,.406,.02),(7.20,.533,.442,.01),(7.49,.505,.412,.05),(7.76,.464,.37,.08),(7.80,.43,.34,.08)],cloth,slope=slope)
centered('Cap • patent visor',[(7.12,.47,.44,-.08),(7.15,.552,.515,-.083),(7.20,.535,.454,-.04),(7.235,.51,.409,0)],black,slope=slope)
def front_arc(rad,depth,z,y=0):
    return [(rad*sin(t*pi/16),y-depth*cos(t*pi/16),z+slope*rad*sin(t*pi/16)) for t in range(-7,8)]
cord('Cap • visor piping',front_arc(.525,.493,7.187,-.056),.012,gold)
def grillpoint(u,h):
    x=.46*u
    return (x,.025-.447*sqrt(1-(x/.55)**2),7.23+slope*x+h)
for u in [-.90,-.68,-.43,-.17,.10,.37,.64,.9]:
    cord('Cap • fluted grille',[grillpoint(u,0),grillpoint(u-.10,.35*(1-abs(u)*.69))],.016,gold)
cord('Cap • heraldic arch',[grillpoint(u,.36*(1-abs(u)*.70)) for u in [-1,-.72,-.40,0,.43,.74,1]],.026,lightgold)
cord('Cap • grille sill',[grillpoint(u,0) for u in [-1,-.7,-.3,0,.3,.7,1]],.021,gold)
badge('Cap • crest',0,-.422,7.64,.063,.09,gold)

group('04 • Jacket, shoulder and medals')
centered('Jacket • fitted ivory tunic',[(4.15,.49,.327,-.015),(4.19,.55,.35,0),(4.48,.51,.338,0),
 (4.74,.394,.279,0),(4.98,.408,.29,0),(5.29,.492,.345,-.014),(5.54,.586,.393,-.044),
 (5.72,.605,.37,-.015),(5.94,.644,.284,.0),(6.015,.535,.236,0),(6.07,.245,.18,0)],pearl,n=40,sub=2)
for s in (-1,1):
    lock('Jacket • black side gore',[(s*.466,0,4.30,.064,.22),(s*.457,0,4.47,.091,.255),
      (s*.349,0,4.77,.071,.211),(s*.386,.0,5.10,.07,.215),(s*.49,.0,5.42,.11,.274),
      (s*.529,0,5.64,.12,.262),(s*.49,0,5.84,.103,.204)],black)
    cord('Jacket • braided panel edge',[(s*.38,-.218,4.35),(s*.292,-.207,4.78),(s*.36,-.251,5.20),(s*.474,-.298,5.58)],.014,gold)
    for z,x,y in [(4.97,.224,-.239),(5.27,.276,-.306),(5.55,.32,-.377)]:
        oval('Jacket • brass button',(s*x,y-.015,z),(.044,.025,.048),gold)
        oval('Button • inset',(s*x,y-.037,z),(.020,.009,.024),lightgold)
    # Military lapel folded from the neckline across the upper chest.
    pts=[(s*.20,-.15,6.04),(s*.51,-.21,5.96),(s*.41,-.333,5.80),(s*.06,-.409,5.60),(s*.285,-.327,5.85)]
    mesh('Jacket • folded lapel',pts,[(0,1,4),(1,2,4),(2,3,4)],cloth if s<0 else pearl)
    cord('Lapel • piping',pts[1:4],.014,steel)
centered('Belt • leather waist',[(4.61,.466,.326,0),(4.63,.474,.338,0),(4.76,.439,.323,0),(4.79,.424,.307,0)],black)
for s in (-1,1):
    badge('Belt • split gilt clasp',s*.084,-.334,4.704,.077,.104,gold)
for j,m in enumerate([gold,blue,red]):
    oval('Medals • ribbon bar',(.348+.058*j,-.312+.027*j,5.796),(.034,.025,.036),m)
oval('Medals • suspended disc',(.420,-.321,5.68),(.070,.022,.076),gold)
badge('Medals • relief',.42,-.347,5.68,.039,.053,lightgold)
for i,m in enumerate([red,pearl,blue]):
    cord('Medals • hanging sash',[(.433+.012*i,-.30,5.62),(.60+.012*i,-.25,5.27),(.635+.012*i,-.20,4.96),(.48+.012*i,-.235,4.67)],.014,m)

group('05 • Arms and gauntlets')
for s in (-1,1):
    def limb(name,rows,mat):
        return loft(name,[(s*x,y,z,a,b) for x,y,z,a,b in rows],mat)
    limb('Sleeve • tailored',[(.99,-.02,5.00,.136,.133),(.99,-.02,5.045,.166,.145),(.88,0,5.43,.152,.166),
        (.73,0,5.81,.219,.223),(.617,0,5.94,.208,.216),(.57,.02,5.97,.11,.14)],pearl)
    limb('Shoulder • epaulette',[(.70,0,5.69,.229,.211),(.706,0,5.76,.253,.25),(.645,0,5.94,.237,.24),(.60,.01,6.0,.16,.169)],black)
    if s==-1:
        for i in range(9):
            t=pi*(i+1)/11
            x=.70+.225*cos(t);y=-.225*sin(t)
            cord('Shoulder • bullion fringe',[(s*x,y,5.80),(s*(x+.055),y-.025,5.60),(s*(x+.10),y-.015,5.49+.05*cos(t))],.017,gold)
    limb('Gauntlet • articulated bracer',[(1.244,-.09,4.33,.10,.105),(1.22,-.084,4.43,.12,.13),
        (1.11,-.055,4.74,.157,.15),(1.035,-.034,4.96,.137,.139),(1.013,-.028,5.055,.147,.142)],black)
    for z,x in [(4.36,1.239),(4.45,1.212),(4.87,1.063)]:
        limb('Gauntlet • binding',[(x,-.073,z,.135,.144),(x-.011,-.073,z+.042,.139,.145)],gold if z!=4.45 else red)
    oval('Glove • palm',(s*1.266,-.107,4.21),(.12,.099,.177),black,-s*.20)
    for j in range(4):
        x=1.19+j*.051; h=.14-.022*abs(j-1)
        oval('Glove • separated digit',(s*x,-.12,4.07+.012*j),(.029,.047,h),black,-s*.14)
        oval('Glove • gilt fingertip',(s*(x+.013),-.157,4.04-h*.45+.012*j),(.023,.023,.047),gold,-s*.14)
    oval('Glove • thumb',(s*1.17,-.177,4.19),(.049,.053,.107),black,s*.34)

group('06 • Shorts, stockings and boots')
centered('Shorts • high hip',[(4.05,.468,.315,.016),(4.17,.557,.354,.016),(4.42,.535,.34,0),(4.48,.494,.31,0)],black)
for s in (-1,1):
    def leg(name,rows,mat):
        return loft(name,[(s*x,y,z,a,b) for x,y,z,a,b in rows],mat,n=30)
    leg('Shorts • tailored leg',[(.294,0,3.86,.276,.298),(.290,0,3.89,.29,.31),(.279,.0,4.15,.311,.359),(.25,0,4.40,.277,.31)],black)
    cord('Shorts • carmine welt',[(s*.24,-.291,3.90),(s*.39,-.302,4.056),(s*.53,-.219,4.23),(s*.535,-.13,4.34)],.026,wine)
    badge('Shorts • strap slider',s*.496,-.236,4.215,.057,.084,gold)
    leg('Stockings • thigh',[(.335,.01,2.84,.19,.191),(.334,.012,3.10,.237,.241),(.319,0,3.52,.261,.277),(.29,.0,3.98,.28,.30)],meshmat)
    leg('Boots • tall fitted shaft',[(.38,.035,.28,.146,.162),(.372,.038,.56,.131,.147),(.371,.045,.95,.148,.171),
        (.372,.055,1.46,.191,.218),(.352,.06,1.92,.229,.254),(.337,.053,2.30,.196,.206),
        (.335,.021,2.59,.203,.207),(.333,.01,2.96,.224,.232),(.332,0,3.25,.247,.259)],black)
    leg('Boots • flared cuff',[(.333,.01,2.96,.222,.235),(.333,.01,3.01,.248,.252),(.331,0,3.22,.254,.272),(.331,0,3.27,.251,.266)],cloth)
    for z,y in [(3.177,-.261),(3.03,-.244),(2.72,-.192)]:
        oval('Boots • round stud',(s*.333,y,z),(.050,.024,.054),gold)
    for side in (-1,1):
        cord('Boots • red chevron',[(s*(.335+.183*side),-.13,2.73),(s*(.335+.105*side),-.199,2.81),(s*.335,-.22,2.91)],.035,red)
    badge('Boots • shin insignia',s*.335,-.215,2.62,.059,.226,gold)
    leg('UNVERIFIED_Boots • toe and sole',[(.38,-.115,.082,.151,.335),(.38,-.12,.11,.173,.36),(.38,-.12,.22,.169,.34),(.38,-.061,.31,.145,.237),(.38,.019,.45,.135,.166)],black)
    oval('UNVERIFIED_Boots • heel',(s*.38,.132,.085),(.114,.098,.08),cloth)

group('07 • Cape')
# Two physical surfaces with shared rim; length varies across shoulder and folds.
for s in (-1,1):
    vs=[]; fs=[]; cols=19; rows=13
    for layer in range(2):
        for i in range(rows):
            t=i/(rows-1)
            for j in range(cols):
                u=j/(cols-1)
                x=s*((.035+.68*u)*(1-t)+(.09+1.25*u+.22*sin(pi*u))*t+.12*sin(pi*t)*u)
                y=.29+.12*sin(pi*t)+(.52+.16*cos(4*pi*u))*t-.30*u**3-.15*u**4*t+.051*layer
                z=5.99-.18*u-(3.59+.46*cos(2*pi*u)-.22*u)*t
                vs.append((x,y,z))
    k=cols*rows
    for layer in range(2):
        for i in range(rows-1):
            for j in range(cols-1):
                a=layer*k+i*cols+j
                q=(a,a+1,a+cols+1,a+cols)
                fs.append(q if layer else q[::-1])
    edges=list(range(cols))+[i*cols+cols-1 for i in range(1,rows)]+list(range(k-2,k-cols-1,-1))+[i*cols for i in reversed(range(1,rows-1))]
    for a,b in zip(edges,edges[1:]+edges[:1]): fs.append((a,b,b+k,a+k))
    o=mesh('UNVERIFIED_Cape • lined mantle',vs,fs,red,1);o.data.materials.append(cloth)
    for p in list(o.data.polygons)[(cols-1)*(rows-1):]: p.material_index=1
    outer=[vs[i*cols+cols-1] for i in range(rows)]
    cord('Cape • bound edge',outer,.018,wine)

group('08 • Weapon | toggle collection')
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(1.27,-.13,4.19))
socket=bpy.context.object;socket.name='WeaponSocket.R'
for c in list(socket.users_collection):c.objects.unlink(socket)
current.objects.link(socket)
for name,x,y,z,a,b,h,m in [('Weapon • grip',1.28,-.205,4.15,.067,.066,.29,cloth),
    ('Weapon • ferrule',1.28,-.205,4.43,.081,.080,.07,gold),('Weapon • pommel',1.28,-.205,3.87,.061,.061,.085,gold)]:
    oval(name,(x,y,z),(a,b,h),m)
for j in range(6):
    z=3.98+j*.065
    cord('Weapon • spiral grip',[(1.225,-.23,z),(1.28,-.272,z+.028),(1.331,-.239,z+.056)],.012,lightgold)
badge('Weapon • spearhead',1.28,-.213,4.64,.081,.247,gold)
badge('Weapon • enamel',1.28,-.266,4.64,.036,.161,red)
cord('UNVERIFIED_Weapon • flexible lash',[(1.28,-.205,3.84),(1.44,-.23,3.12),(1.58,-.13,2.49),(1.83,.05,2.03),(2.02,.14,2.14),(2.01,.17,2.48)],.013,black)
for o in list(current.objects):
    if o!=socket:
        o.parent=socket;o.matrix_parent_inverse=socket.matrix_world.inverted()

# Export the character before studio lights, floor and camera are added.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(OUT/'gordia-static.glb'),export_format='GLB',use_selection=True,export_apply=True)
group('09 • Portrait studio (excluded from GLB)')
ground=material('Blue-grey cyclorama',(.144,.160,.196),.9)
bpy.ops.mesh.primitive_plane_add(size=200);attach(bpy.context.object,'Studio floor',ground)
def aim(o,target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,pos,power,size,color):
    bpy.ops.object.light_add(type='AREA',location=pos)
    o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;aim(o,(0,0,4.6))
light('Warm key',(-4,-6,10),700,5,(1,.86,.78))
light('Cool fill',(4,-4,8),550,4,(.78,.84,1))
light('Hair rim',(1,4,9),1050,4,(1,.85,.74))
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO'
def camera(angle):
    t=math.radians(angle);cam.location=(13*sin(t),-13*cos(t),5.75);cam.data.ortho_scale=8.8
    aim(cam,(0,0,3.94))
camera(0)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'gordia-static.blend'),compress=True)
for name,angle in [('front',0),('three-quarter',45),('right',90),('back',180),('left',-90)]:
    camera(angle);scene.render.filepath=str(VIEWS/(name+'.png'));bpy.ops.render.render(write_still=True)
