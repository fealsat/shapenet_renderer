# ShapeNet Renderer

This project renders spherical views of 3D models in `.obj`, `.ply`, or `.gltf` formats using Blender
in [headless mode](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html). It is based on Vincent
Sitzmann's spherical renderer but updated for Blender 2.8+ and enhanced with several features and flexible configuration
using a JSON file. Below are instructions to clone, install Blender, and run the script.

## Features

- Single file or batch rendering of directories (especially for the Shapenet dataset)
- Random sampling or Archimedean spiral (based
  on [this code](https://github.com/vsitzmann/shapenet_renderer/blob/master/util.py#L205))
- Automatic alignment and positioning of objects within the camera frame
- Mono-, bi- and trinocular camera setups are supported with optional tangential offset
- Extensive configuration to allow ambient, fixed or random sun lighting including optional shadows
- Support for ambient occlusion to mimic indirect lighting
- Support for image-based lighting using HDR / EXR images
- Different view transforms to allow for better color management (can avoid overexposure of models)

## Usage

To clone this repository, use the following command:

```bash
git clone https://github.com/fealsat/shapenet_renderer.git
cd shapenet_renderer
blender -b --python shapenet_spherical_renderer.py -- --mesh_fpath <your_model_path> --config <your_config_file.json>
```

### Blender Installation

The script uses Blender for rendering. Follow the instructions below to install Blender on your system:
Download Blender from the [Blender Download Page](https://www.blender.org/download/).

---

## Config file parameters

| Key                | Type     | Description                                                                   |
|--------------------|----------|-------------------------------------------------------------------------------|
| `file_path`        | `string` | Dummy. Overwritten by `--mesh_fpath`.                                         |
| `out_dir`          | `string` | Directory to store output files.                                              |
| `num_observations` | `int`    | Number of observations to sample.                                             |
| `mode`             | `string` | Mode of operation (`test` uses Archimedean spiral, `train` samples randomly). |
| `object`           | `object` | Object-related settings.                                                      |
| `lighting`         | `object` | Lighting configuration.                                                       |
| `rendering`        | `object` | Rendering settings.                                                           |

---

### `object`

| Key           | Type      | Description                                               |
|---------------|-----------|-----------------------------------------------------------|
| `scale`       | `float`   | Scale factor for the object.                              |
| `center_mode` | `string`  | Vertical centering mode for the object (`mean`, `min`).   |
| `normalize`   | `boolean` | Normalize object dimensions to unit scale before scaling. |

---

### `lighting`

| Key                | Type           | Description                                |
|--------------------|----------------|--------------------------------------------|
| `enable`           | `boolean`      | Enable or disable lighting.                |
| `is_random`        | `boolean`      | Enable random lighting orientation.        |
| `ibl`              | `object`       | Image-based lighting (HDRI) configuration. |
| `sun_light`        | `object`       | Sunlight-related settings.                 |
| `ambient_light`    | `array[float]` | Ambient light RGBA color.                  |
| `background_color` | `array[float]` | Background color in RGBA format.           |

#### `lighting.ibl`

| Key                | Type      | Description                                                              |
|--------------------|-----------|--------------------------------------------------------------------------|
| `enable`           | `boolean` | Enable or disable image-based lighting (IBL).                            |
| `directory`        | `string`  | Directory containing HDRI environment maps.                              |
| `file_path`        | `string`  | Path to a specific HDRI file (overridden by random selection if random). |
| `random_rotation`  | `boolean` | Randomly rotate HDRI environment map.                                    |
| `rotation_euler_z` | `float`   | Fixed Z-axis rotation for HDRI (if `random_rotation` is false).          |

#### `lighting.sun_light`

| Key                    | Type      | Description                                          |
|------------------------|-----------|------------------------------------------------------|
| `rotation_euler_y`     | `float`   | Y-axis rotation of the sunlight (in radians).        |
| `rotation_euler_z`     | `float`   | Z-axis rotation of the sunlight (in radians).        |
| `energy`               | `float`   | Energy/intensity of sunlight.                        |
| `radius`               | `float`   | Radius of the sunlight source.                       |
| `use_shadow`           | `boolean` | Whether sunlight should cast shadows.                |
| `contact_shadow`       | `object`  | Contact shadow settings (for Blender versions <4.2). |
| `cascade_count`        | `int`     | Number of shadow map cascades.                       |
| `cascade_max_distance` | `float`   | Max distance for shadow cascade coverage.            |

#### `lighting.sun_light.contact_shadow`

| Key         | Type    | Description                           |
|-------------|---------|---------------------------------------|
| `distance`  | `float` | Maximum distance for contact shadows. |
| `thickness` | `float` | Shadow thickness for contact points.  |

---

### `rendering`

| Key                | Type      | Description                                                                     |
|--------------------|-----------|---------------------------------------------------------------------------------|
| `use_exr`          | `boolean` | Save rendered images in EXR format with multiple passes (RGBA, normals, depth). |
| `use_mvs`          | `boolean` | Enable rendering from multiple camera views for MVS-style output.               |
| `mvs`              | `array`   | List of camera offset vectors for stereo or trinocular setups.                  |
| `distance_offset`  | `float`   | Metric offset to push the camera further away from objects at the center.       |
| `camera`           | `object`  | Camera configuration settings.                                                  |
| `shadow`           | `object`  | Shadow-related settings.                                                        |
| `ao`               | `object`  | Ambient occlusion (AO) configuration.                                           |
| `fog`              | `object`  | Volumetric fog settings.                                                        |
| `color_management` | `object`  | View transform and grading look.                                                |

#### `rendering.camera`

| Key      | Type    | Description                               |
|----------|---------|-------------------------------------------|
| `width`  | `int`   | Width of the output image (in pixels).    |
| `height` | `int`   | Height of the output image (in pixels).   |
| `fov`    | `float` | Field of view of the camera (in radians). |

#### `rendering.shadow`

| Key                | Type      | Description                                                     |
|--------------------|-----------|-----------------------------------------------------------------|
| `cascade_size`     | `string`  | Shadow map resolution size (e.g., `"4096"`). Only Blender <4.2. |
| `use_soft_shadows` | `boolean` | Enable soft shadows (PCF filtering). Only Blender <4.2.         |

#### `rendering.ao`

| Key                | Type      | Description                                                 |
|--------------------|-----------|-------------------------------------------------------------|
| `enable`           | `boolean` | Enable ambient occlusion.                                   |
| `distance`         | `float`   | AO influence radius. Only Blender <4.2.                     |
| `use_bounce`       | `boolean` | Simulate indirect lighting with bounces. Only Blender <4.2. |
| `use_bent_normals` | `boolean` | Use bent normals for better AO shading. Only Blender <4.2.  |

#### `rendering.fog`

| Key      | Type           | Description                                              |
|----------|----------------|----------------------------------------------------------|
| `enable` | `boolean`      | Enable or disable volumetric fog.                        |
| `preset` | `string`       | Fog quality preset (`low`, `medium`, `high`).            |
| `gamma`  | `array[float]` | Per-channel gamma adjustment for fog color (\[R, G, B]). |

#### `rendering.color_management`

| Key              | Type     | Description                                           |
|------------------|----------|-------------------------------------------------------|
| `view_transform` | `string` | View transform (e.g., `AgX`, `Filmic`, `Standard`).   |
| `look`           | `string` | Look or grading preset (e.g., `AgX - Base Contrast`). |

---