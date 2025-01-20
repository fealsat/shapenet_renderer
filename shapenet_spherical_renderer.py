import argparse
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(__file__))

import util
import blender_interface


def main():
    p = argparse.ArgumentParser(description='Renders spherical views of given 3D models in *.obj, *.ply or *.gltf format by rotating a camera around it.')
    p.add_argument('--mesh_fpath', type=str, required=True, help='File path to either a single 3D model or a directory containing 3D models.')
    p.add_argument('--config', type=str, required=True, help='Path to YAML config file for dataset.')

    argv = sys.argv
    argv = sys.argv[sys.argv.index("--") + 1:]

    opt = p.parse_args(argv)

    instances = []
    fp = opt.mesh_fpath

    # if it's a directory, collect all the files
    if os.path.isdir(opt.mesh_fpath):
        instances = [fp for fp in os.listdir(opt.mesh_fpath) if util.is_allowed_type(fp)]
    else:
        if util.is_allowed_type(p.mesh_fpath):
            instances.append(p.mesh_fpath)
            fp = os.path.dirname(p.mesh_fpath)
    if len(instances) == 0:
        raise ValueError('Input must either be a directory containing 3D model files or a path to a single 3D model file.')

    # load the config & instantiate renderer
    config = util.load_config(opt.config)
    renderer = blender_interface.BlenderInterface(config)

    for instance in instances:
        print(instance, fp)
        # import instance
        renderer.import_mesh(os.path.join(fp, instance))
        instance_name = os.path.splitext(os.path.basename(instance))[0]
        # sample locations for camera
        radius = renderer.fit_to_view()
        num_observations = config['num_observations']
        if config['mode'] == 'train':
            positions = util.sample_spherical(radius, num_observations)
        elif config['mode'] == 'test':
            positions = util.sample_archimedean_spiral(radius, num_observations)

        # obj_location = np.zeros((1,3))

        # cv_poses = util.look_at(cam_locations, obj_location)
        # blender_poses = [util.cv_cam2world_to_bcam2world(m) for m in cv_poses]

        # rot_mat = np.eye(3)
        # hom_coords = np.array([[0., 0., 0., 1.]]).reshape(1, 4)
        # obj_pose = np.concatenate((rot_mat, obj_location.reshape(3,1)), axis=-1)
        # obj_pose = np.concatenate((obj_pose, hom_coords), axis=0)

        renderer.render(instance_name, positions, write_cam_params=True)


if __name__ == '__main__':
    main()
