# Small Add-on By ElectronicBlueberry (Laila L.),
# to quickly place linked copies of objects in a scene.

# Press ctrl + right-click in object mode, 
# to place a linked duplicate of the active object on a surface.

# Settings under the "Tool" Tab.
# Keybindings configurable via Keymappings, just search for "Click Placer".

bl_info = {
	"name": "Click Placer",
	"description": "Place linked duplicate of active object at cursor",
	"author": "Electronic Blueberry",
	"version": (0, 1),
	"blender": (2, 92, 0),
	"category": "Object"
}

import bpy
from mathutils import Vector
from bpy_extras import view3d_utils

class ClickPlacerProperties(bpy.types.PropertyGroup):
	rotate_to_normal: bpy.props.BoolProperty(
		name =
			"Rotate to Normal",
		description =
			"Rotate the new object to align it to the surface normal.",
		default = True
	)

	up_axis: bpy.props.EnumProperty(
		items = [
			("x", "X", "X axis up."),
			("y", "Y", "Y axis up."),
			("z", "Z", "Z axis up."),
			("-x", "- X", "Negative X axis up."),
			("-y", "- Y", "Negative Y axis up."),
			("-z", "- Z", "Negative Z axis up.")
		],
		name = "Up Axis",
		description = "Axis to be considered up, when aligning object normal.",
		default = 'z',
	)

class ClickPlacerPanel(bpy.types.Panel):
	bl_idname = "click_placer.click_placer_panel"
	bl_label = "Click Placer"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Tool"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		click_placer = scene.click_placer
		
		layout.prop(click_placer, "rotate_to_normal")
		layout.prop(click_placer, "up_axis", expand = True)


class ClickPlacerOperator(bpy.types.Operator):
	bl_idname = "click_placer.click_placer_operator"
	bl_label = "Click Placer"
	bl_options = {'REGISTER', 'UNDO'}

	def invoke(self, context, event):
		if context.object:
			click_placer = context.scene.click_placer
			mouse_pos = [event.mouse_region_x, event.mouse_region_y]

			viewport_region = context.region
			viewport_region_data = context.space_data.region_3d
			viewport_matrix = viewport_region_data.view_matrix.inverted()
			
			ray_start = viewport_matrix.to_translation()
			ray_depth = viewport_matrix @ Vector((0,0,-1000))
			
			ray_end = view3d_utils.region_2d_to_location_3d(
				viewport_region,
				viewport_region_data,
				mouse_pos,
				ray_depth
			)

			ray_dir = ray_end.normalized()

			despgraph = context.evaluated_depsgraph_get()

			self.cast = context.scene.ray_cast(
				despgraph,
				origin = ray_start,
				direction = ray_dir,
				distance = 1000.0
			)

			if not self.cast[0]:
				return {'CANCELLED'}

			# linked copy
			bpy.ops.object.duplicate(
				{
					"object" : context.object,
					"selected_objects" : [context.object]
				},
				linked=True
			)

			self.new_obj = bpy.context.object
			self.new_obj.location = self.cast[1]

			if click_placer.rotate_to_normal:
				axis = Vector(axis_dict[click_placer.up_axis])
				rot = axis.rotation_difference( self.cast[2] ).to_euler()
				self.new_obj.rotation_euler = rot

		return {'FINISHED'}


classes = [
	ClickPlacerProperties,
	ClickPlacerPanel,
	ClickPlacerOperator
]

addon_keymaps = []

axis_dict = {
	"x": (1,0,0),
	"y": (0,1,0),
	"z": (0,0,1),
	"-x": (-1,0,0),
	"-y": (0,-1,0),
	"-z": (0,0,-1)
}

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	bpy.types.Scene.click_placer = bpy.props.PointerProperty(
		type = ClickPlacerProperties
	)
	
	# handle the keymap
	wm = bpy.context.window_manager

	kc = wm.keyconfigs.addon
	if kc:
		km = wm.keyconfigs.addon.keymaps.new(
			name = 'Object Mode',
			space_type = 'EMPTY'
		)
		
		kmi = km.keymap_items.new(
			ClickPlacerOperator.bl_idname,
			'RIGHTMOUSE', 'CLICK',
			ctrl = True
		)

		addon_keymaps.append((km, kmi))

def unregister():
	# handle the keymap
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

	for cls in classes:
		bpy.utils.unregister_class(cls)

	del bpy.types.Scene.click_placer

if __name__ == '__main__':
	register()