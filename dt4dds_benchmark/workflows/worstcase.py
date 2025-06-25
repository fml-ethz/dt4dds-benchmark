import dataclasses
import pathlib

from .baseworkflow import BaseWorkflow
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class WorstCase(BaseWorkflow):
    """
    Worst-case workflow assuming synthesis by electrochemical methods and amplification by a Taq-based polymerase.

    After initialization, the workflow can be used to run a simulation by calling run().    
    """
    initial_coverage: float = 50
    aging_halflives: float = 0
    sequencing_depth: float = 50

    command_path = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'workflow_worstcase' / 'run.sh')


    def _run_workflow(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))

        # add optional arguments
        if self.initial_coverage: cmd.extend(['--initial_coverage', str(self.initial_coverage)])
        if self.aging_halflives: cmd.extend(['--aging_halflives', str(self.aging_halflives)])
        if self.sequencing_depth: cmd.extend(['--sequencing_depth', str(self.sequencing_depth)])

        return SubProcess(cmd, **kwargs)