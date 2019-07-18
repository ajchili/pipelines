import tensorflow_data_validation as tfdv

train_stats = tfdv.generate_statistics_from_csv(data_location=input_path)

tfdv.visualize_statistics(train_stats)
