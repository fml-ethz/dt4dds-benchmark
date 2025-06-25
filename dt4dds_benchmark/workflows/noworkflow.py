import dataclasses
import pathlib

from .baseworkflow import BaseWorkflow
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class NoWorkflow(BaseWorkflow):
    """
    Simple conversion of the design file to sequencing files.

    After initialization, the workflow can be used to run a simulation by calling run().    
    """

    command_path = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'workflow_none' / 'run.sh')


    def _run_workflow(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))

        return SubProcess(cmd, **kwargs)