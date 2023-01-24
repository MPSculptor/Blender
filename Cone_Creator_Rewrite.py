bl_info = {
    "name": "Cone Creator",
    "author": "Martin Preston",
    "version": (2,0),
    "blender": (3, 0, 0),
    "location": "PT_main_panel",
    "description": "Adds Various Cones from File Data",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

import bpy
import json
import math
import mathutils
from mathutils import  Vector, Euler, Matrix
import random

 
 
class PDProperties(bpy.types.PropertyGroup):
       
    dir_choice = bpy.utils.user_resource("SCRIPTS")
    file = dir_choice + "\\addons\\Cones.json"  
    print(file)
    
    # Opening JSON file
    f = open(file)
      
    # returns JSON object as a dictionary
    cone_data = json.load(f)

    items =[]
      
    # Iterating through the json list
    count = 1
    for i in cone_data["Cones"]:
        choice = "OP" + str(count)
        items = items + [(i["Name"], i["Name"], i["Name"]+" cone")]
        count += 1
          
    # Closing file
    f.close()  
    
    cone_choice : bpy.props.EnumProperty(
    name = "Type", 
    items = items
    ) 
    
    quantity : bpy.props.IntProperty(
    name = "quantity",    min = 1,
    max = 125,
    default =1
    )
    
    join_cone : bpy.props.BoolProperty(
    name = "join_cone",
    default =1
    )
    
 
class ADDONNAME_PT_cone_creator(bpy.types.Panel):
    bl_label = "Cone Creator"
    bl_idname = "ADDONNAME_PT_cone_creator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Cones"
 
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
                
        row = layout.row()
        row.label(text = "Please choose a Cone")
        layout.prop(mytool, "cone_choice")
        
        row = layout.row()
        row.label(text = "Qty to Create (1 to 125)")
        layout.prop(mytool, "quantity")
 
        obj = context.object
 
        row = layout.row()
        row.operator("addonname.cone_creator")
        
        row = layout.row()
        row.label(text = "Join as 1 object")
        row.prop(mytool, "join_cone")
        
 
 
class ADDONNAME_PT_add_cone(bpy.types.Operator):
    bl_label = "Add Cone"
    bl_idname = "addonname.cone_creator"
    
    
    def link_object(self, filepath):
        with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects] 

    
    def execute(self, context):
        
        # Open Master File and get location of data        
        dir_choice = bpy.utils.user_resource("SCRIPTS")
        file = dir_choice + "\\addons\\Cones.json"  
        # Opening JSON file
        f = open(file)
    
        # returns JSON object as a dictionary
        cone_data = json.load(f)
        # get the chosen cone 
        chosen_cone = bpy.context.scene.my_tool.cone_choice

        File_Dir = cone_data["Directory"]
        print(cone_data["Cones"])
        # Iterating through the json list
        for i in cone_data["Cones"]:
            if (chosen_cone == i["Name"]):
                cone_create_file = i["File"]
        # Closing file
        f.close()  
        
        #Open up the data file
        file = cone_create_file 
                
        Quantity = bpy.context.scene.my_tool.quantity
        Square_number = math.ceil(math.pow(Quantity,(1/3))) # to get sensible block of cones
        
        # *** COLLECT CONE DATA ***
        
        g = open(File_Dir+file)
        creation_data = json.load(g)
        
        Spiral_Name = creation_data["name"]
        Parastichy = creation_data["Parastichy"]
        Quads = creation_data["Faces"]
        Range_Diameter = creation_data["Diameter"]
        Range_Number = creation_data["Vertices"]
        Range_Dome = creation_data["Height"] 
        Flat_Width_High = creation_data["Flat_Side_Top"]
        Flat_Width_Low = creation_data["Flat_Side_Bottom"] 
        Base_Width = creation_data["Base_Width"]
        Depression_Width = creation_data["Depression_Width"] 
        Depression_Depth = creation_data["Depression_Depth"]
        Range_Over = creation_data["Lean"]
        Range_Twist = creation_data["Base_Shear_Angle"]
        Base_Twist_Height = creation_data["Base_Shear_Height"]
        Base_Twist_Lateral = creation_data["Base_Shear_Lateral"]
        Base_Twist_Shear = creation_data["Shear_Factor"]
        Reset_Drop = creation_data["Show_Rotation"]
        Jitter = creation_data["Jitter"]
        Make_Tighter = creation_data["Make_Tighter"]
        Compress_Spine_Top= creation_data["Compress_Spine_Top"]
        Compress_Spine_Bottom= creation_data["Compress_Spine_Bottom"]
        
        Area_Multiplier = creation_data["Area_Multiplier"]
        filepath = creation_data["File"]
        Left_Right = creation_data["Left_Right"]
        Open_Close = creation_data["Open_Close"]
        offset = creation_data["Base_Offset"]
        randomness = creation_data["Randomness"]
        freeze = creation_data["Freeze_Rotation"]
        Min_Top_Area = creation_data["Min_Top_Area"]
        Min_Top_Number = creation_data["Min_Top_Number"]
        bottom_height_adjust = creation_data["Bottom_Height_Adjust"]
        bottom_scale_factor = creation_data["Bottom_Scale_Factor"]
        
        g.close() 
        
        # Make some one time data for grid of cones spacing
        step_up = Range_Dome["High"] * 1.25 
        step_side = Range_Diameter["High"] * 1.5
                        
        # Vertical vector for getting rotation axis via dot product with normal
        Vertical = Vector((0.0,0.0,1.0))
        
        named = "Cones - " + Spiral_Name
        collections = bpy.data.collections # create a collection to hold them
        if named not in collections :
            collection = collections.new(named)
            collections[0].children.link(bpy.data.collections[named])               
        
        # *** END COLLECT CONE DATA ***
        
        # @@@ LOAD IN CONE SCALES @@@
        
        #load in pine blade - filepath from file
        self.link_object(filepath)

        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects]
        
        scale_list = []
        freeze_list =[]
        stalk_list =[]
        top = 999
        counter = 0
        print(data_to.objects)
        for n in data_to.objects:
            #object_list.append(n.name)
            print(n.name)
            if "Stalk" in n.name: # find if there is a stalk
                stalk_list.append(counter)
            elif "Top" in n.name: # or a top
                top = counter
            elif "Freeze" in n.name:
                freeze_list.append(counter)
            else: # Make list of all else as cone scales
                scale_list.append(counter)
            counter += 1                           
        
             
        # @@@ END lOAD IN CONE SCALES @@@
             
        Count =1
        
        for z in range (Square_number):
            for y in range (Square_number):
                for x in range (Square_number):
                    if (Count <= Quantity):
                        #Deal with randomness - uniform for uniform distribution float, randrange for integer
                        if Range_Diameter["High"] > Range_Diameter["Low"]:
                            Full_Diameter = random.uniform(Range_Diameter["Low"],Range_Diameter["High"])
                        else:
                            Full_Diameter = Range_Diameter["Low"]
                        print(Count,"   Diameter ", Full_Diameter)
                        if Range_Number["High"] > Range_Number["Low"]:   
                            Point_Number = random.randrange(Range_Number["Low"],Range_Number["High"])
                        else:
                            Point_Number = Range_Number["Low"]
                        if Range_Dome["Low"] < Range_Dome["High"]:
                            Dome = random.uniform(Range_Dome["Low"],Range_Dome["High"])
                        else:
                            Dome = Range_Dome["Low"]
                        if Range_Over["Low"] < Range_Over["High"]:
                            Degrees_Over = random.randrange(Range_Over["Low"],Range_Over["High"])
                        else:
                            Degrees_Over = Range_Over["Low"]
                        if Range_Twist["Low"] < Range_Twist["High"]:
                            Base_Twist = random.randrange(Range_Twist["Low"],Range_Twist["High"])
                        else:
                            Base_Twist = Range_Twist["Low"]#random close up of scales
                        if Open_Close > 0:
                            open_close = random.uniform(0,Open_Close)
                        else:
                            open_close = 0 
                        
                        
                                                
                        where = (x*step_side,y*step_side,z*step_up) # where to place cone
                            
                        
                        bpy.ops.curve.add_phyllotactic_dome(
                            spiral_name = Spiral_Name + " Cone",
                            parastichy = Parastichy,
                            quads = Quads,
                            full_diameter = Full_Diameter,
                            point_number = Point_Number,
                            dome = Dome, 
                            flat_width_high = Flat_Width_High,
                            flat_width_low = Flat_Width_Low, 
                            base_width = Base_Width,
                            depression_width = Depression_Width, 
                            depression_depth = Depression_Depth,
                            degrees_over = Degrees_Over,
                            base_twist = Base_Twist,
                            base_twist_height = Base_Twist_Height,
                            base_twist_lateral = Base_Twist_Lateral,
                            base_twist_factor = Base_Twist_Shear,
                            reset_drop = Reset_Drop,
                            jitter = Jitter,
                            make_tighter = Make_Tighter,
                            compress_spine_top = Compress_Spine_Top,
                            compress_spine_bottom = Compress_Spine_Bottom
                            )
                            
                        # Shrink it to a core and move it up a bit to hide it
                        bpy.ops.transform.resize(value = (0.01,0.01,0.01))
                        bpy.ops.transform.translate(value = (0.0,0.0,Dome/5))                       
                        Count += 1 
                        bpy.data.collections[named].objects.link(bpy.context.active_object) # add to collection
                        bpy.context.collection.objects.unlink(bpy.context.active_object) #remove from where phyllotactic_dome puts it
                        
                                                
                        # Variables to collect max min data
                        area_max = 0.0
                        area_min = 999.9
                        height_min = 999.9
                        height_max = 0
                        y_min = 999.9
                        y_max = 0
                        
                        # make a list containing the vertices in the central spine
                        # which can be accesses by an index
                        Spine_Vertices = []
                        
                        for i in bpy.context.object.data.vertices:
                            if i.index > Point_Number:
                                Spine_Vertices.append(i.co)
                                
                        Top_Position = Spine_Vertices[0]
                        Bottom_Position = Spine_Vertices[Point_Number]
                        obj = bpy.context.object.data
                        
                        Seed_Scale_List = {"Faces":[]} # initailaise dictionary
                        
                        scale_count = 0
                        for f in obj.vertices: # get each vertex
                            if f.index < Point_Number and f.index > 0:
                                Id = {} # initialise dictionary entry
                                
                                Id ["Id"] = f.index
                                
                                origin = Spine_Vertices[f.index-1]
                                Id["Origin"] = origin
                                endpoint = f.co
                                Id["Endpoint"] = endpoint
                                                   
                                face_normal = mathutils.Vector.normalized(endpoint-origin)
                                Id["Face_Normal"] = face_normal
                                magnitude = (endpoint-origin).length
                                Id["Magnitude"] = magnitude
                                if magnitude > area_max:
                                    area_max = magnitude
                                if magnitude < area_min:
                                    area_min = magnitude
                                # Find Euler
                                euler = face_normal.cross(Vertical)
                                Id["Face_Euler"] = euler
                                                     
                                Seed_Scale_List ["Faces"].append(Id)
                                scale_count += 1
                                
                        # Work out left/Right scale constants
                        scale_left = Left_Right[0]
                        scale_right = Left_Right[1]
                                                
                        obj_y = data_to.objects[scale_list[0]].dimensions[1] #length of blade
                                                   
                        counter = 0
                        
                        freeze_rotation = math.floor(freeze * Point_Number)
                        for f in Seed_Scale_List["Faces"]:
                            
                            y_scale = abs(f["Face_Euler"][1])
                            if y_scale > 0:
                                y_scale = 1 + (y_scale * (scale_right-1))
                            else:
                                y_scale = 1 + (y_scale * (scale_left-1))
                                                                          
                            scale = f["Magnitude"]/area_max
                            blade_origin = f["Origin"]
                            
                            #Choose a scale by default
                            choice  = scale_list[random.randint(0,(len(scale_list)-1))]
                                
                            bottom_rotate = 12#12
                            if counter > freeze_rotation:
                                blade_origin = (blade_origin + (save_location*bottom_height_adjust))/(bottom_height_adjust+1)
                                try:
                                    choice  = freeze_list[random.randint(0,(len(freeze_list)-1))]
                                except:
                                    print("Can't find one !")
                            else:
                                save_location = blade_origin
                                
                            blade_copy = data_to.objects[choice].copy()
                            
                            blade_copy.location = blade_origin
                            
                            # randomize scale
                            rand_x = random.uniform(1-randomness,1+randomness)
                            rand_y = random.uniform(1-randomness,1+randomness)
                            rand_z = random.uniform(1-randomness,1+randomness)
                            blade_copy.scale = (scale * rand_x, (scale*y_scale) * rand_y, (scale*y_scale) * rand_z)
                            
                            # rotation as per underlying face
                            face_normal = f["Face_Normal"]
                            normal = Vector(face_normal)
                            
                            # randomize rotation
                            normal[0] = normal[0] * random.uniform(1-randomness,1+randomness)
                            normal[1] = normal[1] * random.uniform(1-randomness,1+randomness)
                            normal[2] = normal[2] * random.uniform(1-randomness,1+randomness)
                            normal = mathutils.Vector.normalized(normal)
                            
                            #to stop rotation overshooting at top
                            reducer = f["Id"]/(scale_count/12)
                            if reducer>1:
                                reducer = 1
                            angle_plus = (math.radians(open_close)) * reducer
                            print("open_close ",open_close," f[ID] ",f["Id"], "   ",scale_count)
                            # Add in varied closing rotation
                            #Get angle of scale
                            vector_angle = math.acos(normal.dot(Vertical))
                            #open_close comes as 1 to 0 (0-90 angle
                            # use a multiplier to the angle to get a rotation
                            #print("open_close",open_close,"  Vector_angle ",math.degrees(vector_angle))
                            #close_angle = vector_angle*open_close
                            #print("close_angle ",math.degrees(close_angle))
                            normal_plus = Matrix.Rotation(angle_plus,4,f["Face_Euler"])
                            new_normal = normal_plus @ normal # face_normal
                                                        
                            # Close bottom scales more for pines
                            if counter == freeze_rotation:
                                z_rot = new_normal[2]
                                
                            #replace z component for bottom scales
                            if counter > freeze_rotation:
                                new_normal[2] = (new_normal[2] + (z_rot * (bottom_rotate-1)))/bottom_rotate
                                if new_normal[2] < 0:
                                    new_normal[2] = 0
                                                            
                            # Apply rotation to scale
                            eul = new_normal.to_track_quat('X','Z').to_euler()
                            blade_copy.rotation_euler = eul
                            
                            # Add it into the scene
                            bpy.data.collections[named].objects.link(blade_copy)
                            
                            blade_copy.select_set(True)
                            counter +=1
                            
                        if top != 999: #Add the Top
                            
                            Top_Normal = Vector((0.0,0.0,0.0))
                            for i in range (1,7):
                                f = Seed_Scale_List["Faces"][i]
                                Top_Normal = Top_Normal + f["Face_Normal"]
                            Top_Normal = Top_Normal/6
                            
                            top_copy = data_to.objects[top].copy()
                            face_normal = Top_Normal # f["Face_Normal"]
                            eul = face_normal.to_track_quat('X','Z').to_euler()
                            top_copy.location = Top_Position # f["Face_Centre"]
                            top_copy.rotation_euler = eul
                            bpy.data.collections[named].objects.link(top_copy)
                            top_copy.select_set(True)
                        
                        if len(stalk_list) != 0: #Add the Stalk
                            
                            stalk_normal = Vector((0.0,1.0,0.0))
                            #Place where last blade was, using last eul too
                            
                            #Choose random stalk
                            choice  = stalk_list[random.randint(0,(len(stalk_list)-1))]
                            stalk_copy = data_to.objects[choice].copy()
                            stalk_copy.location = Bottom_Position
                            eul = stalk_normal.to_track_quat('X','Z').to_euler()
                            stalk_copy.rotation_euler = eul
                            bpy.data.collections[named].objects.link(stalk_copy)
                            stalk_copy.select_set(True)
                           
                        
                        if bpy.context.scene.my_tool.join_cone: # Join as One cone if indicated
                            bpy.ops.object.join()
                        cone = bpy.ops.object
                        # set origin to geometry
                        cone.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                        # Move into grid space
                        bpy.ops.transform.translate(value =where) 
                        axis = ['X','Y','Z']
                        #rotate twice for interest
                        rot = random.uniform(-math.pi,math.pi)
                        choice = random.randrange(0,3)
                        axis_choice = axis[choice]
                        bpy.ops.transform.rotate(value=rot, orient_axis = axis_choice,  orient_type ='GLOBAL')
                        axis = ['X','Y','Z']
                        rot = random.uniform(-math.pi,math.pi)
                        choice = random.randrange(0,3)
                        axis_choice = axis[choice]
                        bpy.ops.transform.rotate(value=rot, orient_axis = axis_choice,  orient_type ='GLOBAL')
        # Clean up orphaned data and any unused mesh block so all left tidy                            
        bpy.ops.outliner.orphans_purge(do_recursive = True)

        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

        for block in bpy.data.materials:
            if block.users == 0:
                bpy.data.materials.remove(block)

        for block in bpy.data.textures:
            if block.users == 0:
                bpy.data.textures.remove(block)

        for block in bpy.data.images:
            if block.users == 0:
                bpy.data.images.remove(block)
            

        return {'FINISHED'}
    

classes = [PDProperties, ADDONNAME_PT_cone_creator, ADDONNAME_PT_add_cone]
 
 
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        bpy.types.Scene.my_tool = bpy.props.PointerProperty(type = PDProperties)
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bopy.types.Scene.my_tool
 
 
if __name__ == "__main__":
    register()
    
    
    
    
