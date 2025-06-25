import dataclasses
import plotly.express as px
import pandas as pd
import numpy as np

from .datafit import DataFit

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class Dataset():

    overview: pd.DataFrame
    results: pd.DataFrame
    performances: pd.DataFrame

    # convenience properties
    combined_results = property(lambda self: self.overview.copy().merge(self.results, on='id', how='left', suffixes=('_param', '')))
    combined_performances = property(lambda self: self.overview.copy().merge(self.performances, on='id', how='left', suffixes=('_param', '')))


    @classmethod
    def combine(cls, *datasets):
        overview = pd.concat([ds.overview for ds in datasets], ignore_index=True)
        results = pd.concat([ds.results for ds in datasets], ignore_index=True)
        performances = pd.concat([ds.performances for ds in datasets], ignore_index=True)
        return cls(overview=overview, results=results, performances=performances)


    def __post_init__(self):
        self._check_status()

        # remove superfluous columns if present
        self.overview = self.overview.drop(columns=['notes', 'time_stamp'], errors='ignore')


    def _check_status(self):
        # get the counts of statuses in the results
        status_counts = dict(self.overview['status'].value_counts())

        # check if there are runs which are not finished
        if not len(status_counts) == 1 or 'Finished' not in status_counts:
            logger.warning("There are unfinished or failed runs in the dataset.")
            logger.warning(f"Status counts: {', '.join([f'{value} {key}' for key, value in status_counts.items()])}")


    @property
    def concise_results(self):
        to_keep = ['id', 'status', 'type']
        to_keep.extend([col for col in self.overview.columns if any(s in col for s in ['.type', '.name'])])
        to_keep.extend(self.results.columns)
        to_keep = list(dict.fromkeys(to_keep)) # remove duplicates but keep order
        return self.combined_results[to_keep].copy()
    

    @property
    def unfinished_overview(self):
        return self.overview.loc[self.overview['status'] != 'Finished']
    

    def fit(self, on, metric='decoding_success', log=True):
        return DataFit(self.combined_results, on=on, metric=metric, log=log)
    

    def without(self, select_dict):
        # get the uids where the value of select_dict in the column key is true
        idf = self.overview.copy()
        for key, value in select_dict.items():
            idf = idf.loc[idf[key] == value]
        uids = idf['id'].values
        return Dataset(
            overview=self.overview.loc[~self.overview['id'].isin(uids)],
            results=self.results.loc[~self.results['id'].isin(uids)],
            performances=self.performances.loc[~self.performances['id'].isin(uids)]
        )
    

    def only_with(self, select_dict):
        # get the uids where the value of select_dict in the column key is true
        idf = self.overview.copy()
        for key, value in select_dict.items():
            idf = idf.loc[idf[key] == value]
        uids = idf['id'].values
        return Dataset(
            overview=self.overview.loc[self.overview['id'].isin(uids)],
            results=self.results.loc[self.results['id'].isin(uids)],
            performances=self.performances.loc[self.performances['id'].isin(uids)]
        )
    

    def separate_by_parameters(self, parameters):
        # get the unique values of the parameters
        unique_values = self.overview[parameters].drop_duplicates()

        datasets = []
        # iterate over the unique values
        for i, row in unique_values.iterrows():
            # select the rows with these parameters
            idx = self.overview.columns.intersection(row.dropna().index)
            selectdf = self.overview.loc[self.overview[idx].eq(row.dropna().loc[idx]).all(1)]
            
            # get the data for those ids
            overview = self.overview.loc[self.overview['id'].isin(selectdf['id'])]
            results = self.results.loc[self.results['id'].isin(selectdf['id'])]
            performances = self.performances.loc[self.performances['id'].isin(selectdf['id'])]
            
            # create a new dataset
            datasets.append(Dataset(overview=overview, results=results, performances=performances))

        return datasets


    def separate_by_step(self, step):
        parameters = [col for col in self.overview.columns if col.startswith(step)]
        return self.separate_by_parameters(parameters)


    def get_fits_by_group(self, by, on, metric='decoding_success', log=True, additional_agg={}):
        # get the unique values of the groupings
        unique_values = self.overview[by].drop_duplicates()

        data = []
        # iterate over the unique values
        for i, row in unique_values.iterrows():
            # select the rows with these parameters
            idx = self.overview.columns.intersection(row.dropna().index)
            selectdf = self.overview.loc[self.overview[idx].eq(row.dropna().loc[idx]).all(1)]
            
            # get the result for these ids and fit them
            overview = self.combined_results.loc[self.combined_results['id'].isin(selectdf['id'])]
            fit = DataFit(overview, on, metric=metric, log=log)

            # compile results
            d = {
                **row.to_dict(), 
                'on': on, 
                'threshold': fit.threshold, 
                'threshold_50%': fit.get_threshold(p=0.5), 
                'threshold_99%': fit.get_threshold(p=0.99), 
                'params_k': fit.sigmoid_params[0], 
                'params_x0': fit.sigmoid_params[1],
                'message': fit.fit_result['message'],
            }
            for key, value in additional_agg.items():
                d[key] = getattr(np, value)(overview[key])
            data.append(d)
        
        return pd.DataFrame(data)


    def get_aggregated_results(self, on, how="mean", additional_agg={}):
        # collect the columns to group by
        not_include = [on]
        not_include.extend(self.results.columns)
        not_include.extend([col for col in self.overview.columns if '.' not in col])
        not_include.extend([col for col in self.overview.columns if 'metadata' in col])
        feature_columns = [col for col in self.combined_results.columns if col not in not_include]

        # group by the parameter
        agg = {on: how}
        agg.update(additional_agg)
        return self.combined_results.groupby(feature_columns, as_index=False, dropna=False).agg(agg).reset_index()
    


    def plot_aggregated_xy(self, x, y, additional_agg={}, title_columns=None, **kwargs):
        df = self.get_aggregated_results(on=y, additional_agg=additional_agg)        
        
        if title_columns:
            kwargs['title'] = "-".join([df[c].values[0] for c in title_columns])

        # create the plot
        return px.scatter(df, x=x, y=y, width=kwargs.pop('width', 600), height=kwargs.pop('height', 400), **kwargs)
