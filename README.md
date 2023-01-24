# Blender assets - Cones and Moss
Blender assets

I have uploaded this repository for the sole purpose of submitting my work to blender marketplace and for the assessment of the resources I have created. I am fairly new to Blender and the output below represents my first foray into Python coding. My aim is to use the skills learnt here to develop an addon to produce realistic herbaceous plants 'grown' from a text file definition and a small amount of geometry. I'm interested in using code to replicate organic forms. I may work on some code to weave baskets as a training ground to working with fleshed out curves.

# Cones

There are a total of 10 blend files containing cone assets. Each has 8 sample cones with the exception of the Douglas Fir which contains only 2. This allowed file sizes that would upload to Github. The cones were all produced using two addons that I have created with Python scripts. 
The first addon creates the cone shape as a mesh and can be installed and used independently from the add mesh menu. It is called Phyllotactic Dome and takes a phyllotactic spiral and wraps it around a conical shape. This cone can be manipulated by adjusting its different segments and base to form a wide variety of cone-like solids. I intend to use this basic addon as the base point to create more natural forms such as realistic flowers. It would also lend itself well to the basis for an animal horn generator. I have uploaded this addon for you to intall and try out.

  file:- Phyllotactic_Dome_1_5.py
  
The second addon takes information read from JSON files and fashions fully formed cones from scale geometry held in separate blend files. I have currently created 10 varied cones that it will output, each with randomised variation. It is these created mesh objects that I would like to offer.
I have uploaded this addon file too in a limited form for you to try if you want. To install it requires the following rather involved process. It is a too fiddly which is why I don't plan at present to genarally release this file. ( In future I'm sure this could be streamlined, but that is not a current priority. ) 

  1) Install the unzipped 'Picea' folder in a location of your choice. open up the two JSON files contained in it ( Picea_pungens.json and Picea_abies.json ) and amend line 38 to point to your installation of the included blend files. You will also need to open up each blend file and use File > External Data > Find Missing Files to reconnect the image textures which are located in the assets folder you will have unzipped.
  2) Install Cones.json in the addons folder of your Blender installation. On Windows with Blender version 3.3 this would be C:\Users\(your username)\AppData\Roaming\Blender Foundation\Blender\3.3\scripts\addons. Then change the directory in line 2 to point to your installation of the Picea folder.
  3) Install the Cone_Creator_Rewrite.py file as with any addon.
  4) The plugin should now work in a limited fashion so that it will produce Norway Spruce and Blue Spruce cones only. The addon adds a 'Cones' tab to the 3D viewport popout menus. 
  
  files : Cone_Creator_Rewrite.py, Cones.json & Picea.zip ( In order to work this requires installation of Phyllotactic_Dome_1_5.py above )

The individual cone assets are Alder.zip, Austrian Pine.zip, Blue Spruce.zip, Douglas Fir 2.zip, European Larch.zip, Japanese Larch.zip, Maritime Pine.zip, Monterey Pine.zip, Mountain Pine 8.zip & Norway Spruce.zip
  
# Moss
The moss assets work differently from the cones above.
Each moss type is a geometry node setup that places small 'moss planes' randomly orientated and randomly selected on the vertex groups of the object they are connected too. Each 'Moss plane' is a simple shape with a moss image isolated with a transparent alpha channel mask. Hence, the effect only works well with Cycles rendering.
I have uploaded the four textures ( 3 moss and 1 fungus ) as individual files and as a combined asset. To use any of them, copy and paste my geometry into your scene to load in the geometry nodes setup and then attach the geometry node to your geometry from the Geometry Nodes workspace. Select any number of vertices from your model and assign them to the vertex group that is specified in the vertex group tab. In the modifiers tab you will see a geometry nodes section where ther will be exposed controls to give artistic control over the way the moss is sized and arranged. 

The assets are : 4 Moss Balls.zip - all assets in one file. Or the individual files : Fungus.zip, Moss_001.zip, Moss_002.zip & Moss_003.zip

