
import torch
import torch.nn as nn
import os
import warnings
import numpy as np
import pandas as pds

from models.iTransformer.data_provider.data_factory import data_provider
from models.iTransformer.experiments.exp_basic import Exp_Basic
from models.iTransformer.utils.tools import visual

warnings.filterwarnings('ignore')


class Exp_Long_Term_Forecast(Exp_Basic):
    def __init__(self, args):
        super(Exp_Long_Term_Forecast, self).__init__(args)

    def _build_model(self):
        model = self.model_dict[self.args.model].Model(self.args).float()

        if self.args.use_multi_gpu and self.args.use_gpu:
            model = nn.DataParallel(model, device_ids=self.args.device_ids)
        return model

    def _get_data(self, flag):
        try:
            data_set = data_provider(self.args, flag)
            return data_set
        except:
            raise Exception

    def predict(self):
        try:
            pred_data = self._get_data(flag='pred')

            path = os.path.join('models', 'iTransformer')
            best_model_path = os.path.join(path, 'predictor.pth')
            self.model.load_state_dict(torch.load(best_model_path))

            preds = []
            folder_path = self.args.result_data_path
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            self.model.eval()
            with torch.no_grad():
                batch_x, batch_y, batch_x_mark, batch_y_mark, date_pred = pred_data.__getitem__(index=0)
                batch_x = torch.from_numpy(batch_x).float().to(self.device)
                batch_y = torch.from_numpy(batch_y).float()
                batch_x_mark = torch.from_numpy(batch_x_mark).float().to(self.device)
                batch_y_mark = torch.from_numpy(batch_y_mark).float().to(self.device)

                batch_x = batch_x.reshape(1, batch_x.shape[0], batch_x.shape[1])
                batch_y = batch_y.reshape(1, batch_y.shape[0], batch_y.shape[1])
                batch_x_mark = batch_x_mark.reshape(1, batch_x_mark.shape[0], batch_x_mark.shape[1])
                batch_y_mark = batch_y_mark.reshape(1, batch_y_mark.shape[0], batch_y_mark.shape[1])

                date_pred = np.datetime64('1970-01-01T00:00:00') + np.array(date_pred, dtype='timedelta64[s]').reshape(-1)

                # decoder input
                dec_inp = torch.zeros_like(batch_y[:, -self.args.pred_len:, :]).float()
                dec_inp = torch.cat([batch_y[:, :self.args.label_len, :], dec_inp], dim=1).float().to(self.device)

                # encoder - decoder
                if self.args.use_amp:
                    with torch.cuda.amp.autocast():
                        if self.args.output_attention:
                            outputs = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)[0]
                        else:
                            outputs = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)
                else:
                    if self.args.output_attention:
                        outputs = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)[0]
                    else:
                        outputs = self.model(batch_x, batch_x_mark, dec_inp, batch_y_mark)

                input = batch_x.detach().cpu().numpy()
                outputs = outputs.detach().cpu().numpy()

                if pred_data.scale and self.args.inverse:
                    shape = outputs.shape
                    outputs = pred_data.inverse_transform(outputs.squeeze(0)).reshape(shape)
                preds.append(outputs)

                feats = pred_data.feats
                feat_idx = self.args.enc_in if feats[-1] != "OT" else self.args.enc_in - 1
                
                for i in range(feat_idx):
                    gt = input[0, :, i]
                    pd = np.concatenate((input[0, :, i], outputs[0, :, i]), axis=0)

                    feat_path = os.path.join(self.args.result_data_path, 'fig', f'feat_{i}')
                    if not os.path.exists(feat_path):
                        os.makedirs(feat_path)

                    visual(gt, pd, date_pred, feats[i], os.path.join(feat_path, 'preds.png'))

            preds = np.concatenate((input, outputs), axis=1)
            preds = preds.squeeze(0)
            df_preds = pds.DataFrame(preds, columns=feats)

            date_pred = pds.to_datetime(date_pred)
            df_preds.insert(0, 'date', date_pred)

            tmp_npy_preds = np.zeros((preds.shape[0], preds.shape[1] + 1))
            tmp_npy_preds[:, 0] = date_pred
            tmp_npy_preds[:, 1:] = preds

            npy_preds = np.zeros((tmp_npy_preds.shape[0] + 1, tmp_npy_preds.shape[1]))
            npy_preds[0, :] = feats.insert(0, 'date')
            npy_preds[1:, :] = tmp_npy_preds

            # Save preds
            df_preds.to_csv(os.path.join(self.args.result_data_path, 'preds.csv'), index=False)
            df_preds.to_excel(os.path.join(self.args.result_data_path, 'preds.xlsx'), index=False)
            np.save(os.path.join(self.args.result_data_path, 'preds.npy'), npy_preds)

            return

        except:
            raise Exception