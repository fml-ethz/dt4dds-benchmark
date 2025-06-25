import dataclasses
import pathlib

from .baseclustering import BaseClustering
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class MMseqs2(BaseClustering):
    """
    After initialization, the clustering can be started by calling run().    
    """
    
    command_path = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'clustering_mmseqs2' / 'cluster.sh')
    minimum_coverage: float = None
    minimum_identity: float = None
    coverage_mode: int = None


    # 
    # clustering
    # 

    def _run_clustering(self, input_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(output_file.resolve()))

        # add optional arguments
        if self.minimum_coverage: cmd.extend(['-c', str(self.minimum_coverage)])
        if self.minimum_identity: cmd.extend(['--min-seq-id', str(self.minimum_identity)])
        if self.coverage_mode: cmd.extend(['--cov-mode', str(self.coverage_mode)])

        return SubProcess(cmd, **kwargs)