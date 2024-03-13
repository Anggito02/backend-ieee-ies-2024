from models.iTransformer.data_provider.data_loader import Dataset_Pred

def data_provider(args, flag):
    try:
        timeenc = 0 if args.embed != 'timeF' else 1

        # Prediction confi
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

        return data_set
    except:
        raise Exception