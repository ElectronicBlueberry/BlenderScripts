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

class ClickPlacer(bpy.types.Operator):
	bl_idname = "object.click_placer"
	bl_label = "Click Placer"
	bl_options = {'REGISTER', 'UNDO'}

	# todo: interface
	rotate_to_nomal: bpy.props.BoolProperty(
		name = "Rotate to Normal",
		description = "Rotate the new object for z-up to align to the surface normal.",
		default = False
	)

	def invoke(self, context, event):
		if context.object:
			mouse_pos = [event.mouse_region_x, event.mouse_region_y]

			viewport_region = context.region
			viewport_region_data = context.space_data.region_3d
			viewport_matrix = viewport_region_data.view_matrix.inverted()
			
			ray_start = viewport_matrix.to_translation()
			ray_depth = viewport_matrix @ Vector((0,0,-1000))
			
			ray_end = view3d_utils.region_2d_to_location_3d(viewport_region,viewport_region_data, mouse_pos, ray_depth )
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

			if self.rotate_to_nomal:
				z = Vector((0, 0, 1))
				rot = z.rotation_difference( self.cast[2] ).to_euler()
				self.new_obj.rotation_euler = rot

		return {'FINISHED'}


def register():
	bpy.utils.register_class(ClickPlacer)

def unregister():
	bpy.utils.unregister_class(ClickPlacer)

if __name__ == '__main__':
	register()