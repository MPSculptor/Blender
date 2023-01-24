# Blender assets - Cones and Moss
Blender assets

I have uploaded this repository for the sole purpose of submitting my work to blender marketplace and for the assessment of what I have created.

There are a total of 10 blend files containing cone assets. Each has 8 sample cones with the exception of the Douglas Fir which contains only 2. This allowed file sizes that would upload to Github. The cones were all produced using two addons that I have created with Python scripts. 
The first addon creates a cone shape as a mesh and can be installed and used independently from the add mesh menu. It is called Phyllotactic Dome and takes a phyllotactic spiral and wraps it around a conical shape. This cone can be manipulated by adjusting its different segemnts and base to form a wide variety of cone-like solids. I intend to use this basic addon as the base point to create more natural forms such as realistic flowers. It would also lend itself well to the basis for an animal horn generator. I have uploaded this addon for you to intall and try out.
The second addon takes information read from JSON files and fashions fully formed cones from scale geometry held in separate blend files. I have currently created 10 varied cones that it will output, each with randomised variation. It is these created mesh objects that I would like to offer.
I have uploaded this addon file too in a limited form for you to try if you want. To install it requires the following process. It is a little fiddly which is why I don't plan at present to genarally release this file. 

  1) Install the unzipped 'Picea' folder in a location of your choice. open up the two JSON files ( Picea_pungens.json and Picea_abies.json ) and amend line 38 to point to your installation of the appropriate blend files.
  2) Install Cones.json in the addons folder of your Blender installation. On Windows this would be C:\Users\(your username)\AppData\Roaming\Blender Foundation\Blender\3.3\scripts\addons. Then change the directory in line 2 to point to your installation of the Picea folder.
  3) Install the Cone_Creator_Rewrite.py file as with any addon.
  4) The plugin should now work in a limited fashion so that it will produce Norway Spruce and Blue Spruce cones only. 

