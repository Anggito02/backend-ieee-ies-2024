class Args:
    def __init__(self, dataset_dir_path,
                 result_data_path, freq, features):
        self.root_path = dataset_dir_path
        self.data_path = 'dataset.csv'
        self.result_data_path = result_data_path

        self.model = 'iTransformer'
        self.freq = freq

        self.seq_len = 96
        self.label_len = 48
        self.pred_len = 48
        
        self.enc_in = features
        self.dec_in = features
        self.c_out = features

        self.d_model = 512
        self.n_heads = 8
        self.e_layers = 3
        self.d_layers = 1
        self.d_ff = 512
        self.output_attention = False
        self.use_norm = True
        self.class_strategy = 'projection'
        self.factor = 1
        self.dropout = 0.1
        self.embed = 'timeF'
        self.activation = 'gelu'
        self.use_amp = False
        
        self.num_workers = 10
        self.batch_size = 32

        self.use_gpu = True
        self.use_multi_gpu = False
        self.gpu = 0
        self.devices = 0



