import dataclasses
import pathlib

from .baseclustering import BaseClustering
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class CDHit(BaseClustering):
    """
    After initialization, the clustering can be started by calling run().    
    """
    
    command_path = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'clustering_cdhit' / 'cluster.sh')
    identity_threshold: float = None
    word_size: int = None
    threads: int = 1


    # 
    # defaults
    # 

    @classmethod
    def default(cls, **kwargs):
        """  """
        kwargs.update(identity_threshold=0.85, word_size=6)
        return cls('default', **kwargs)


    # 
    # clustering
    # 

    def _run_clustering(self, input_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(output_file.resolve()))

        # add optional arguments
        if self.identity_threshold: cmd.extend(['-c', str(self.identity_threshold)])
        if self.word_size: cmd.extend(['-n', str(self.word_size)])
        if self.threads > 1: cmd.extend(['-T', str(self.threads)])

        return SubProcess(cmd, **kwargs)