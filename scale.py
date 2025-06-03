import os
import pickle
import csv

import common
import argparse
import numpy as np


class Scale:
    """
    Scales a bunch of meshes.
    """

    def __init__(self, parse_args=True):
        """
        Constructor.
        """

        if parse_args:
            parser = self.get_parser()
            self.options = parser.parse_args()
        else:
            self.options = None

    def get_parser(self):
        """
        Get parser of tool.

        :return: parser
        """

        parser = argparse.ArgumentParser(description='Scale a set of meshes stored as OFF files.')
        parser.add_argument('--in_dir', type=str, help='Path to input directory.')
        parser.add_argument('--out_dir', type=str, help='Path to output directory; files within are overwritten!')
        parser.add_argument('--transform_out_dir', type=str,
                            help='Path to scale & translation parameters output directory; will overwrite files!')
        parser.add_argument('--use_max_scale', type=bool,
                            help='Set True to find the largest scale possible first, then use this scale to scale every model.')
        parser.add_argument('--padding', type=float, default=0.1, help='Relative padding applied on each side.')
        return parser

    def read_directory(self, directory):
        """
        Read directory.

        :param directory: path to directory
        :return: list of files
        """

        files = []
        for filename in os.listdir(directory):
            files.append(os.path.normpath(os.path.join(directory, filename)))

        return files

    def run(self):
        """
        Run the tool, i.e. scale all found OFF files.
        """

        assert os.path.exists(self.options.in_dir)
        common.makedir(self.options.out_dir)
        files = self.read_directory(self.options.in_dir)
        files = [f for f in files if f.endswith('.off') or f.endswith('.obj')]
        if len(files) == 0:
            raise ValueError(f"No files found in {self.options.in_dir}")

        max_size = None
        if self.options.use_max_scale:
            max_size = 0
            for filepath in files:
                mesh = common.Mesh.from_off(filepath)
                # Get extents of model.
                min, max = mesh.extents()
                total_min = np.min(np.array(min))
                total_max = np.max(np.array(max))
                c_size = total_max.item() - total_min.item(),
                if c_size[0] > max_size:
                    max_size = c_size[0]

        for filepath in files:
            if filepath.endswith('.off'):
                mesh = common.Mesh.from_off(filepath)
            elif filepath.endswith('.obj'):
                mesh = common.Mesh.from_obj(filepath)
            elif filepath.endswith('.glb'):
                mesh = common.Mesh.from_glb(filepath)
            elif filepath.endswith('.gltf'):
                mesh = common.Mesh.from_gltf(filepath)
            else:
                raise ValueError(f"Unsupported file type: {filepath}")

            # Get extents of model.
            min, max = mesh.extents()
            total_min = np.min(np.array(min))
            total_max = np.max(np.array(max))

            # Set the center (although this should usually be the origin already).
            centers = (
                (min[0] + max[0]) / 2,
                (min[1] + max[1]) / 2,
                (min[2] + max[2]) / 2
            )
            # Scales all dimensions equally.
            if self.options.use_max_scale:
                sizes = (max_size, max_size, max_size)
            else:
                sizes = (
                    total_max - total_min,
                    total_max - total_min,
                    total_max - total_min
                )
            translation = (
                -centers[0],
                -centers[1],
                -centers[2]
            )
            scales = (
                1 / (sizes[0] + 2 * self.options.padding * sizes[0]),
                1 / (sizes[1] + 2 * self.options.padding * sizes[1]),
                1 / (sizes[2] + 2 * self.options.padding * sizes[2])
            )

            mesh.translate(translation)
            mesh.scale(scales)

            print('[Data] %s extents before %f - %f, %f - %f, %f - %f' % (
                os.path.basename(filepath), min[0], max[0], min[1], max[1], min[2], max[2]))
            min, max = mesh.extents()
            print('[Data] %s extents after %f - %f, %f - %f, %f - %f' % (
                os.path.basename(filepath), min[0], max[0], min[1], max[1], min[2], max[2]))

            # May also switch axes if necessary.
            # mesh.switch_axes(1, 2)
            bname_wo_ext = os.path.basename(filepath).split(".")[0]
            mesh.to_off(os.path.join(self.options.out_dir, bname_wo_ext + ".off"))

            # dump the scale and translation to csv files
            tr_dump_path = os.path.join(self.options.transform_out_dir,
                                        os.path.basename(filepath).split(".")[0] + ".csv")
            with open(tr_dump_path, 'w') as f:
                field_names = ['scale_x', 'scale_y', 'scale_z', 'translation_x', 'translation_y', 'translation_z']
                c_dict = {'scale_x': scales[0], 'scale_y': scales[1], 'scale_z': scales[2],
                          'translation_x': translation[0], 'translation_y': translation[1],
                          'translation_z': translation[2]}

                writer = csv.DictWriter(f, fieldnames=field_names)
                writer.writeheader()
                writer.writerow(c_dict)


if __name__ == '__main__':
    app = Scale()
    app.run()