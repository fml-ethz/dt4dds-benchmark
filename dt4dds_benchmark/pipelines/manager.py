import time
import pathlib
import pandas as pd
import bamboost
import numpy as np
import h5py
import uuid
import time

from ..analysis import Dataset

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bamboost.set_log_level('WARNING')



class BaseManager():
    """  """

    def __init__(self):
        self.overview = []
        self.results = []
        self.performance = []


    def run(self, pipelines):
        """  """
        start = time.time()
        logger.info(f"Running {len(pipelines)} pipelines.")

        # run the pipelines
        self._run(pipelines)

        # finish up
        logger.info(f"Finished running pipelines in {time.time() - start:.0f} seconds.")


    def get_current_data(self):
        """  """
        # get all the ids
        uids = [overview['id'] for overview in self.overview]

        # add all the uids to the results
        results = pd.DataFrame(self.results)
        results['id'] = uids

        # add all the uids to the performances
        performance = pd.DataFrame(self.performance)
        performance['id'] = [uid for uid in uids for _ in range(len(performance) // len(uids))]

        return Dataset(
            overview = pd.DataFrame(self.overview),
            results = results,
            performances = performance,
        )
    

    def get_data(self):
        return self.get_current_data()


    def _run(self, pipelines):
        """  """
        # iterate over the pipelines
        for i, pipeline in enumerate(pipelines):
            logger.info(f"Running pipeline: {pipeline} ({i+1}/{len(pipelines)})")
            parameters, result, performance = self._run_pipeline(pipeline)


    def _run_pipeline(self, pipeline, uid=None):

        # set the uid
        if uid is None: uid = uuid.uuid4().hex
        if pipeline.output_folder:
            pipeline.output_folder = pathlib.Path(pipeline.output_folder) / uid
            if pipeline.output_folder.exists(): raise FileExistsError(f"Output folder {pipeline.output_folder} already exists.")

        # create the overview
        overview = {'id': uid, 'status': 'Running'}
        overview.update(bamboost.common.utilities.flatten_dict(pipeline.parameters))

        # run the pipeline
        try:
            result, performance = pipeline.run()
            self.results.append(result)
            self.performance.append(performance)
            overview.update({'status': 'Finished'})
            return overview, result, performance
        except Exception as e:
            overview.update({'status': f'Failed: {str(e)}'})
            logger.exception(f"Pipeline {pipeline} failed with {e}.")
            raise e
        finally:
            self.overview.append(overview)

        

class HDF5Manager(BaseManager):

    TIMEOUT = 60

    def __init__(self, filepath):
        super().__init__()
        self.filepath = pathlib.Path(filepath)

    
    def _open(self):
        start = time.time()
        while (time.time() - start) < self.TIMEOUT:
            try:
                return h5py.File(self.filepath, 'a')
            except OSError:
                time.sleep(0.1)
        raise TimeoutError(f"Could not open file {self.filepath} after {self.TIMEOUT} seconds.")


    def _write_attributes(self, group, dictionary):
        for key, value in dictionary.items():
            if value is None:
                continue
            elif type(value) == str:
                group.attrs[key] = value
            else:
                group.attrs[key] = np.array(value)


    def _write_datasets(self, group, list_of_dictionaries):
        dictionary = {key: [d[key] for d in list_of_dictionaries] for key in list_of_dictionaries[0].keys()}
        for key, value in dictionary.items():
            group[key] = value


    def _run(self, pipelines):

        # write all of the parameters
        uuids = [uuid.uuid4().hex for _ in pipelines]
        with self._open() as f:
            for i, (uid, pipeline) in enumerate(zip(uuids, pipelines)):
                # create the overview
                overview = {'id': uid, 'status': 'Initiated'}
                overview.update(bamboost.common.utilities.flatten_dict(pipeline.parameters))
                # create the group for the pipeline
                group = f.create_group(uid)
                self._write_attributes(group, overview)

        # run the pipelines
        for i, (uid, pipeline) in enumerate(zip(uuids, pipelines)):
            # set running status
            with self._open() as f:
                f[uid].attrs['status'] = 'Running'

            # run the pipeline
            try:
                logger.info(f"Running pipeline: {pipeline} ({i+1}/{len(pipelines)})")
                parameters, result, performance = self._run_pipeline(pipeline, uid=uid)
            except Exception as e:
                # set failed status
                with self._open() as f:
                    group = f[uid]
                    group.attrs['status'] = f'Failed: {str(e)}'
                continue

            # write the results
            with self._open() as f:
                group = f.require_group(uid)
                f[uid].attrs['status'] = 'Finished'
                self._write_attributes(group.create_group('result'), result)
                self._write_datasets(group.create_group('performance'), performance)


    def get_data(self):
        if not pathlib.Path(self.filepath).exists():
            raise FileNotFoundError(f"File {self.filepath} does not exist.")
        
        # open the file
        with self._open() as f:
            uids = list(f.keys())

            # retrieve the results based on attributes
            overviews = []
            results = []
            performances = {'id': []}
            for uid in uids:
                overview = dict(f[uid].attrs)
                overviews.append(overview)

                # retrieve the result data from the attributes
                if 'result' in f[uid]:
                    result = dict(f[uid]['result'].attrs)
                    result['id'] = uid
                    results.append(result)
                
                # retrieve the performance data from the datasets
                if 'performance' in f[uid]:
                    for key in dict(f[uid]['performance']).keys():
                        if key not in performances:
                            performances[key] = []
                        performances[key].extend(list(f[uid]['performance'][key][()]))
                    performances['id'].extend([uid for _ in f[uid]['performance']['identifier'][()]])

        # return as dataset
        return Dataset(
            overview = pd.DataFrame(overviews),
            results = pd.DataFrame(results),
            performances = pd.DataFrame(performances),
        )





class BamboostManager(BaseManager):

    @classmethod
    def from_path(cls, filepath: pathlib.Path):
        return cls(bamboost.Manager(filepath))
    

    @classmethod
    def from_uid(cls, uid: str):
        return cls(bamboost.Manager.from_uid(uid))


    def __init__(self, bamboost_manager: bamboost.Manager):
        super().__init__()
        self.bamboost_manager = bamboost_manager
    

    def _run(self, pipelines):

        # register and create the simulations
        simulations = [self.bamboost_manager.create_simulation(
            parameters = pipeline.parameters,
            duplicate_action = 'r',
        ) for pipeline in pipelines]

        # iterate over the pipelines
        for i, (pipeline, sim) in enumerate(zip(pipelines, simulations)):
            # use the context manager to manage simulation state
            with sim:
                # run the pipeline
                logger.info(f"Running pipeline: {pipeline} ({i+1}/{len(pipelines)})")
                overview, result, performance = self._run_pipeline(pipeline, uid=sim.uid)

                # add the performance data to the simulation
                perf_data = sim.userdata.require_group('performance')
                for key in performance[0].keys():
                    if type(performance[0][key]) == str:
                        perf_data.add_dataset(key, np.array([p[key] for p in performance]), dtype=h5py.string_dtype())
                    else:
                        perf_data[key] = np.array([p[key] for p in performance])

                # add the result to the simulation data
                result_data = sim.userdata.require_group('result')
                for key, value in result.items():
                    result_data[key] = value

                # finish the simulation
                sim.finish_sim()


    def get_data(self):

        # retrieve the results based on attributes
        results = []
        performances = {'id': []}
        for sim in self.bamboost_manager.sims():
            uid = sim.uid
            with sim.open() as f:
                result = dict(f['userdata']['result'].attrs)
                result['id'] = uid
                results.append(result)

                # retrieve the performance data from the datasets
                for key in dict(f['userdata']['performance']).keys():
                    if key not in performances:
                        performances[key] = []
                    performances[key].extend(list(f['userdata']['performance'][key][()]))
                performances['id'].extend([uid for _ in f['userdata']['performance']['identifier'][()]])

        # return as dataset
        return Dataset(
            overview = self.bamboost_manager.df.copy(),
            results = pd.DataFrame(results),
            performances = pd.DataFrame(performances),
        )    