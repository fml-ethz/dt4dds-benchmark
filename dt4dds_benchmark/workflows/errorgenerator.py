import dataclasses
import pathlib

from .baseworkflow import BaseWorkflow
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class ErrorGenerator(BaseWorkflow):
    """
    Error generator to introduce pre-defined error patterns.

    After initialization, the workflow can be used to run a simulation by calling run().    
    """
    
    rate_substitutions: float = 0
    rate_deletions: float = 0
    rate_insertions: float = 0
    overall_rate: float = dataclasses.field(init=False)
    coverage: float = 20
    dropout: float = 0

    command_path = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'workflow_errorgenerator' / 'run.sh')


    @classmethod
    def from_ratio(cls, overall_rate: float, r_subs: float = 8, r_dels: float = 1.9, r_ins: float = 0.1, coverage: float = 20, dropout: float = 0):
        rate_subs = float(overall_rate) * r_subs / (r_subs + r_dels + r_ins)
        rate_dels = float(overall_rate) * r_dels / (r_subs + r_dels + r_ins)
        rate_ins = float(overall_rate) * r_ins / (r_subs + r_dels + r_ins)
        return cls(rate_substitutions=rate_subs, rate_deletions=rate_dels, rate_insertions=rate_ins, coverage=coverage, dropout=dropout)


    def __post_init__(self):
        super().__post_init__()
        self.overall_rate = self.rate_substitutions + self.rate_deletions + self.rate_insertions


    def _run_workflow(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))

        # add optional arguments
        cmd.extend(['--rate_substitutions', str(self.rate_substitutions)])
        cmd.extend(['--rate_deletions', str(self.rate_deletions)])
        cmd.extend(['--rate_insertions', str(self.rate_insertions)])
        cmd.extend(['--coverage', str(self.coverage)])
        cmd.extend(['--dropout', str(self.dropout)])

        return SubProcess(cmd, **kwargs)