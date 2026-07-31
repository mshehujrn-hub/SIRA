import pprint
class DataExplorer:

    def basic_summary(self, df):

         print(df.info())

         print(df.describe(include="all"))

    def show_columns(self, df):

        print(df.columns)

    def show_shape(self, df):

        print(df.shape)

    def show_random_samples(self, df):

        print(df.sample(5))       

    def show_missing_values(self, df):

        missing_values = df.isnull().sum()

        print(missing_values[missing_values > 0])          

    def duplicate_rows(self, df):
        duplicate_count = df.duplicated().sum()
        pprint.pprint(f"number of duplicate rows: {duplicate_count}")    