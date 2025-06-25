import time
import pathlib
import dataclasses

from ..tools import Step

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class BaseClustering(Step):
    """ Abstract class for clustering. To be overridden by actual clustering implementations as a subclass. """

    def __post_init__(self):
        super().__post_init__()
        self._class = 'Clustering'

    # 
    # public methods
    # 

    def run(self, input_file: pathlib.Path, output_file: pathlib.Path, **kwargs):
        """ Cluster the sequences in the input file and write the clustered sequences to the output file. Returns the metadata of the process. """
        
        logger.info(f"Clustering {input_file} into {output_file} with {self}.")
        start = time.time()

        try:
            process = self._run_clustering(pathlib.Path(input_file), pathlib.Path(output_file), **kwargs)
            return process.metadata
        except Exception as e:
            logger.error(f"Clustering failed with {e}")
            raise e
        finally:
            logger.info(f"Clustering {self} took {time.time()-start:.1f} seconds")


    # 
    # override these methods in the subclass
    # 

    def _run_clustering(self, input_file: pathlib.Path, output_file: pathlib.Path, **kwargs):
        """ To be override by the subclass """
        raise NotImplementedError("_run_clustering() not implemented")