import time
import tempfile
import pathlib
import shutil
import dataclasses
import copy
import itertools
from typing import List, Dict

from ..tools import logs, standardize_dict

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



@dataclasses.dataclass(kw_only=True)
class BasePipeline():

    type: str = dataclasses.field(init=False)

    # main settings
    output_folder: pathlib.Path = ''        # path to the output folder, if None, a temporary folder will be used and deleted afterwards
    delete_output_folder: bool = False      # whether to delete the output folder after running the pipeline
    process_timeout: int = 1*60*60          # timeout for each process in seconds
    metadata: dict = None                   # additional metadata about the pipeline

    # file names
    filename_input: str = 'input'                   # name of the file to be encoded
    filename_sequences: str = 'sequences.txt'       # name of the file with the design sequences
    filename_reads: str = 'reads.txt'               # name of the file with the reads
    filename_clusters: str = 'clusters.txt'         # name of the file with the clustering output
    filename_output: str = 'output'                 # name of the file with the codec output
    filename_log: str = 'pipeline.log'              # name of the log file
    filename_suffix_log: str = '.log'               # suffix for log files
    filename_suffix_params: str = '_settings.yaml'  # suffix for parameter files

    # generated file paths
    filepath_input = property(lambda self: self.output_folder.resolve() / self.filename_input)
    filepath_sequences = property(lambda self: self.output_folder.resolve() / self.filename_sequences)
    filepath_reads = property(lambda self: self.output_folder.resolve() / self.filename_reads)
    filepath_clusters = property(lambda self: self.output_folder.resolve() / self.filename_clusters)
    filepath_output = property(lambda self: self.output_folder.resolve() / self.filename_output)
    filepath_log = property(lambda self: self.output_folder.resolve() / self.filename_log)

    # convenience properties
    identifier = property(lambda self: f"{self._class}:{self._type}")
    parameters = property(lambda self: standardize_dict(dataclasses.asdict(self)))


    def __post_init__(self):
        self._class = 'Pipeline'
        self.type = self.__class__.__name__


    @classmethod
    def factory(cls, 
            list_args: Dict[str, List], 
            n_iterations: int = None, 
            output_folder: pathlib.Path = None, 
            **kwargs
        ):

        # generate all possible combinations of the list arguments
        combinations = list(itertools.product(*list_args.values()))

        # create a pipeline for each combination
        pipelines = []
        for i, combination in enumerate(combinations):

            # re-pack the arguments with their keyword
            args_dict = dict(zip(list_args.keys(), combination))

            # create a pipeline for each iteration
            for i_iter in range(1, n_iterations+1) if n_iterations else [None]:

                # set up the output folder
                if output_folder:
                    title = "_".join([a.name for a in args_dict.values()]) + f"_{str(i).zfill(len(str(len(combinations))))}"
                    folder = pathlib.Path(output_folder) / title
                    if i_iter: folder = folder / str(i_iter).zfill(len(str(n_iterations)))
                else:
                    folder = ''

                # copy the kwargs for this pipeline
                ikwargs = copy.deepcopy(kwargs)

                # set the iteration number in the metadata
                metadata = ikwargs.get('metadata', {})
                if i_iter:
                    metadata['iteration'] = i_iter

                # create the pipeline
                ikwargs.update(
                    **args_dict,
                    metadata = metadata,
                    output_folder = folder,
                )
                pipelines.append(cls(**ikwargs))

        # return the pipeline instances
        logger.info(f"Generated {len(pipelines)} pipelines.")
        return pipelines


    @property
    def _pipeline(self):
        raise NotImplementedError


    def run(self):
        # check/prepare the output folder
        if self.output_folder:
            # check that the output folder does not exist yet
            self.output_folder = pathlib.Path(self.output_folder)
            if self.output_folder.exists():
                raise FileExistsError(f'Output folder {self.output_folder} already exists.')
        else:
            # create a temporary folder
            self.output_folder = pathlib.Path(tempfile.mkdtemp())
            self.delete_output_folder = True

        # set up the output folder and the logger
        self.output_folder.mkdir(parents=True, exist_ok=True)
        logs.setup_logfile(self.filepath_log, level=logger.level)

        # copy additional files
        self._prepare_files()

        # save the parameters of the pipeline
        for step, fun, input, output, identifier in self._pipeline:
            step.save_parameters(self.output_folder.resolve() / f'{identifier}{self.filename_suffix_params}')

        # run the pipeline
        start = time.time()
        self.performance = []
        try:
            return self._run_pipeline()
        except Exception as e:
            logger.exception(f"Pipeline failed with {e}.")
            raise e
        finally:
            logger.info(f"Pipeline took {time.time()-start:.0f} seconds.")

            # de-register the logger file handler
            logs.remove_logfile(self.filepath_log)

            # remove the output folder if needed
            if self.delete_output_folder:
                shutil.rmtree(str(self.output_folder.resolve()), ignore_errors=True)
                self.output_folder = None


    def _prepare_files(self):
        pass
        

    def _run_pipeline(self):
        # run each part of the pipeline, tracking where it fails
        failed_at = ""
        for step, process_call, input, output, identifier in self._pipeline:
            if not self._run_step(process_call, input, output, identifier): 
                logger.info(f"Pipeline failed at step {identifier}.")
                failed_at = identifier
                break

        # check if the pipeline was successful
        if not failed_at:
            logger.info(f"Pipeline completed.")

        # compile the pipeline results
        self.result = {
            'completed': not failed_at,
            'failed_at': failed_at,
        }
        self._customize_result(self.result)

        return self.result, self.performance

    
    def _run_step(self, process_call, input: pathlib.Path, output: pathlib.Path, identifier: str):
        # run the process
        logger.debug(f"Running {identifier}")
        performance = process_call(
            input, 
            output, 
            process_log_file = self.output_folder / (identifier + self.filename_suffix_log),
            timeout = self.process_timeout
        )

        # we measure success by the return code and whether the output file exists
        success = (performance['return_code'] == 0) and output.exists()
        if not success:
            logger.warning(f"Process {identifier} failed with return code {performance['return_code']}, output exists: {output.exists()}.")

        # include additional data in the metadata
        performance['identifier'] = identifier
        performance['success'] = success

        # save metadata
        self.performance.append(performance)

        # return success
        return performance['success']


    def _customize_result(self, results):
        pass