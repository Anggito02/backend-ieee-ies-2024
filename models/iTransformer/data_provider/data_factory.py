from models.iTransformer.data_provider.data_loader import Dataset_Pred
from torch.utils.data import DataLoader

def data_provider(args, flag):
    timeenc = 0 if args.embed != 'timeF' else 1

    # Prediction config
    shuffle_flag = False
    drop_last = False
    batch_size = 1
    freq = args.freq
    Data = Dataset_Pred
    
    data_set = Data(
        root_path=args.root_path,
        data_path=args.data_path,
        flag=flag,
        size=[args.seq_len, args.label_len, args.pred_len],
        timeenc=timeenc,
        freq=freq
    )

    data_loader = DataLoader(
        data_set,
        batch_size=batch_size,
        shuffle=shuffle_flag,
        num_workers=1,
        drop_last=drop_last)
    return data_set, data_loader
