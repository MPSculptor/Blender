bl_info = {
    "name": "Phyllotactic Dome",
    "author": "Martin Preston",
    "version": (1,5),
    "blender": (3, 3, 0),
    "location": "View3D > Add > Mesh > Phyllotactic Dome",
    "description": "Adds a new Phyllotactic Dome",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}


import bpy
from bpy import data as D, context as C
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
import bmesh
import math
import mathutils 
from mathutils import Matrix, Vector
from bmesh.types import BMVert
from bpy.props import *
import random

def return_z_place (i, maximum_point, full_radius, corrected_radius):
    try:
        zz = (math.cos(math.asin((math.sqrt(i)*corrected_radius)/full_radius)))*maximum_point
    except:
        zz = (math.cos(math.asin(round((math.sqrt(i)*corrected_radius)/full_radius))))*maximum_point
    return(zz)

def add_spiral(self, context,
    spiral_name,parastichy,quads,
    full_diameter, point_number,
    dome, flat_width_high,
    flat_width_low, base_width,
    depression_width, depression_depth,
    degrees_over,
    base_twist,
    base_twist_height,base_twist_lateral,
    base_twist_factor,reset_drop,jitter,
    make_tighter,compress_spine_top,compress_spine_bottom
    ):
       
    # ***  My Code ***
    
    # declared dictionary of created meshes
    mesh_name_mapping = {}
    
    #calculated variable
    full_radius = full_diameter/2 # need radius in calculations
    corrected_radius = full_radius / ( math.sqrt(point_number-1) ) #send corrected figure to the Maths to keep spiral within radius
    depression = True # is depression active. Shuts off so doesn't depress base
    if depression_width == 0 :
        depression = False
        
    match parastichy: #set the spiral numbers 
        case "OP1":
            spiral_a=2
            spiral_b=3
        case "OP2":
            spiral_a=3
            spiral_b=5
        case "OP3":
            spiral_a=5
            spiral_b=8
        case "OP4":
            spiral_a=8
            spiral_b=13
        case "OP5":
            spiral_a=13
            spiral_b=21
        case "OP6":
            spiral_a=21
            spiral_b=34
        case _:
            spiral_a=8
            spiral_b=13  
            
    #restrict vertex numebrs
    if (point_number<(spiral_a+spiral_b+1)):
        point_number=(spiral_a+spiral_b)
            
    match quads:
        case "OP3":
            face_shape ="Vert"
        case "OP2":
            face_shape ="Horiz"
        case _:
            face_shape ="Quad"
              
            
    element_angle =  (math.pi*2)/((spiral_b/spiral_a)+1)   #rotation between elements 
               
    #dictionary to store the vertices in
    base_vertices = [{'x':0,'y':0,'z':0,'theta':0,'dome_theta':0,'radius':0} for x in range(0, point_number+1)] # raw data as straight spiral
    vertices = [{'x':0,'y':0,'z':0} for x in range(0, point_number+1)] # for adjusted data
    vertices_spine = [{'x':0,'y':0,'z':0} for x in range(0, point_number+1)] # for central spine
    
    # can't allow base max width higher than max width
    if flat_width_low >= flat_width_high:
        flat_width_low = flat_width_high
                
    #work out height of maximum width
    maximum_point = dome # full height
    zone_2_first = round((1-flat_width_high)*(point_number-1)) # first i of flat section
    zone_2_last = round((1-flat_width_low)*(point_number-1)) # first i of bottom section
    zone = "Zone X"
    print ("Zone 1 = 0 to ",zone_2_first-1)
    print ("Zone 1 = ",zone_2_first," to ",zone_2_last)
    print ("Zone 3 = ",zone_2_last+1," to ",point_number-1)

            
    for i in range (point_number): # Calculate base data for all points
                
        #calculate consistent rotational position
        angle = (element_angle * i)
        radius = math.sqrt(i) * corrected_radius
        #calculate positions
        x_place = math.cos(angle)*radius
        y_place = math.sin(angle)*radius
        # work out height on dome using trig
        try:
            try:
                angle_for_dome = math.asin(radius / full_radius) # sine Theta = Opp/Hyp
            except:
                angle_for_dome = math.asin(round(radius / full_radius)) # sine Theta = Opp/Hyp
        except:
            break
        z_place = math.cos(angle_for_dome)*maximum_point

        # Assign a location to vertex.
        base_vertices[i+1]['x'] = x_place
        base_vertices[i+1]['y'] = y_place
        base_vertices[i+1]['z'] = z_place
        base_vertices[i+1]['theta'] = angle
        base_vertices[i+1]['dome_theta'] = angle_for_dome
        base_vertices[i+1]['radius'] = radius
        
        # x and y already set to 0 by assignment
        vertices_spine[i+1]['z'] = z_place
        
    #work out some marker points
    i_max = point_number-1 # The maximum vertex number
    zone_1_last = zone_2_first # i counts 1 less that vertex number
    zone_1_max_radius = base_vertices[zone_1_last]['radius']
    zone_1_max_angle = base_vertices[zone_1_last]['dome_theta']
    zone_1_low_z = base_vertices[zone_1_last]['z']
    zone_3_first = zone_2_last+2
    zone_3_high_z = base_vertices[zone_3_first]['dome_theta']
    zone_3_adjust_position = (point_number-zone_2_last-2)
    zone_3_adjust_radius = math.sqrt(pow(base_vertices[zone_3_adjust_position]['x'],2)+pow(base_vertices[zone_3_adjust_position]['y'],2))
    zone_3_adjust_height = return_z_place(zone_3_adjust_position,maximum_point, full_radius, corrected_radius)
    zone_3_start_height = return_z_place(zone_3_first,maximum_point, full_radius, corrected_radius)
    
                
    for i in range (point_number): # adjust the different zones
        x_place = base_vertices[i+1]['x']
        y_place = base_vertices[i+1]['y']
        z_place = base_vertices[i+1]['z']
        old_radius = base_vertices[i+1]['radius']
        old_angle = base_vertices[i+1]['dome_theta']
        
        if i < zone_2_first: # for vertices above flat mid section
            zone = "Zone 1"
            #adjust to full width first
            radius_adj = full_radius/zone_1_max_radius
            #extra adjustment to make transition smoother. ie idealise to circle
            angle = ((zone_1_max_angle-old_angle)/zone_1_max_angle)*(math.pi/2)
            ideal = math.cos(angle)*zone_1_max_radius
            try:
                adj_adj = ideal/old_radius
            except:
                adj_adj = 0
            radius_adj = radius_adj*adj_adj  
            
            x_place = x_place*radius_adj
            y_place = y_place*radius_adj      
                            
        elif i > zone_2_last: # for vertices below bulge point
            zone = "Zone 3"
              
            base_adjust = (point_number-zone_2_last-1)-(i-(zone_2_last+1))
            base_adjust_percent = (-(base_adjust-(point_number-zone_2_last-1)))/(point_number-zone_2_last)
            
            x_place_adj= base_vertices[base_adjust+1]['x']
            y_place_adj= base_vertices[base_adjust+1]['y']
            radius_adj = math.sqrt(pow(x_place_adj,2)+pow(y_place_adj,2))
            old_angle = base_vertices[base_adjust+1]['dome_theta']
            zone_3_adj_max_angle = base_vertices[zone_3_adjust_position]['dome_theta']
            
            angle = base_vertices[i+1]['theta']
            x_place = math.cos(angle)*radius_adj
            y_place = math.sin(angle)*radius_adj
            
            #Take z from 'above' to make better dome on base
            z_place= base_vertices[base_adjust+1]['z']
            
            #radius adjust to make full width like top arc
            if (zone_3_adjust_radius <0.0000001):
                zone_3_adjust_radius = 0.0000001
            radius_adj = full_radius/zone_3_adjust_radius
            
            #extra adjustment to make transition smoother. ie idealise to circle
            angle = ((zone_3_adj_max_angle-old_angle)/zone_3_adj_max_angle)*(math.pi/2)
            ideal = math.cos(angle)*zone_3_adjust_radius
            try:
                adj_adj = ideal/zone_3_adjust_radius
            except:
                adj_adj = 0
            radius_adj = radius_adj*adj_adj
                    
            x_place = x_place*radius_adj
            y_place = y_place*radius_adj

            #adjust back out again for wider base radius
            radius_new = math.sqrt(pow(x_place,2)+pow(y_place,2))
            desired_radius = full_radius-((full_radius-radius_new)*(1-base_width))
            correction = (desired_radius/radius_new)
            x_place=x_place*correction
            y_place=y_place*correction
            
            print("z_place ",z_place)
            #adjust z to bring things tighter
            z_place = zone_3_start_height-((z_place-zone_3_adjust_height) / (((z_place-zone_3_adjust_height)+1) *make_tighter))
            print ("zp ",z_place,"z3 ",zone_3_start_height,"   z3a ",zone_3_adjust_height)                      
        else :
            zone = "Zone 2 - no change"
            if (old_radius>0):
                zone = "Zone 2"

                radius_adj = full_radius/old_radius
                x_place = x_place*radius_adj
                y_place = y_place*radius_adj
                            
        depression_radius = full_radius*depression_width # size of depression
        if depression : # if its active
            # no need to calculate if outside depression
            # work out hypoteneuse
            hypoteneuse = math.sqrt((pow(x_place,2)+(pow(y_place,2))))
            if hypoteneuse > depression_radius: # check if needed, cancel if depression exceeded
                depression = False
                
        if depression : # indent if required
                how_deep =(maximum_point*depression_depth)*(1-(math.sin((hypoteneuse/depression_radius)*(math.pi/2)))) # get curved depression from sin
                z_place -= how_deep
                            
        # Assign a location to vertex.
        vertices[i+1]['x'] = x_place
        vertices[i+1]['y'] = y_place
        vertices[i+1]['z'] = z_place
        new_radius = math.sqrt(pow(x_place,2)+pow(y_place,2))

    #Adjust the z axis to fill the space
    #find last position and range to lowest
    lowest_point = vertices[point_number]['z']
    range_from_top = maximum_point-lowest_point  
    # run through and scale them all up to fill space 
    for i in range (point_number):
        z_old = vertices[i+1]['z']
        z_new = z_old*((z_old-lowest_point)/(maximum_point-lowest_point))
        vertices[i+1]['z'] = z_new
        vertices_spine[i+1]['z'] = z_new
        
        # *** My basic Routine Ends *** 
        
    # $$$ Rotation Routines $$$
    
    # Apply transform to each vertex coordinate.
    
    #  1) Drop down to where based displacement affects and rotate everything over
    
    #work out figures
    drop = base_twist_height * maximum_point
    top = vertices[1]['z']
    side_move = base_twist_lateral * full_radius
    twist = math.radians(base_twist)
    # move to maintain rotation point
                 
    #drop and move to get rotation point for base shift
    translate_1= Matrix.Translation(Vector((0.0,side_move,-drop)))
    
    for i in range(0, len(vertices)):        
        vr = Vector((vertices[i]['x'],vertices[i]['y'],vertices[i]['z']))
        vs = Vector((vertices_spine[i]['x'],vertices_spine[i]['y'],vertices_spine[i]['z']))
        vr = translate_1 @ vr
        vs = translate_1 @ vs
        vertices[i]['x'] = vr[0]
        vertices[i]['y'] = vr[1]
        vertices[i]['z'] = vr[2]
        vertices_spine[i]['x'] = vs[0]
        vertices_spine[i]['y'] = vs[1]
        vertices_spine[i]['z'] = vs[2]
            
    # rotate  left and right proportionally
          
    if (base_twist >0): # Only if there is twist to do !
        
        for i in range(0, len(vertices)):
            #shear based on distance from bottom. factor in to alter affect
            shear_angle = twist*math.pow(((top-vertices[i]['z'])/maximum_point),base_twist_factor)                    
            shear_1 = Matrix.Rotation(-shear_angle,4,Vector((1.0,0.0,0)))
            vr = Vector((vertices[i]['x'],vertices[i]['y'],vertices[i]['z']))
            vs = Vector((vertices_spine[i]['x'],vertices_spine[i]['y'],vertices_spine[i]['z']))
            vr = shear_1 @ vr
            vs = shear_1 @ vs
            vertices[i]['x'] = vr[0]
            vertices[i]['y'] = vr[1]
            vertices[i]['z'] = vr[2]
            vertices_spine[i]['x'] = vs[0]
            vertices_spine[i]['y'] = vs[1]
            vertices_spine[i]['z'] = vs[2]
        
    #  3) Put it back where it came from 
    
    # Governed by the rest_drop flag to make it easier to visualise the base adjustment 
    
    #raise 
    for i in range(0, len(vertices)):
        if not (reset_drop):
            translate_2 = Matrix.Translation(Vector((0.0,0.0,drop)))
            vr = Vector((vertices[i]['x'],vertices[i]['y'],vertices[i]['z']))
            vs = Vector((vertices_spine[i]['x'],vertices_spine[i]['y'],vertices_spine[i]['z']))
            vr = translate_2 @ vr
            vs = translate_2 @ vs
            vertices[i]['x'] = vr[0]
            vertices[i]['y'] = vr[1]
            vertices[i]['z'] = vr[2]
            vertices_spine[i]['x'] = vs[0]
            vertices_spine[i]['y'] = vs[1]
            vertices_spine[i]['z'] = vs[2]
            
        
    #4 Apply lean as a graduated rotation based on height aqnd jitter
    
    for i in range(0, len(vertices)):

        #bend more the higher you are up
        rise = vertices[i]['z']/maximum_point
        lean = math.radians(degrees_over)*rise
        
        X_Jitter = full_radius /10*jitter*(random.randrange(-100,100)/100)
        Y_Jitter = full_radius /10*jitter*(random.randrange(-100,100)/100)
        Z_Jitter = full_radius /10*jitter*(random.randrange(-100,100)/100)
                 
        #set bend in x and y axes
        rotate_3 = Matrix.Rotation(lean, 4, Vector((1.0, 0.0, 0.0)))
        translate_3 = Matrix.Translation(Vector((X_Jitter,Y_Jitter,Z_Jitter)))
        vr = Vector((vertices[i]['x'],vertices[i]['y'],vertices[i]['z']))
        vs = Vector((vertices_spine[i]['x'],vertices_spine[i]['y'],vertices_spine[i]['z']))
        vr = rotate_3 @ translate_3 @ vr
        vs = rotate_3 @ translate_3 @ vs
        vertices[i]['x'] = vr[0]
        vertices[i]['y'] = vr[1]
        vertices[i]['z'] = vr[2]
        vertices_spine[i]['x'] = vs[0]
        vertices_spine[i]['y'] = vs[1]
        vertices_spine[i]['z'] = vs[2]
        
    # pick average of top and bottom compressions and compress towards this
    spine = len(vertices_spine)
    spine_middle = math.floor(spine/2)
    print(spine,"  ",spine_middle)
    for i in range(0,spine_middle):
        change = (spine_middle-i)
        new_position = (spine_middle - math.floor(change*compress_spine_top))
        print (i," < middle  , change = ",change,"   new = ",new_position)
        vertices_spine[i] = vertices_spine[new_position] 
    for i in range(spine -1,spine_middle,-1):
        change = (i-spine_middle)
        new_position = (spine_middle + math.floor(change*compress_spine_bottom))
        print(i," > middle  , change = ",change,"   new = ",new_position)
        vertices_spine[i] = vertices_spine[new_position] 
            
              
    # $$$ Rotation Ends $$$        
        
    ##  CREATE THE MESH ##
    
    bm = bmesh.new()
    verts = [(element['x'],element['y'],element['z']) for element in vertices]
    verts = verts + [(element['x'],element['y'],element['z']) for element in vertices_spine]
    
    cases = {1:(3,5), 2:(5,8), 3:(8,13), 4:(13,21), 5:(21,34)}  
    faces = [{2,5,1},{2,4,1},{3,5,1}] # to start you off as all inherit 2/3
    
                
    for x in cases: # add 1 more block of traingles for each larger spiral, inheriting all lower additions
        
        match cases[x][1]: # to deal with triangles with poor normals still not fully corrected on higher parastichies
            case 34:
                reject = [55,76,5,8,16]
            case 21:
                reject = [29,42,5,8,0]
            case 13:
                reject = [16,24,0,0,0]
            case _:
                reject = [0,0,0,0,0]
        
        if (cases[x][1] <= spiral_b):
            for i in range(cases[x][1]+1,cases[x][0]+cases[x][1]+1):
                if i  > reject[0]:
                    try:
                        faces = faces+[(i-cases[x][0],i,i-cases[x][1])] # triangles towards middle
                    except:
                        continue
                print (reject)
                
    
    match spiral_b: # to deal with triangles with poor normals
            case 34:
                reject = [55,76,5,8,16]
            case 21:
                reject = [29,42,5,8,0]
            case 13:
                reject = [16,24,0,0,0]
            case _:
                reject = [0,0,0,0,0]
    
    # Add faces missing in higher parastichies            
    for i in range (6 , 17):
        if i > reject[2] and i <= reject[3]:
            faces = faces+[(i-5,i,i+8)]
        if i > reject[3] and i <= reject[4]:
            faces = faces+[(i-8,i,i+13)]
                
    
    #for i in range((spiral_b+spiral_a+1),point_number+1):
    if reject[0] == 0:
        start = spiral_b+spiral_a+1
    else:
        start = reject[1] +1
    for i in range(start,point_number+1):
        if (face_shape =="Quad"):
            try: # Make Quadrilaterals
                faces =faces + [(i-spiral_b,i,i-spiral_a,i-spiral_b-spiral_a)] #quads further out
            except:
                continue
        else:
            if (face_shape =="Horiz"):    
                try: # or try Horizontal Triangles
                    faces =faces + [(i-spiral_b,i,i-spiral_a)]
                    faces =faces + [(i-spiral_a,i-spiral_b-spiral_a,i-spiral_b)]
                except:
                    continue
            else:
                try: # or even try Vertical Triangles
                    faces =faces + [(i-spiral_b,i,i-spiral_b-spiral_a)]
                    faces =faces + [(i,i-spiral_a,i-spiral_b-spiral_a)]
                except:
                    continue
    if reject[0] > 0:
        for i in range (spiral_b+spiral_a+1,reject[1]+1):
            faces = faces + [(i-spiral_b-spiral_a,i-spiral_a-spiral_a,i-spiral_b)]
            faces = faces + [(i-spiral_a-spiral_a,i-spiral_b,i-spiral_a)]
            faces = faces + [(i-spiral_b,i-spiral_a,i)]
    
    # Fill in the base with triangles
    
    for i in range (0,spiral_a):
        v = point_number-i
        try:
            faces=faces+[(v,v-spiral_a,0)]
            faces=faces+[(v,v-spiral_b,0)]
        except:
            continue
    for i in range (0,(spiral_b-spiral_a)):
        v = point_number-i-spiral_a
        try:
            faces=faces+[(v,v-spiral_a,0)]
        except:
            continue
            
    edges = []
    for i in range (point_number+2,point_number*2+1):
        edges = edges + [(i,i+1)]
    
    
        

    mesh_name = spiral_name
    mesh_data = bpy.data.meshes.new(mesh_name)
    mesh_data.from_pydata(verts, edges, faces)

    # Load bMesh with mesh data.
    bm = bmesh.new()
    bm.from_mesh(mesh_data)
    bm.to_mesh(mesh_data)
    bm.free()
    mesh_obj = bpy.data.objects.new(mesh_data.name, mesh_data)
    mesh_name_mapping[mesh_data.name] = mesh_obj
    bpy.context.collection.objects.link(mesh_obj)
    
    # Select just the added object so you can correct the normals
    bpy.ops.object.select_all(action='DESELECT') # deselect everything
    bpy.data.objects[mesh_obj.name].select_set(True) #to select the object in the 3D viewport,
    bpy.context.view_layer.objects.active = bpy.data.objects[mesh_obj.name]# to set the object active
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False) # correct normals
    bpy.ops.object.mode_set(mode='OBJECT')

    
    

