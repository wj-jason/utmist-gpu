import os
import pandas as pd
import numpy as np
import librosa
import sqlite3
from tqdm import tqdm
import subprocess

class TrainingDataProcessor:
  def __init__(self,
               data_drive_id = '10PBQNQbw8FlR0Mcn5auMBjTssPloUnyH',
               data_folder = '2024-04-30 raw dataset - tagged only',
               anno_drive_id = '17kQkzsBbwGvn_YfBZI4_3Mclzni3EIRO'
              ):
    self.data_drive_id = data_drive_id
    self.data_folder = data_folder
    self.anno_drive_id = anno_drive_id

  def load_dataset(self) -> None:

      data_zip = 'shared-dir/2024-04-30 raw dataset - tagged only.zip'
      output_dir = 'data/extracted_files'
      if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        try:
          subprocess.run(['unzip', data_zip, '-d', output_dir], check=True)
          print(f'Files extracted to {output_dir}')
        except subprocess.CalledProcessError as e:
          print(f"An error occurred while extracting the zip file: {e}")
      else:
        print(f"{output_dir} already exists. Skipping extraction.")

  def get_annotations(self) -> pd.DataFrame:

    db_dir = 'shared-dir/'
    db_files = [f for f in os.listdir(db_dir) if f.endswith('.db')]

    all_dataframes = []
    for file_name in tqdm(db_files, desc="Processing annotation files", unit="file"):
        file_path = os.path.join(db_dir, file_name)
        conn = sqlite3.connect(file_path)
        df = pd.read_sql_query("SELECT * FROM 'annotations'", conn)
        conn.close()
        all_dataframes.append(df)

    if all_dataframes:
          concatenated_df = pd.concat(all_dataframes, ignore_index=True)
          processed_df = concatenated_df[
            ~(
              (concatenated_df['label1'] == "None") &
              (concatenated_df['label2'] == "None") &
              (concatenated_df['label3'] == "None") &
              (concatenated_df['label4'] == "None") &
              (concatenated_df['label5'] == "None")
            )
          ]
          return processed_df.reset_index(drop=True)
    else:
          raise Exception("No .db files found or no data to concatenate.")

  def get_mel_spectrograms(self):

    self.load_dataset()
    annotations = self.get_annotations()

    spectrograms = []
    labels = []

    for index, row in tqdm(annotations.iterrows(), total=len(annotations), desc='Creating spectrograms', unit='file'):
        try:
          absolute_path = f'data/extracted_files/event_data/{row["path"]}'
          X, sample_rate = librosa.load(absolute_path)
          # 3. Extract Mel Spectrogram, append to spectrograms
          # I had it transposed earlier because I saw a different resource which transposed it
            # but I dont think I need to
          # Also the issue with the black strip over the spectrogram needs to be fixed
          ms = librosa.feature.melspectrogram(y=X, sr=sample_rate, fmax=4096)
          spectrograms.append(ms)
          # 4. Extract labels, append to labels
          labels.append([row[label_column] if row[label_column] != 'None' else None
                        for label_column in ['label1', 'label2', 'label3', 'label4', 'label5']])
        except FileNotFoundError as e:
          print(f"\n\n{e}\n")

    spectrograms = np.array(spectrograms)
    labels = np.array(labels)

    # 5. One-hot-encode labels
    unique_labels = pd.Series(labels.flatten()).dropna().unique()
    label_to_index = {label: i for i, label in enumerate(unique_labels)}
    one_hot_labels = np.zeros((len(labels), len(label_to_index)), dtype=int)
    for i, label_list in enumerate(labels):
        for label in label_list:
            if label is not None:
                one_hot_labels[i, label_to_index[label]] = 1

    # 6. Return spectrograms and labels as a multi-dimensional list
    return spectrograms, one_hot_labels

if __name__ == '__main__':
  processor = TrainingDataProcessor()
  data = processor.get_mel_spectrograms()
  print(data[0][1])
