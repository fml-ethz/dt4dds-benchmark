import dataclasses
import functools
import numpy as np

from .manager import BaseManager
from .basepipeline import BasePipeline

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)




@dataclasses.dataclass
class FocusVariator():

    manager: BaseManager
    pipeline: BasePipeline
    fixed_kwargs: dict
    vary_kwarg: str
    func: functools.partial
    func_kwarg: str
    vary_range: list
    output_folder: str = ''

    vary_init_values: list = None
    vary_init_n: int = 10
    vary_focus_iterations: int = 2
    vary_focus_factor: float = 2
    vary_focus_n: int = 10

    metric: str = "decoding_success"
    metric_reversed: bool = False


    def run(self):
        logger.info(f"Running focus variator with {self.vary_kwarg}:{self.func_kwarg} in {self.vary_range}.")

        # first create and run the pipelines with the initial values
        if not self.vary_init_values:
            self.vary_init_values = np.logspace(*np.log10(self.vary_range), num=self.vary_init_n)
        pipelines = [self._create_pipeline(value) for value in self.vary_init_values]
        self.manager.run(pipelines)

        # run focus iterations
        for i in range(self.vary_focus_iterations):
            logger.info(f"Starting focus iteration {i+1}/{self.vary_focus_iterations}.")
            new_points = self._verify_points(self._select_new_points())
            pipelines = [self._create_pipeline(value) for value in new_points]
            self.manager.run(pipelines)

        logger.info(f"Finished focus variator.")


    def _select_new_points(self):
        data = self.manager.get_current_data()
        df = data.combined_results

        loc = None
        if df[self.metric].max() < 1 or df[self.metric].min() > 0: 
            if df[self.metric].max() < 1:
                logger.info(f"Metric {self.metric} has never reached 1.")
                loc = "start" if self.metric_reversed else "end"
            elif df[self.metric].min() > 0:
                logger.info(f"Metric {self.metric} has never reached 0.")
                loc = "end" if self.metric_reversed else "start"
        else:
            fit = data.fit(f"{self.vary_kwarg}.{self.func_kwarg}", metric=self.metric)
            midpoint = fit.get_threshold(p=0.5)
            if not midpoint:
                logger.info(f"Estimation of logistic midpoint failed")
                loc = "all"
            elif midpoint < self.vary_range[0] or midpoint > self.vary_range[1]:
                logger.info(f"Estimate {midpoint} is outside the range {self.vary_range}.")
                if midpoint < self.vary_range[0]:
                    loc = "end" if self.metric_reversed else "start"
                else:
                    loc = "start" if self.metric_reversed else "end"

        if loc == "end":
            logger.info(f"Choosing new points at the end of the range.")
            start = max(self.vary_range[0], self.vary_range[1]/self.vary_focus_factor)
            end = self.vary_range[1]
        elif loc == "start":
            logger.info(f"Choosing new points at the start of the range.")
            start = self.vary_range[0]
            end = min(self.vary_range[1], self.vary_range[0]*self.vary_focus_factor)
        elif loc == "all":
            logger.info(f"Choosing new points across the whole range.")
            start = self.vary_range[0]
            end = self.vary_range[1]
        else:
            startpoint = min(fit.get_threshold(p=0.01), fit.get_threshold(p=0.99))
            endpoint = max(fit.get_threshold(p=0.01), fit.get_threshold(p=0.99))
            logger.info(f"Choosing new points based on the midpoint {midpoint}, startpoint {startpoint}, and endpoint {endpoint} of {self.metric}.")
            start = max(self.vary_range[0], min(midpoint/self.vary_focus_factor, startpoint))
            end = min(self.vary_range[1], max(midpoint*self.vary_focus_factor, endpoint))
        
        logger.info(f"New points will be between {start} and {end}.")
        return np.logspace(*np.log10([start, end]), num=self.vary_focus_n)

    
    def _verify_points(self, points):
        # allow for some rounding errors due to floats
        assert np.max(points) < 1.01*self.vary_range[1]
        assert np.min(points) > 0.99*self.vary_range[0]
        return points


    def _create_pipeline(self, value: float):
        kwargs = self.fixed_kwargs.copy()
        kwargs[self.vary_kwarg] = self.func(**{self.func_kwarg: value})
        if self.output_folder: 
            kwargs['output_folder'] = self.output_folder / f"{self.vary_kwarg}-{self.func_kwarg}"
        return self.pipeline(**kwargs)