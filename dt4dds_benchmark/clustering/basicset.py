import dataclasses
import pathlib

from .baseclustering import BaseClustering
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class BasicSet(BaseClustering):
    """
    After initialization, the clustering can be started by calling run().    
    """
    
    command_path = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'clustering_basicset' / 'cluster.sh')


    # 
    # defaults
    # 

    @classmethod
    def default(cls, **kwargs):
        """  """
        return cls('default', **kwargs)


    # 
    # clustering
    # 

    def _run_clustering(self, input_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(output_file.resolve()))

        return SubProcess(cmd, **kwargs)