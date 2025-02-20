import os
import util
import bpy
import numpy as np


class BlenderInterface():
    def __init__(self, config):
        self.config = config

        # Delete the default cube (default selected)
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)
        bpy.ops.object.select_all(action='DESELECT')

        # Object to render
        self.obj = None
        self.scale = config['object']['scale']
        self.center_mode = config['object']['center_mode']
        # Output directory
        self.out_dir = config['out_dir']

        # Set up the camera & lighting
        self.camera = self.setup_camera_rendering()
        self.sun_light = self.setup_lighting()

        bpy.ops.object.select_all(action='DESELECT')

    # Setup camera & rendering parameters
    def setup_camera_rendering(self):
        cam = self.config['rendering']['camera']

        def fit_to_view(im_w, im_h, fov, dims):
            fov_y = 2.0 * np.arctan(np.tan(fov / 2) / (im_w / im_h))
            r = np.linalg.norm(dims) * 0.5 * 1.1
            return r / min(np.tan(fov / 2), np.tan(fov_y / 2))

        bpy.ops.object.empty_add(type='ARROWS', location=(0, 0, 0))
        empty = bpy.context.view_layer.objects.active

        bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
        bpy.context.scene.camera = bpy.data.objects["Camera"]
        camera = bpy.context.view_layer.objects.active
        camera_const = camera.constraints.new(type='TRACK_TO')
        camera_const.target = empty
        camera.data.lens_unit = 'FOV'
        camera.data.angle = cam['fov']
        bpy.context.scene.render.resolution_x = cam['width']
        bpy.context.scene.render.resolution_y = cam['height']
        bpy.context.scene.render.resolution_percentage = 100
        camera.data.sensor_height = camera.data.sensor_width # Square sensor

        # Rendering
        rendering = self.config['rendering']
        ao = rendering['ao']
        # Get version of Blender and adjust API
        version = bpy.app.version
        v_id = version[0] * 100 + version[1] * 10 + version[2]
        if v_id > 420:  # in Blender version 4.2 the API changed
            bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
            # shadows
            bpy.context.scene.eevee.use_shadows = True
            # ao
            bpy.context.scene.eevee.use_raytracing = ao['enable']
            bpy.context.scene.eevee.ray_tracing_method = 'SCREEN'
            bpy.context.scene.eevee.ray_tracing_options.resolution_scale = '1'
            bpy.context.scene.eevee.ray_tracing_options.use_denoise = True
            bpy.context.scene.eevee.use_fast_gi = ao['enable']
            bpy.context.scene.eevee.fast_gi_method = 'AMBIENT_OCCLUSION_ONLY'
            bpy.context.scene.eevee.fast_gi_resolution = '1'
        else:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE'
            # shadows
            bpy.context.scene.eevee.shadow_cascade_size = rendering['shadow']['cascade_size']
            bpy.context.scene.eevee.use_soft_shadows = rendering['shadow']['use_soft_shadows']
            # ao
            bpy.context.scene.eevee.use_gtao = ao['enable']
            bpy.context.scene.eevee.gtao_distance = ao['distance']
            bpy.context.scene.eevee.use_gtao_bent_normals = ao['use_bent_normals']
            bpy.context.scene.eevee.use_gtao_bounce = ao['use_bounce']
        bpy.context.scene.view_settings.view_transform = rendering['color_management']['view_transform']
        bpy.context.scene.view_settings.look = rendering['color_management']['look']

        return camera

    # Setup the world properties
    def setup_world_props(self, ambient_color, bg_color):
        world = bpy.context.scene.world

        world.use_nodes = True
        nodes = world.node_tree.nodes

        mix_shader = nodes.new('ShaderNodeMixShader')

        background_shader = nodes.new('ShaderNodeBackground')
        background_shader.inputs[0].default_value = bg_color

        ambient_shader = nodes.new('ShaderNodeBackground')
        ambient_shader.inputs[0].default_value = ambient_color

        weight = nodes.new('ShaderNodeLightPath')

        world.node_tree.links.new(weight.outputs['Is Camera Ray'], mix_shader.inputs[0])
        world.node_tree.links.new(ambient_shader.outputs[0], mix_shader.inputs[1])
        world.node_tree.links.new(background_shader.outputs[0], mix_shader.inputs[2])
        world.node_tree.links.new(nodes['World Output'].inputs[0], mix_shader.outputs[0])

    # Setup lighting
    def setup_lighting(self):
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 0))
        sun_light = bpy.context.view_layer.objects.active

        lighting = self.config['lighting']
        sun_lighting = lighting['sun_light']
        if lighting['enable']:
            is_random = lighting['is_random']
            sun_light.rotation_euler[1] = np.random.uniform(-np.pi / 3, np.pi / 3) if is_random else sun_lighting['rotation_euler_y']
            sun_light.rotation_euler[2] = np.random.uniform(0, 2 * np.pi) if is_random else sun_lighting['rotation_euler_z']

        sun_light.data.energy = sun_lighting['energy'] if lighting['enable'] else 0.0
        sun_light.data.use_shadow = sun_lighting['use_shadow']
        # Get version of Blender and adjust API
        version = bpy.app.version
        v_id = version[0] * 100 + version[1] * 10 + version[2]
        if v_id < 420:  # since Blender 4.2 the API became simpler
            sun_light.data.use_contact_shadow = sun_lighting['use_shadow']
            sun_light.data.contact_shadow_distance = sun_lighting['contact_shadow']['distance']
            sun_light.data.contact_shadow_thickness = sun_lighting['contact_shadow']['thickness']
            sun_light.data.shadow_cascade_count = sun_lighting['cascade_count']
            sun_light.data.shadow_cascade_max_distance = sun_lighting['cascade_max_distance']

        # bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = lighting['ambient_light']
        self.setup_world_props(lighting['ambient_light'], lighting['background_color'])

        bpy.ops.object.select_all(action='DESELECT')

        return sun_light

    def fit_to_view(self):
        intrin = self.config['rendering']['camera']
        fov = intrin['fov']
        im_w = intrin['width']
        im_h = intrin['height']
        dims = self.obj.dimensions
        fov_y = 2.0 * np.arctan(np.tan(fov / 2) / (im_w / im_h))
        r = np.linalg.norm(dims) * 0.5 * 1.1
        return r / min(np.tan(fov / 2), np.tan(fov_y / 2))

    def import_mesh(self, fpath):
        # deselect everything
        bpy.ops.object.select_all(action='DESELECT')

        ext = os.path.splitext(fpath)[-1]
        if ext == '.obj':
            bpy.ops.wm.obj_import(filepath=str(fpath))
        elif ext == '.ply':
            bpy.ops.wm.ply_import(filepath=str(fpath))
        elif ext == '.gltf':
            bpy.ops.import_scene.gltf(filepath=fpath, loglevel=50, import_shading='SMOOTH')
        # optionally scale the object
        bpy.ops.transform.resize(value=(self.scale, self.scale, self.scale))
        # join multiple objects together for simplicity
        bpy.ops.object.join()

        obj = bpy.context.view_layer.objects.active
        obj.name = os.path.basename(fpath)

        # Center the object at the origin
        v_coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
        min_x = min(co.x for co in v_coords)
        min_y = min(co.y for co in v_coords)
        if self.center_mode == 'min':
            min_z = min(co.z for co in v_coords)  # min / max, center vertically
        else:
            min_z = sum(co.z for co in v_coords) / len(v_coords)  # vertical center of mass

        offset = np.array([min_x, min_y, min_z]) + np.array(obj.dimensions) / 2
        offset[2] = min_z
        bpy.context.scene.cursor.location = offset
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        obj.location = (0, 0, 0)

        # Add Edge Split modifier
        edge_split = obj.modifiers.new('EdgeSplit', type='EDGE_SPLIT')

        util.dump(obj)

        # Adjust materials
        materials = obj.data.materials
        for m in materials:
            if m.node_tree.nodes:
                for n in m.node_tree.nodes:
                    # Check if material has metallic & roughness
                    if 'Principled BSDF' in n.name:
                        n['Metallic'] = 0.0
                        n['Roughness'] = 1.0
                    # Disable texture interpolation
                    if 'Image Texture' in n.name:
                        n.interpolation = 'Closest' 
            # Disable alpha blending
            m.blend_method = 'OPAQUE'

        self.obj = obj

        bpy.ops.object.select_all(action='DESELECT')

    def render(self, instance_name, positions, write_cam_params=False):
        bpy.context.scene.view_layers["ViewLayer"].use_pass_z = True
        bpy.context.scene.view_layers["ViewLayer"].use_pass_normal = True

        # Create the output directory
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        obj_dir = os.path.join(self.out_dir, instance_name)
        os.makedirs(obj_dir, exist_ok=True)

        im_w = bpy.context.scene.render.resolution_x
        im_h = bpy.context.scene.render.resolution_y

        if write_cam_params:
            img_dir = os.path.join(obj_dir, 'rgb')
            pose_dir = os.path.join(obj_dir, 'pose')

            util.cond_mkdir(img_dir)
            util.cond_mkdir(pose_dir)

            K = util.get_calibration_matrix_K_from_blender(self.camera.data)
            im_w = bpy.context.scene.render.resolution_x
            im_h = bpy.context.scene.render.resolution_y
            with open(os.path.join(obj_dir, 'intrinsics.txt'),'w') as intrinsics_file:
                intrinsics_file.write('%f %f %f 0.\n'%(K[0][0], K[0][2], K[1][2]))
                intrinsics_file.write('0. 0. 0.\n')
                intrinsics_file.write('1.\n')
                intrinsics_file.write('%d %d\n'%(im_h, im_w))
        else:
            img_dir = self.out_dir
            util.cond_mkdir(img_dir)

        # whether to generate EXR or not
        use_exr = self.config['rendering']['use_exr']

        bpy.context.scene.frame_set(0)
        for i, pos in enumerate(positions):
            self.camera.location = pos
            self.camera.keyframe_insert(data_path="location", frame=i)
            file_path = os.path.join(img_dir, '%06d'%i)
            # set current frame
            bpy.context.scene.frame_set(i)
            if use_exr:
                # render EXR
                bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
                bpy.context.scene.render.filepath = '{}.{}'.format(file_path, 'exr')
                bpy.ops.render.render(write_still=True)
            # render PNG
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.filepath = '{}.{}'.format(file_path, 'png')
            bpy.ops.render.render(write_still=True)

            if write_cam_params:
                # Write out camera pose
                RT = util.get_world2cam_from_blender_cam(self.camera)
                cam2world = RT.inverted()
                with open(os.path.join(pose_dir, '%06d.txt'%i),'w') as pose_file:
                    matrix_flat = []
                    for j in range(4):
                        for k in range(4):
                            matrix_flat.append(cam2world[j][k])
                    pose_file.write(' '.join(map(str, matrix_flat)) + '\n')

        bpy.data.objects.remove(self.obj)
