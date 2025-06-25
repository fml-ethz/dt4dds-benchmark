import dataclasses
import plotly.express as px
import pandas as pd
import numpy as np
import statsmodels.api as sm
import warnings

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def sigmoid(x, k, x0):
    return 1 / (1 + np.exp(np.clip(-k * (x - x0), -500, 500)))

def p_sigmoid(k, x0, p=0.95):
    return -1/k * np.log(1/p - 1) + x0



@dataclasses.dataclass
class DataFit():

    # required parameters
    data: pd.DataFrame
    on: str

    # optional parameters
    metric: str = 'decoding_success'
    log: bool = True
    default_threshold: float = 0.95

    # will hold the sigmoid parameters
    sigmoid_params: list = dataclasses.field(init=False)
    fit_result: dict = dataclasses.field(init=False)


    def __post_init__(self):
        self._df = self.data.loc[self.data['status'] == 'Finished'].copy()
        self._df[self.on] = self._df[self.on].astype(float)
        self._df[self.metric] = self._df[self.metric].astype(float)
        self.fit_result = self._fit()
        self.sigmoid_params = self.fit_result['params']
        self.fit_successful = self.fit_result['success']


    @property
    def threshold(self):
        return self.get_threshold(p=self.default_threshold)

    @property
    def _x(self):
        return np.log10(self._df[self.on].values) if self.log else self._df[self.on].values
    
    @property
    def _y(self):
        return self._df[self.metric].values
    

    def get_threshold(self, p=0.95, force=False):
        if not self.fit_successful and not force: return None
        threshold = p_sigmoid(*self.sigmoid_params, p=p)
        return 10**threshold if self.log else threshold


    def _fit(self):
        # check if the metric reaches 0 and 1
        if self._y.max() < 1 or self._y.min() > 0:
            logger.warning(f"Metric {self.metric} never reaches 0 or 1.")
            return {'params': [None, None], 'switch': None, 'inversed': None, 'message': 'Metric never reaches 0 or 1.', 'success': False}
        
        # check if at least a few points are 0 or 1, by enforcing at least 2 points in either class
        if len(self._y[self._y == 0]) < 2 or len(self._y[self._y == 1]) < 2:
            logger.warning(f"Metric {self.metric} has less than 2 points at either 0 or 1.")
            return {'params': [None, None], 'switch': None, 'inversed': None, 'message': 'Metric has less than 2 points at 0 or 1.', 'success': False}

        try:
            # order _x and _y by _x
            order = np.argsort(self._x)

            # if the first value in (sorted) _y is 1, then the metric order is most likely inversed
            inversed = False
            if self._y[order[0]] == 1:
                inversed = True

            # get the value at which the signal metric switches
            switch = self._x[np.argmax(self._y > 0)]
            if inversed:
                switch = self._x[np.argmax(self._y < 1)]

            # prepare initial guess, we assume k=1 for simplicity
            start_params = [1, -switch]
            if inversed:
                start_params = [-1, switch]

            # fit the sigmoid
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                result = sm.Logit(self._y, sm.add_constant(self._x)).fit(
                    method='bfgs', 
                    start_params=start_params, 
                    disp=False
                )

            # convert the parameters to k, x0 from beta_0 and beta_1
            params = [result.params[1], -result.params[0]/result.params[1]] # [k, x0]

        except RuntimeError:
            logger.warning(f"Could not fit sigmoid to data for {self.on}, switch={switch}.")
            return {'params': [None, None], 'switch': switch, 'inversed': inversed, 'message': 'Fitting failed.', 'result': result, 'success': False}
        
        # check if the parameters are within the bounds
        if params[1] < self._x.min() or params[1] > self._x.max():
            logger.warning(f"Parameter estimates exceed bounds for {self.on}.")
            return {'params': params, 'switch': switch, 'inversed': inversed, 'message': 'Fit exceeds bounds.', 'result': result, 'success': False}
        
        if p_sigmoid(*params) < self._x.min() or p_sigmoid(*params) > self._x.max():
            logger.warning(f"Threshold estimate exceeds bounds for {self.on}.")
            return {'params': params, 'switch': switch, 'inversed': inversed, 'message': 'Threshold exceeds bounds.', 'result': result, 'success': False}
        
        return {'params': params, 'switch': switch, 'inversed': inversed, 'message': 'Fit successful.', 'result': result, 'success': True}
    

    def predict(self, values):
        if not self.fit_successful: raise ValueError("No sigmoid parameters from fitting available.")
        if self.log: values = np.log10(values)
        return sigmoid(values, *self.sigmoid_params)


    def plot(self, title_columns=None, **kwargs):
        # create figure
        if title_columns:
            kwargs['title'] = "-".join([self._df[c].astype(str).values[0] for c in title_columns])
        fig = px.scatter(
            self._df, 
            x=self.on, 
            y=self.metric, 
            width=kwargs.pop('width', 600), 
            height=kwargs.pop('height', 400), 
            log_x=self.log,
            **kwargs
        )
        fig.update_yaxes(range=[0, 1])
        fig.update_layout(showlegend=False)

        # fit params
        if self.fit_successful:
            x_vals = np.logspace(self._x.min(), self._x.max(), 500) if self.log else np.linspace(self._x.min(), self._x.max(), 500)
            y_vals = self.predict(x_vals)
            fig.add_scatter(x=x_vals, y=y_vals, mode='lines', name='Sigmoid fit')
            fig.add_vline(x=self.threshold, line_dash='dash', line_color='black')
            fig.update_layout(title=dict(text=f"{fig.layout.title.text}<br><sup>Threshold: {self.threshold:.3g}</sup>"))
        else:
            fig.update_layout(title=dict(text=f"{fig.layout.title.text}<br><sup>Threshold: None</sup>"))
        return fig
