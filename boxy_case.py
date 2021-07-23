# import importlib
# import cadquery as cq
from watchy_sizes import *
import watchy_sizes

# New params
p_tolerance = 0.5
p_ledge_h = pcb_y_to_slot + pcb_slot_h # top and bottom inner "ledge"
p_strap_width = 24 + 0.5
p_strap_dia = 4.0
p_tbar_space_height = p_strap_dia + 1.0
p_tbar_hole_r = 0.5 # Radius of t-bar pin
p_under_pcb_depth = 8.0 # space for battery, etc.
p_inset_depth = pcb_t
p_flipFastener = True

#parameter definitions
p_thickness =  1.0 #Thickness of the box walls

p_outerWidth = pcb_w + 2 * p_thickness # Total outer width of box enclosure
p_outerLength = pcb_h + 2 * p_thickness #Total outer length of box enclosure
p_outerHeight = p_under_pcb_depth + p_thickness + p_inset_depth #Total outer height of box enclosure

p_sideRadius = pcb_radius #Radius for the curves around the sides of the box
p_topAndBottomRadius =  p_outerHeight * 0.6 #Radius for the curves on the top and bottom edges of the box
p_topAndBottomRadiusInner =  p_topAndBottomRadius

p_screwpostID = 2.5 #Inner Diameter of the screw post holes, should be roughly screw diameter not including threads

p_boreDiameter = 4.5 #Diameter of the counterbore hole, if any
p_boreDepth = 0.5 #Depth of the counterbore hole, if
p_countersinkDiameter = 0.0 #Outer diameter of countersink.  Should roughly match the outer diameter of the screw head
p_countersinkAngle = 90.0 #Countersink angle (complete angle between opposite sides, not from center to one side)

# Watchy model
#watchy = cq.importers.importStep('/home/gilad/sources/watchy/cases/Watchy.step')
#watchy = (watchy
#  .rotateAboutCenter((0,1,0), 180)
#  .translate((-pcb_w / 2.0 + 0.8, -pcb_h / 2.0, p_outerHeight - p_inset_depth - 0.5))
#)
#debug(watchy)

#outer shell
oshell = (cq.Workplane("XY")
  .rect(p_outerWidth,p_outerLength)
  .extrude(p_outerHeight)
)

#weird geometry happens if we make the fillets in the wrong order
if p_sideRadius > p_topAndBottomRadius:
    oshell = oshell.edges("|Z").fillet(p_sideRadius)
    oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
else:
    #oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
    #oshell = oshell.edges(cq.NearestToPointSelector((0,0,0))).fillet(p_topAndBottomRadius)
    oshell = oshell.edges("#Z and(not(>Z))").fillet(p_topAndBottomRadius)
    oshell = oshell.edges("|Z").fillet(p_sideRadius)

#inner shell
ishell = (oshell.faces("<Z").workplane(p_thickness,True)
    .rect((p_outerWidth - 2.0* p_thickness),(p_outerLength - 2.0*p_thickness - 2.0*p_ledge_h))
    .extrude((p_outerHeight - p_thickness),False) #set combine false to produce just the new boss
)
ishell = (ishell.edges("|Z")
  .fillet(p_sideRadius - p_thickness)
  .edges(cq.NearestToPointSelector((0,0,0)))
  .fillet(p_topAndBottomRadiusInner)
)

#make the box outer box
box = oshell.cut(ishell)

# Top strip hole
tbar_hole_depth = 1.5
strip_hole_y_offset = p_outerLength / 2.0 - p_strap_dia / 2.0 + 0.5
tbar_top = (cq.Workplane("ZY")
  .workplane(
    origin=(0, strip_hole_y_offset, 0), 
    offset=(-p_strap_width / 2.0))
  .circle(p_tbar_space_height)
  .extrude(p_strap_width)
  .workplane(
    origin=(0, p_outerLength / 2.0 - p_topAndBottomRadius + p_strap_dia / 2.0 + 0.5, p_strap_dia / 2.0 + 0.5), 
    offset=(-p_strap_width / 2.0 - tbar_hole_depth))
  .circle(p_tbar_hole_r)
  .extrude(p_strap_width + tbar_hole_depth * 2.0)
)

tbar_bottom = (cq.Workplane("ZY")
  .workplane(
    origin=(0, -strip_hole_y_offset, 0), 
    offset=(-p_strap_width / 2.0))
  .circle(p_tbar_space_height)
  .extrude(p_strap_width)
  .workplane(
    origin=(0, -(p_outerLength / 2.0 - p_topAndBottomRadius + p_strap_dia / 2.0 + 0.5), p_strap_dia / 2.0 + 0.5), 
    offset=(-p_strap_width / 2.0 - tbar_hole_depth))
  .circle(p_tbar_hole_r)
  .extrude(p_strap_width + tbar_hole_depth * 2.0)
)
with_tbars = box.cut(tbar_top).cut(tbar_bottom)

# side holes (buttons, etc)
pcb_top = p_outerLength / 2.0 - p_thickness
pcb_top_to_top_button = 7.5
top_button_to_usb = 7.5
usb_to_bottom_button = 6.5
button_width  = 4.6
button_height = 2.0
usb_b_width  = 7.4
usb_b_height = 3.0

