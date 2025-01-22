# ShapeNet Renderer

This project renders spherical views of 3D models in `.obj`, `.ply`, or `.gltf` formats using Blender in [headless mode](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html). It is based on Vincent Sitzmann's spherical renderer but updated for Blender 2.8+ and enhanced with several features and flexible configuration using a JSON file. Below are instructions to clone, install Blender, and run the script.

## Features

- Single file or batch rendering of directories (especially for the Shapenet dataset)
- Random sampling or Archimedean spiral (based on [this code](https://github.com/vsitzmann/shapenet_renderer/blob/master/util.py#L205))
- Automatic alignment and positioning of objects within the camera frame
- Extensive configuration to allow ambient, fixed or random sun lighting including optional shadows
- Support for ambient occlusion to mimic indirect lighting
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

| Key             | Type          | Description                                  |
|------------------|---------------|----------------------------------------------|
| `file_path`     | `string`      | Dummy. Overwritten by mesh_fpath.            |
| `out_dir`       | `string`      | Directory to store output files.             |
| `num_observations` | `integer`  | Number of observations to sample.           |
| `mode`          | `string`      | Mode of operation (`test`, `train`). `test` uses Archimedean spiral, `train` samples randomly.   |
| `object`        | `object`      | Object-related settings.                     |
| `lighting`      | `object`      | Lighting configuration.                      |
| `rendering`     | `object`      | Rendering settings.                          |

---

### `object`

| Key           | Type          | Description                                  |
|---------------|---------------|----------------------------------------------|
| `scale`       | `integer`     | Scale factor for the object.                 |
| `center_mode` | `string`      | Vertical centering mode for the object (`mean`, `min`).|

---

### `lighting`

| Key             | Type          | Description                                  |
|------------------|---------------|----------------------------------------------|
| `enable`        | `boolean`     | Enable or disable lighting.                  |
| `is_random`     | `boolean`     | Enable random lighting. If false, the `rotation_euler_y` and `rotation_euler_z` values are used.                     |
| `sun_light`     | `object`      | Sunlight-related settings.                   |
| `ambient_light` | `array[float]`| Ambient light color in RGBA format.          |

#### `lighting.sun_light`

| Key                  | Type          | Description                                  |
|-----------------------|---------------|----------------------------------------------|
| `rotation_euler_y`   | `float`       | Y-axis rotation of the sunlight (in radians).|
| `rotation_euler_z`   | `float`       | Z-axis rotation of the sunlight (in radians).|
| `energy`             | `float`       | Energy intensity of the sunlight.            |
| `radius`             | `float`       | Radius of the sunlight source.               |
| `use_shadow`         | `boolean`     | Enable or disable sunlight shadows.          |
| `contact_shadow`     | `object`      | Contact shadow settings for sunlight. Only Blender <4.2.        |
| `cascade_count`      | `integer`     | Number of cascades for shadow mapping. Only Blender <4.2.      |
| `cascade_max_distance` | `float`     | Maximum cascade distance for shadow mapping. Only Blender <4.2. |

#### `lighting.sun_light.contact_shadow`

| Key         | Type          | Description                                  |
|-------------|---------------|----------------------------------------------|
| `distance`  | `float`       | Maximum distance for contact shadows. Only Blender <4.2.        |
| `thickness` | `float`       | Thickness of contact shadows. Only Blender <4.2.                |

---

### `rendering`

| Key                 | Type          | Description                                  |
|----------------------|---------------|----------------------------------------------|
| `use_exr`           | `boolean`     | Save rendering outputs in EXR format. Stores RGBA, normals and depth.      |
| `camera`            | `object`      | Camera-related settings.                    |
| `shadow`            | `object`      | Shadow configuration.                       |
| `ao`                | `object`      | Ambient occlusion settings.                 |
| `color_management`  | `object`      | Color management settings.                  |

#### `rendering.camera`

| Key    | Type      | Description                                  |
|--------|-----------|----------------------------------------------|
| `width` | `integer` | Width of the rendered image.                |
| `height` | `integer` | Height of the rendered image.              |
| `fov`   | `float`   | Field of view of the camera (in radians).   |

#### `rendering.shadow`

| Key             | Type      | Description                                  |
|------------------|-----------|----------------------------------------------|
| `cascade_size`  | `string`  | Shadow map cascade size (e.g., `4096`). Only Blender <4.2.    |
| `use_soft_shadows` | `boolean` | Enable or disable soft shadows. Only Blender <4.2.       |

#### `rendering.ao`

| Key                | Type      | Description                                  |
|---------------------|-----------|----------------------------------------------|
| `enable`           | `boolean` | Enable or disable ambient occlusion.        |
| `distance`         | `float`   | Maximum distance for ambient occlusion. Only Blender <4.2.     |
| `use_bounce`       | `boolean` | Enable or disable bounce lighting. Only Blender <4.2.          |
| `use_bent_normals` | `boolean` | Enable or disable bent normals. Only Blender <4.2.         |

#### `rendering.color_management`

| Key             | Type      | Description                                  |
|------------------|-----------|----------------------------------------------|
| `view_transform` | `string`  | View transform for color management (e.g., `AgX`, `Filmic`, `None`). |
| `look`           | `string`  | Color grading look (e.g., `AgX - Base Contrast`). |

--- 

This documentation organizes the configuration for easy reference and implementation.
