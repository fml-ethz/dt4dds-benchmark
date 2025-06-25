import dataclasses
import pathlib

from .baseclustering import BaseClustering
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class Starcode(BaseClustering):
    """
    After initialization, the clustering can be started by calling run().    
    """
    
    command_path = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'clustering_starcode' / 'cluster.sh')
    distance: float = None
    cluster_ratio: float = None
    spheres: bool = False
    connected_comp: bool = False
    threads: int = 1


    # 
    # clustering
    # 

    def _run_clustering(self, input_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(output_file.resolve()))

        # add optional arguments
        if self.distance: cmd.extend(['--dist', str(self.distance)])
        if self.cluster_ratio: cmd.extend(['--cluster-ratio', str(self.cluster_ratio)])
        if self.spheres: cmd.append('--sphere')
        if self.connected_comp: cmd.append('--connected-comp')
        if self.threads > 1: cmd.extend(['--threads', str(self.threads)])

        return SubProcess(cmd, **kwargs)