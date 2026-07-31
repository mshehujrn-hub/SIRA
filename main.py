from src.data_loader import DataLoader
from src.eda import DataExplorer
from src.utils import print_header
from src.preprocessing import DataCleaner

def main():
    loader = DataLoader()
    explorer = DataExplorer()

    df = loader.load_data()

    explorer.basic_summary(df)
    explorer.show_columns(df)
    explorer.show_shape(df)
    explorer.show_random_samples(df)
    explorer.show_missing_values(df)

def main():
    loader = DataLoader()
    df = loader.load_data()
    explorer = DataExplorer

    print_header("Data Head Preview")
    print(df.head().to_string())   

def main():
    loader = DataLoader()
    cleaner = DataCleaner()

    df = loader.load_data()

    print("before cleaning")
    print(df.shape)

    df = cleaner.remove_missing(df) 
    df = cleaner.remove_duplicates (df)    
    df = cleaner.strip_spaces(df)
    df = cleaner.lowercase(df)

    print("after cleaning")
    print(df.shape)

    print(df.isnull().sum())
    print(df.duplicated().sum())
    print(df.head())

if __name__ == "__main__":
    main()        
