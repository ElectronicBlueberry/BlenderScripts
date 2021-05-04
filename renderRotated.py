# --- Multi Angle Rendering Script ---
#  This script will render the current scene,
#  rotating the defined 'object' 'steps' times

#  Configure it via the 'cfg' global dict, and run the script
#  to start rendering. You can safely cancel the render at any time

#  I found simmilar solutions online, however they were all using
#  the main context to render, causing blender to freeze up during the
#  render process

#  This script executes the render in the same way as pressing
#  "render" in the ui,
#  providing a live render preview and keeping the ui responsive,
#  making it suitable for rendering complex scenes, or long animations
#  from multiple angles

#  The render results can be found in subfolders in your set output path.

cfg = {
	'object': "Armature",	# what object to rotate
	'steps': 8				# how many times to rotate (in fractions of 360°)
}

import bpy

from math import radians

# --- Globals ---

# shorthand to store the current scene
scene = bpy.context.scene

# whether a render is currently happening
rendering = False

# wheter to start the next render now
render_now = False

# whether or not render was canceled by the user
cancelled = False

# current rendering step
step = 0

# object to roate
obj = scene.objects[ cfg['object'] ]

# - inital scene settings -

# currently set output dir
output_dir = scene.render.filepath

# original auto key setting
auto_key = bpy.context.scene.tool_settings.use_keyframe_insert_auto

# original quat rotation
original_rot = obj.rotation_euler.copy()


# --- Functions ---

def render_animation():
	print(" -?- now rendering step " + str(step + 1)
		+ " of " + str(cfg['steps'])
	)

	# update output dir to include current rotation step
	scene.render.filepath = output_dir + str(step) + '\\'

	# 'INVOKE_DEFAULT' is the magic word, that causes our render
	# to be carried out in the foreground
	bpy.ops.render.render('INVOKE_DEFAULT', animation = True)


# --- Events ---

# called by blender after a render completed
def post_render(dummy):
	global rendering

	print( " -?- render " + str(step + 1) + " done")
	# signal to the event loop, that we are no longer rendering
	rendering = False

# called by blender when the user cancelles the render
def cancel_render(dummy):
	global cancelled

	print(" -!- cancelling render")
	# signal to the event loop, that the render was cancelled
	cancelled = True


# a simple event loop, to keep this script non-blocking
# reacts to changes in global varaibles
def main_loop():
	global step, rendering, render_now, cancelled

	if cancelled:
		stop()
		return None
	elif not rendering and not render_now:
		# make a 2 second pause before the next render
		# bledner sometimes failes to start the next render if we don't do this
		render_now = True
		return 2
	elif not rendering and render_now:
		# increment step count
		step += 1

		# rotate object before next loop
		rot = obj.rotation_euler
		rot[2] += radians(360.0 / cfg['steps'])
		obj.rotation_euler = rot

		# check if more renders need to be done
		if (cfg['steps'] > step):
			rendering = True
			render_now = False
			render_animation()
		else:
			stop()
			return None
	
	# loop every 1 seconds
	return 1


# --- Main ---	

def start():
	global rendering

	# register render events
	bpy.app.handlers.render_complete.append(post_render)
	bpy.app.handlers.render_cancel.append(cancel_render)

	# make sure our roation is not keyed in the timeline
	scene.tool_settings.use_keyframe_insert_auto = False

	# begin first render
	rendering = True

	render_animation()

	# register timer event
	bpy.app.timers.register(main_loop)

# cleanup work
# called if the render was completed or cancelled
def stop():
	# unregister events, so they no longer trigger
	bpy.app.handlers.render_complete.remove(post_render)
	bpy.app.handlers.render_cancel.remove(cancel_render)
	bpy.app.timers.unregister(main_loop)

	# restore inital scene settings
	scene.render.filepath = output_dir
	scene.tool_settings.use_keyframe_insert_auto = auto_key

	# reset rotation to original,
	# to avoid overrotation and floating point errors
	obj.rotation_euler = original_rot

	print("--- done ---")


# start render
if __name__ == "__main__"::
	start()
