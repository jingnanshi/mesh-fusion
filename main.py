import tempfile
import argparse
import sys
sys.path.append('./')
from 1_scale import Scale
from 2_fusion import Fusion
from 3_simplify import Simplification 

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
    print(args)

    # 1. Scaling 
    # python 1_scale.py --in_dir=examples/0_in/ --out_dir=examples/1_scaled/
    # 2. Render
    # python 2_fusion.py --mode=render --in_dir=examples/1_scaled/ --depth_dir=examples/2_depth/ --out_dir=examples/2_watertight/
    # 3. Fusion
    # python 3_fusion.py --mode=fusion --in_dir=examples/2_watertight/ --out_dir=examples/3_fused/
    # 4. Simplify
    # python 4_simplify.py --in_dir=examples/2_watertight/ --out_dir=examples/3_out/
    # 5 Fix frame
    # python 5_fix_frame.py --in_dir=examples/3_out/ --out_dir=examples/4_fixed/

    # 1. Scale
    class Scale_options:
        in_dir = args.in_dir
        out_dir = args.out_dir
        use_max_scale = True
        transform_out_dir = get_temp_dir()
        padding = 0.1

    app_scale = Scale(parse_args=False)
    app_scale.options = Scale_options()
    app_scale.run()

    # 2. Render
    from dataclasses import dataclass

@dataclass
class FusionConfig:
    """Configuration class for Fusion parameters."""
    # Operation mode
    mode: str = 'render'         # Operation mode: render or fuse
    in_dir: str | None = None    # Path to input directory
    depth_dir: str | None = None # Path to depth directory
    out_dir: str | None = None   # Path to output directory
    
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

app_fusion = Fusion(parse_args=False, options=FusionConfig())