class ADD_SPIRAL(Operator, AddObjectHelper):
    """Create a new Phyllotactic Dome"""
    bl_idname = "curve.add_phyllotactic_dome"
    bl_label = "Add Phyllotactic Dome"
    bl_options = {'REGISTER', 'UNDO'}


    #These are the user variables

    # Name
    spiral_name: bpy.props.StringProperty(
        name="Name",
        description ="A name to store the mesh under",
        default = "Phyllotactic Spiral",
    ) 
    
    # parastichy number ie how many spiral in each direction
    parastichy: bpy.props.EnumProperty(
        name="Parastichy",
        description ="Spiral pattern numbers",
        items =[('OP1','2/3',''),
            ('OP2','3/5',''),
            ('OP3','5/8',''),
            ('OP4','8/13',''),
            ('OP5','13/21',''),
            ('OP6','21/34',''),
        ]
    ) 
    # quads or triangles
    quads: bpy.props.EnumProperty(
        name="Faces",
        description ="All Triangles or Quads and Triangles",
        items =[('OP1','Quads and Triangles',''),
            ('OP2','Horizontal Triangles',''),
            ('OP3','Vertical Triangles',''),    
        ]   
    ) 
    # number of elements in spiral
    point_number: bpy.props.IntProperty(
        name="Vertex Count",
        description ="Number of Vertices",
        min=5, max =10000,
        default = 100,
    ) 
    # maximum diameter of spiral as easier to input
    full_diameter: FloatProperty(
        name="Diameter",
        description ="Diameter of Dome",
        min=0.0001, max =1000.0,
        default = 1.0,
    ) 
    # dome height 
    dome: FloatProperty(
        name="Height",
        description ="Dome as Factor of Radius",
        min=0.001, max =1000.0,
        default = 2.0,
    )
    # highest place at which the width is at the maximum (bulge point). 0 = base, 1 = top
    flat_width_high: FloatProperty(
        name="Flat sSection Top",
        description ="Top Height of Flattened Section",
        min=0.01, max =0.98,
        default = 0.55,
    )  
    # lowest place at which the width is at the maximum (bulge point). 0 = base, 1 = top
    flat_width_low: FloatProperty(
        name="Flat Section bottom",
        description ="bottom Height of Flattened Section",
        min=0.01, max =.98,
        default = 0.45,
    )
    # base width as proportion of maximum width. 0 = no width, 1 = same width
    base_width: FloatProperty(
        name="base Width",
        description ="Width at base",
        min=0.0, max =1.0,
        default = 0.8,
    )
    # depression at apex. 1 = full width
    depression_width: FloatProperty(
        name="Top Dimple Width",
        description ="Width of Top Depression",
        min=0.0, max =1.0,
        default = 0.0,
    )
    # how deep it goes . 0 = none, 1= all the way
    depression_depth: FloatProperty(
        name="Top Dimple Depth",
        description ="Depth of Top Depression",
        min=0.0, max =1.0,
        default = .00,
    )
    # how far it leans . 0 = none, 45= all the way
    degrees_over: IntProperty(
        name="Lean (degrees)",
        description ="How far it leans over",
        min=-720, max =720,
        default = 0,
    )
    # Base Twist (0-60 degrees)
    base_twist: IntProperty(
        name="Base Shear Angle",
        description ="The angle the shear is applied",
        min=0, max =90,
        default = 0,
    )
    # Base Twist Height
    base_twist_height: FloatProperty(
        name="Base Shear Height",
        description ="How high the base offset influences",
        min=-2.0, max =2.0,
        default = 0,
    )
    # Base Twist Lateral
    base_twist_lateral: FloatProperty(
        name="Base Shear Lateral",
        description ="Where side to side the base shift rotates around",
        min=-2.0, max =2.0,
        default = 0,
    )
    # Base Twist Factor
    base_twist_factor: IntProperty(
        name="Base Shear Factor",
        description ="Affects Shear Dropoff",
        min=1, max =6,
        default = 1,
    )
    # Reverse the drop/rotate action
    reset_drop: BoolProperty(
        name="See Rotation Point",
        description ="Put Item back to original orientation",
        default = False,
    )
    # Jitter Factor
    jitter: FloatProperty(
        name="Jitter Factor",
        description ="Jitters Vertices",
        min=0.0, max =10.0,
        default = 0.0,
    )
    # squash in the base - more vertices per height
    make_tighter: FloatProperty(
        name="Tighten Base",
        description ="Compresses base section",
        min=0.1, max =10.0,
        default = 1,
    )
    # compress the spine to stop cone eloingating
    compress_spine_top: FloatProperty(
        name="Compress Spine Top",
        description ="compress the internal spine",
        min=0.1, max =1,
        default = 1,
    )
    # compress the spine to stop cone eloingating
    compress_spine_bottom: FloatProperty(
        name="Compress Spine Bottom",
        description ="compress the internal spine",
        min=0.1, max =1,
        default = 1,
    )


    def execute(self, context):
        
        add_spiral(self, context,
            self.spiral_name,self.parastichy,self.quads,
            self.full_diameter,
            self.point_number,self.dome,self.flat_width_high,
            self.flat_width_low,self.base_width,
            self.depression_width,self.depression_depth,
            self.degrees_over,
            self.base_twist,
            self.base_twist_height,self.base_twist_lateral,
            self.base_twist_factor,self.reset_drop,
            self.jitter,self.make_tighter,
            self.compress_spine_top,self.compress_spine_bottom
        )

        return {'FINISHED'}


# Registration

def add_spiral_button(self, context):
    self.layout.operator(
        ADD_SPIRAL.bl_idname,
        text="Add Phyllotactic Dome",
        icon='PLUGIN')


# This allows you to right click on a button and link to documentation
def add_spiral_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_spiral", "scene_layout/object/types.html"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(ADD_SPIRAL)
    bpy.utils.register_manual_map(add_spiral_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_spiral_button)


def unregister():
    bpy.utils.unregister_class(ADD_SPIRAL)
    bpy.utils.unregister_manual_map(add_spiral_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_spiral_button)


if __name__ == "__main__":
    register()
