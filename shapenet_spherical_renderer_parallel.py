
import argparse
import os
import sys
import json

sys.path.append(os.path.dirname(__file__))

import util
import blender_interface


def main():
    p = argparse.ArgumentParser(description='Batched rendering of spherical views of given 3D models in *.obj, *.ply or *.gltf format by rotating a camera around it.')
    p.add_argument('--batch_file', type=str, required=True, help='Path to JSON file containing files to process.')
    p.add_argument('--batch_id', type=int, required=True, help='ID to identify the current batch job.')
    p.add_argument('--config', type=str, required=True, help='Path to JSON config file for dataset.')

    argv = sys.argv[sys.argv.index("--") + 1:]
    opt = p.parse_args(argv)

    print(opt)

    # open the batch file
    with open(opt.batch_file, 'r') as f:
        batch = json.load(f)

    # root path for batch files
    fp = batch['root_path']

    # collect all the files to process
    print(batch['files'][opt.batch_id])
    instances = [f for f in batch['files'][opt.batch_id] if util.is_allowed_type(f)]
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
