# Stage-mapper
### This is Stage XYMapper. Program's purpose is to enable mapping
### a sample using Thorlabs brushed motors (in my case 2x Z825B). The controllers for these motors are KDC101 
### brushed motor controllers (K-cube), however T-Cubes should also work fine with this code.
### Using manual: 1. connect the stages by USB to your computer 2. Open the program (or click reload stages button if program's already opened)
### 3. You now see the control panel: in the first column there should be listed all the stages connected to your computer (or created for virtual stages)
### There also is Add virtual stage button which adds a virtual stage to the list of connected stages, and this virtual stage functions exactly as a real one
### with a caveat that it doesnt exist. You can map with those stages, move them, identify them etc. Lower there also is Open Mapper button which as the name suggests
### opens the Mapper window. The last button is the Reload Stages button, which disconnects all the stages from your computer and re-initializes them.
### In case of virtual stages, clicking this button will destroy them and they will have to be added again.
### Column 2->...
### in each column further than 1 there is an UI for each of existing stages. 
### Mapper Plugin
### Mapper plugin has a main widget in the upper left corner - this represents the grid of points (spaced by 0.2mm) that stages can move to.
### clicking on this widget results in moving the stages to corresponding coordinates.
### This widgets purpose is to roughly choose a position, then on the main control panel you can move to exact spot you wish.
### In the lower left corner there are buttons for mapping control - start, kill and also go to 0,0 to reset your stages.
### in the lower right there are fields that you should fill with proper parameters for your liking. Those will determine the shape of your map.
### Higher there is a Refresh Grid Button which causes your specified grid of mapping points(blue) to snap to your current location.

### happy mapping :)
