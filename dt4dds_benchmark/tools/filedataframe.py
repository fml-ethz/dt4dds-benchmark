import dataclasses
import pathlib
import pandas as pd

@dataclasses.dataclass
class FileDataFrame():
    """  """

    filepath: pathlib.Path          # path to the file to save the dataframe in
    save_on_append: bool = False    # whether to save the dataframe to disk after each append
    entries: list = dataclasses.field(default_factory=lambda: [])

    def append(self, entry: dict):
        """ Adds a row to the dataframe and updates the copy on disk. """
        self.entries.append(entry)
        if self.save_on_append: self.to_csv()

    def extend(self, entries: list):
        """ Adds multiple rows to the dataframe and updates the copy on disk. """
        self.entries.extend(entries)
        if self.save_on_append: self.to_csv()

    def to_df(self):
        """ Returns the entries as a dataframe. """
        return pd.DataFrame.from_records(self.entries)

    def to_csv(self):
        """ Saves the dataframe to disk. """
        df = self.to_df()
        df.to_csv(self.filepath, index=False)

    def to_dicts(self):
        """ Returns the entries as a list of dicts. """
        return self.entries
