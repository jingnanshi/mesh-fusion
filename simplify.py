import os
import argparse
import common
import pymeshlab

class Simplification:
    """
    Perform simplification of watertight meshes.
    """

    def __init__(self, parse_args=True, options=None):
        """
        Constructor.
        """

        parser = self.get_parser()
        if parse_args:
            self.options = parser.parse_args()
        else:
            self.options = options

        self.simplification_script = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'simplification.mlx')

    def get_parser(self):
        """
        Get parser of tool.

        :return: parser
        """

        parser = argparse.ArgumentParser(description='Scale a set of meshes stored as OFF files.')
        parser.add_argument('--in_dir', type=str, help='Path to input directory.')
        parser.add_argument('--out_dir', type=str, help='Path to output directory; files within are overwritten!')
        parser.add_argument('--filetype', type=str, help='What filetype to export.', default="obj")

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
        Run simplification.
        """

        assert os.path.exists(self.options.in_dir)
        common.makedir(self.options.out_dir)
        files = self.read_directory(self.options.in_dir)

        for filepath in files:
            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(filepath)
            ms.load_filter_script(self.simplification_script)
            ms.apply_filter_script()
            bname = os.path.basename(filepath).split('.')[0]
            ms.save_current_mesh(os.path.join(self.options.out_dir, bname+"."+self.options.filetype))

            #os.system('meshlabserver -i %s -o %s -s %s' % (
            #    filepath,
            #    os.path.join(self.options.out_dir, ntpath.basename(filepath)),
            #    self.simplification_script
            #))

if __name__ == '__main__':
    app = Simplification()
    app.run()
