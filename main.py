import os
import tempfile
import argparse
from dataclasses import dataclass
import sys
from typing import Optional
sys.path.append('./')

from scale import Scale
from fusion import Fusion
from simplify import Simplification 
from fix_frame import FixFrame

def get_temp_dir():
    # get a temperory directory
    temp_dir = tempfile.mkdtemp()
    return temp_dir


if __name__ == '__main__':
    print("Main script to handle mesh fusion")
    parser = argparse.ArgumentParser(description='Mesh Fusion')
    parser.add_argument('--in_dir', type=str, help='Path to input directory of meshes.')
    parser.add_argument('--out_dir', type=str, help='Path to output directory; files within are overwritten!')
    args = parser.parse_args()

    # 1. Scaling 
    # python 1_scale.py --in_dir=examples/0_in/ --out_dir=examples/1_scaled/
    # 2. Render
    # python 2_fusion.py --mode=render --in_dir=examples/1_scaled/ --depth_dir=examples/2_depth/ --out_dir=examples/2_watertight/
    # 3. Fusion
    # python 2_fusion.py --mode=fuse --in_dir=examples/1_scaled/ --depth_dir=examples/2_depth/ --out_dir=examples/2_watertight/
    # 4. Simplify
    # python 4_simplify.py --in_dir=examples/2_watertight/ --out_dir=examples/3_out/
    # 5 Fix frame
    # python 5_fix_frame.py --in_dir=examples/3_out/ --out_dir=examples/4_fixed/

    # temperory directories
    in_dir = args.in_dir
    scaled_out_dir = get_temp_dir()
    transform_out_dir = get_temp_dir()
    depth_dir = get_temp_dir()
    water_tight_dir = get_temp_dir()
    framefix_out_dir = get_temp_dir()
    out_dir = args.out_dir

    # 1. Scaling 
    # python 1_scale.py --in_dir=examples/0_in/ --out_dir=examples/1_scaled/
    print(f"Scaling models in {in_dir} to {scaled_out_dir}")
    class Scale_options:
        in_dir = in_dir
        out_dir = scaled_out_dir
        use_max_scale = False 
        transform_out_dir = transform_out_dir
        padding = 0.1

    app_scale = Scale(parse_args=False)
    app_scale.options = Scale_options()
    app_scale.run()

    # 2. Render
    # python 2_fusion.py --mode=render --in_dir=examples/1_scaled/ --depth_dir=examples/2_depth/ --out_dir=examples/2_watertight/
    @dataclass
    class FusionConfig:
        """Configuration class for Fusion parameters."""
        # Operation mode
        mode: str = 'render'         # Operation mode: render or fuse
        in_dir: Optional[str] = None    # Path to input directory
        depth_dir: Optional[str] = None # Path to depth directory
        out_dir: Optional[str] = None   # Path to output directory
        
        # View parameters
        n_views: int = 100          # Number of views per model
        
        # Image parameters
        image_height: int = 640     # Depth image height
        image_width: int = 640      # Depth image width
        focal_length_x: float = 640 # Focal length in x direction
        focal_length_y: float = 640 # Focal length in y direction
        principal_point_x: float = 320 # Principal point location in x direction
        principal_point_y: float = 320 # Principal point location in y direction
        
        # Fusion parameters
        depth_offset_factor: float = 1.5 # Depth maps offset factor * voxel_size
        resolution: float = 256          # Resolution for fusion
        truncation_factor: float = 10    # Truncation factor * voxel_size

    print(f"Rendering models in {scaled_out_dir} to {depth_dir}")
    render_config = FusionConfig()
    render_config.in_dir = scaled_out_dir 
    render_config.depth_dir = depth_dir
    render_config.out_dir = water_tight_dir
    app_fusion = Fusion(parse_args=False, options=render_config)
    app_fusion.run()

    # 3. Fusion
    # python 2_fusion.py --mode=fuse --in_dir=examples/1_scaled/ --depth_dir=examples/2_depth/ --out_dir=examples/2_watertight/
    print(f"Fusing models in {scaled_out_dir} to {water_tight_dir}")
    fusion_config = FusionConfig()
    fusion_config.mode = 'fuse'
    fusion_config.in_dir = scaled_out_dir 
    fusion_config.depth_dir = depth_dir
    fusion_config.out_dir = water_tight_dir
    app_fusion = Fusion(parse_args=False, options=fusion_config)
    app_fusion.run()

    # 4. Fix frame
    # python 4_fix_frame.py --in_dir=examples/3_out/ --out_dir=examples/4_fixed/
    @dataclass
    class FixFrameConfig:
        in_models_dir: Optional[str] = None
        in_transform_params_dir: Optional[str] = None
        out_dir: Optional[str] = None

    print(f"Fixing frame of models in {framefix_out_dir}")
    fix_frame_config = FixFrameConfig()
    fix_frame_config.in_models_dir = water_tight_dir 
    fix_frame_config.in_transform_params_dir = transform_out_dir
    fix_frame_config.out_dir = framefix_out_dir 

    app_fix_frame = FixFrame(parse_args=False, options=fix_frame_config)
    app_fix_frame.run()

    # 5. Simplify
    # python 3_simplify.py --in_dir=examples/2_watertight/ --out_dir=examples/3_out/
    @dataclass
    class SimplifyConfig:
        in_dir: Optional[str] = None
        out_dir: Optional[str] = None

    print(f"Simplifying models in {framefix_out_dir} to {out_dir}")
    simplify_config = SimplifyConfig()
    simplify_config.in_dir = framefix_out_dir 
    simplify_config.out_dir = out_dir
    app_simplify = Simplification(parse_args=False, options=simplify_config)
    app_simplify.run()

    print(f"Done --- see output in {out_dir}")
    print(f"Simplified models in {out_dir}:")
    for file in os.listdir(out_dir):
        print(file)
