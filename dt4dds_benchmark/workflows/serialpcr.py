import dataclasses
import pathlib

from .baseworkflow import BaseWorkflow
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class SerialPCR(BaseWorkflow):
    """
    XXX

    After initialization, the workflow can be used to run a simulation by calling run().    
    """
    n_pcrs: int = 5

    command_path = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'workflow_serialpcr' / 'run.sh')


    def _run_workflow(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))

        # add optional arguments
        if self.n_pcrs: cmd.extend(['--n_pcrs', str(self.n_pcrs)])

        return SubProcess(cmd, **kwargs)