holes_left = (cq.Workplane("YZ")
  .moveTo(pcb_top - (pcb_top_to_top_button - button_height), p_outerHeight)
  .vLine(-p_inset_depth)
  .tangentArcPoint((-button_height, -button_height))
  .hLine(-button_width)
  .hLine(-(top_button_to_usb - (usb_b_height - button_height)))
  .line(-(usb_b_height - button_height), -(usb_b_height - button_height))
  .hLine(-usb_b_width)
  .line(-(usb_b_height - button_height), (usb_b_height - button_height))
  .hLine(-(usb_to_bottom_button - (usb_b_height - button_height)))
  .hLine(-button_width)
  .tangentArcPoint((-button_height, button_height))
  .vLine(p_inset_depth)
  .close()
  .extrude(-p_outerWidth / 2.0)
)

top_button_to_vib = 5.5
vib_to_bottom_button = 6.0
vib_motor_width  = 10.0
vib_motor_height = 2.8

holes_right = (cq.Workplane("YZ")
  .moveTo(pcb_top - (pcb_top_to_top_button - button_height), p_outerHeight)
  .vLine(-p_inset_depth)
  .tangentArcPoint((-button_height, -button_height))
  .hLine(-button_width)
  .hLine(-(top_button_to_vib - (vib_motor_height - button_height)))
  .line(-(vib_motor_height - button_height), -(vib_motor_height - button_height))
  .hLine(-vib_motor_width)
  .line(-(vib_motor_height - button_height), (vib_motor_height - button_height))
  .hLine(-(vib_to_bottom_button - (vib_motor_height - button_height)))
  .hLine(-button_width)
  .tangentArcPoint((-button_height, button_height))
  .vLine(p_inset_depth)
  .close()
  .extrude(p_outerWidth / 2.0)
)

with_side_holes = with_tbars.cut(holes_left).cut(holes_right)

# pcb inset
pcb_inset = (cq.Workplane("XY")
  .workplane(offset=p_outerHeight)
  .rect(pcb_w + p_tolerance, pcb_h + p_tolerance)
  .extrude(-p_inset_depth)
  .edges("|Z")
  .fillet(pcb_radius)
)
with_inset = with_side_holes.cut(pcb_inset)

# fasteners
fastener_overhang = 0.75
fastener_height = fastener_overhang + p_thickness + p_thickness
fastener_depth = p_outerHeight - p_tbar_space_height + p_thickness 
fastener_hole_point = (0, p_outerHeight * 0.75)
fastener_top_thickness = p_thickness;

fastener_top = (cq.Workplane("XY")
  .workplane(
    origin=(0, (p_outerLength / 2.0 - fastener_height / 2.0) + p_thickness, 0), 
    offset=(p_outerHeight + fastener_top_thickness + (pcb_t - p_inset_depth)))
  .rect(pcb_w * 0.5, fastener_height)
  .extrude(-fastener_depth)
  .edges("|Z or(#Z)")
  .fillet(1.0)
  .faces("#X and >X")
  .workplane(
    origin=(0, 0, 0), 
    offset=(-p_thickness))
  .rect(pcb_w , p_outerLength)
  .cutBlind(-fastener_depth)
  
  .faces("|Y and >Y")
  .workplane(origin=(0, 0, 0))
  .pushPoints( [ fastener_hole_point])
  #.cskHole(p_fastener_screw_dia, 2.0 * p_fastener_screw_dia, 82)
  .cboreHole(p_screwpostID, p_boreDiameter, p_boreDepth)
)

fastener_bottom = (cq.Workplane("XY")
  .workplane(
    origin=(0, -(p_outerLength / 2.0 - fastener_height / 2.0) - p_thickness, 0), 
    offset=(p_outerHeight + p_thickness + (pcb_t - p_inset_depth)))
  .rect(pcb_w * 0.5, fastener_height)
  .extrude(-fastener_depth)
  .edges("|Z or(#Z)")
  .fillet(1.0)
  .faces("#X and >X")
  .workplane(
    origin=(0,0,0),
    offset=(-p_thickness))
  .moveTo(p_outerWidth / 2.0,- (p_outerLength / 2.0 - (p_thickness - p_tolerance / 2.0)))
  .hLine(-p_outerWidth)
  .vLine(pcb_h * 0.5)
  .hLine(p_outerWidth)
  .close()
  .cutBlind(-fastener_depth)
)

with_fastener = (with_inset
  .union(fastener_bottom)
  .faces("|Y and >Y")
  .workplane(origin=(0, 0, 0))
  .pushPoints( [ fastener_hole_point])
  .hole(p_screwpostID, p_outerLength / 2.0)
)

if p_flipFastener:
  fastener_top_f = (fastener_top
    .translate((0, 8.0, -p_outerHeight + (fastener_height) / 2.0 + p_thickness))
    .rotateAboutCenter((1,0,0), -90)
  )
  fastener_top = fastener_top.translate((0, fastener_height, 0))
  result = (with_fastener
    .union(fastener_top_f)
    .union(fastener_top)
  )
else:
  result = with_fastener.union(fastener_top)    

#return the combined result
show_object(result)
cq.exporters.export(result, "boxy.stl")
