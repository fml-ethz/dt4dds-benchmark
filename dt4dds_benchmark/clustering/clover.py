import dataclasses
import pathlib

from .baseclustering import BaseClustering
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class Clover(BaseClustering):
    """
    After initialization, the clustering can be started by calling run().    
    """
    
    command_path = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'clustering_clover' / 'cluster.sh')
    read_length: int = 100
    depth: int = None
    vertical_drift: int = None
    horizontal_drift: int = None


    # 
    # clustering
    # 

    def _run_clustering(self, input_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(output_file.resolve()))
        cmd.extend(['-L', str(self.read_length)])

        # add optional arguments
        if self.depth: cmd.extend(['-D', str(self.depth)])
        if self.vertical_drift: cmd.extend(['-V', str(self.vertical_drift)])
        if self.horizontal_drift: cmd.extend(['-H', str(self.horizontal_drift)])

        return SubProcess(cmd, **kwargs)