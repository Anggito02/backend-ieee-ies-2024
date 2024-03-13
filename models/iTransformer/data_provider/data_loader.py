import os
import numpy as np
import pandas as pd
from torch.utils.data import Dataset
from sklearn.preprocessing import StandardScaler
from models.iTransformer.utils.timefeatures import time_features
import warnings

warnings.filterwarnings('ignore')

class Dataset_Pred(Dataset):
    def __init__(self, root_path, flag='pred', size=None,
                 data_path='ETTh1.csv', timeenc=0, freq='15min', cols=None):
        # size [seq_len, label_len, pred_len]
        # info
        if size == None:
            self.seq_len = 24 * 4 * 4
            self.label_len = 24 * 4
            self.pred_len = 24 * 4
        else:
            self.seq_len = size[0]
            self.label_len = size[1]
            self.pred_len = size[2]
        # init
        assert flag in ['pred']

        self.scale = False
        self.inverse = False
        self.timeenc = timeenc
        self.freq = freq
        self.cols = cols
        self.root_path = root_path
        self.data_path = data_path
        self.__read_data__()

    def __read_data__(self):
        try:
            self.scaler = StandardScaler()
            df_raw = pd.read_csv(os.path.join(self.root_path, self.data_path))
            '''
            df_raw.columns: ['date', ...(other features), target feature]
            '''
            self.feats = list(df_raw.columns)
            self.feats.remove('date')

            if self.cols:
                cols = self.cols.copy()
                cols.remove(self.target)
            else:
                cols = list(df_raw.columns)
                cols.remove('date')
            border1 = len(df_raw) - self.seq_len
            border2 = len(df_raw)


            cols_data = df_raw.columns[1:]
            df_data = df_raw[cols_data]

            if self.scale:
                self.scaler.fit(df_data.values)
                data = self.scaler.transform(df_data.values)
            else:
                data = df_data.values

            tmp_stamp = df_raw[['date']][border1:border2]
            tmp_stamp['date'] = pd.to_datetime(tmp_stamp.date)
            pred_dates = pd.date_range(tmp_stamp.date.values[-1], periods=self.pred_len + 1, freq=self.freq)

            df_stamp = pd.DataFrame(columns=['date'])
            df_stamp.date = list(tmp_stamp.date.values) + list(pred_dates[1:])
            data_date = np.array(df_stamp.date)
            if self.timeenc == 0:
                df_stamp['month'] = df_stamp.date.apply(lambda row: row.month, 1)
                df_stamp['day'] = df_stamp.date.apply(lambda row: row.day, 1)
                df_stamp['weekday'] = df_stamp.date.apply(lambda row: row.weekday(), 1)
                df_stamp['hour'] = df_stamp.date.apply(lambda row: row.hour, 1)
                df_stamp['minute'] = df_stamp.date.apply(lambda row: row.minute, 1)
                df_stamp['minute'] = df_stamp.minute.map(lambda x: x // 15)
                data_stamp = df_stamp.drop(['date'], 1).values
            elif self.timeenc == 1:
                data_stamp = time_features(pd.to_datetime(df_stamp['date'].values), freq=self.freq)
                data_stamp = data_stamp.transpose(1, 0)

            self.data_x = data[border1:border2]
            if self.inverse:
                self.data_y = df_data.values[border1:border2]
            else:
                self.data_y = data[border1:border2]
            self.data_stamp = data_stamp
            self.data_date = (data_date - np.datetime64('1970-01-01T00:00:00.000000000')) / np.timedelta64(1, 's')
        except:
            raise Exception

    def __getitem__(self, index):
        s_begin = index
        s_end = s_begin + self.seq_len
        r_begin = s_end - self.label_len
        r_end = r_begin + self.label_len + self.pred_len
        d_begin = s_begin
        d_end = s_end + self.pred_len

        seq_x = self.data_x[s_begin:s_end]
        if self.inverse:
            seq_y = self.data_x[r_begin:r_begin + self.label_len]
        else:
            seq_y = self.data_y[r_begin:r_begin + self.label_len]
        seq_x_mark = self.data_stamp[s_begin:s_end]
        seq_y_mark = self.data_stamp[r_begin:r_end]

        date_pred = self.data_date[d_begin:d_end]

        return seq_x, seq_y, seq_x_mark, seq_y_mark, date_pred

    def __len__(self):
        return len(self.data_x) - self.seq_len + 1

    def inverse_transform(self, data):
        return self.scaler.inverse_transform(data)
