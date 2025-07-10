import os
import sys
import argparse
sys.path.append(os.path.dirname(__file__))

import util
import blender_interface


def main():
    p = argparse.ArgumentParser(description='Renders spherical views of given 3D models in *.obj, *.ply or *.gltf format by rotating a camera around it.')
    p.add_argument('--mesh_fpath', type=str, required=True, help='File path to either a single 3D model or a directory containing 3D models.')
    p.add_argument('--config', type=str, required=True, help='Path to JSON config file for dataset.')

    argv = sys.argv
    argv = sys.argv[sys.argv.index("--") + 1:]

    opt = p.parse_args(argv)

    instances = []
    fp = opt.mesh_fpath

    # if it's a directory, collect all the files
    if os.path.isdir(opt.mesh_fpath):
        instances = [fp for fp in os.listdir(opt.mesh_fpath) if util.is_allowed_type(fp)]
    else:
        if util.is_allowed_type(opt.mesh_fpath):
            instances.append(opt.mesh_fpath)
            fp = os.path.dirname(opt.mesh_fpath)
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

        renderer.render(instance_name, positions, write_cam_params=True)


if __name__ == '__main__':
    main()
