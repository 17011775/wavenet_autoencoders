# coding: utf-8
"""
Make subset of dataset

usage: mksubset.py [options] <in_dir> <out_dir> <scp_dir>

options:
    -h, --help               Show help message.
"""
from docopt import docopt
import librosa
from glob import glob
from os.path import join, basename, exists, splitext
from tqdm import tqdm
import sys
import os
from shutil import copy2
from scipy.io import wavfile
import numpy as np
import  json

LANs = ['english','french','mandarin','LANG1','LANG2']


def read_wav(src_file):
    sr,x = wavfile.read(src_file)
    #x,sr = librosa.core.load(path)
    return sr,x
def write_wav(dst_path,sr,x):
    wavefile.write(dst_path,sr,x)



if __name__ == "__main__":
    args = docopt(__doc__)
    in_dir = args["<in_dir>"] # default : 2020/2017/
    out_dir = args["<out_dir>"] # default: dump/2017/
    scp_dir = args['<scp_dir>'] # default: scp/2017/
    #limit = float(args["--limit"])
    #train_dev_test_split = args["--train-dev-test-split"]
    #dev_size = float(args["--dev-size"])
    #test_size = float(args["--test-size"])
    #target_sr = args["--target-sr"]
    #target_sr = int(target_sr) if target_sr is not None else None
    #random_state = int(args["--random-state"])

    signed_int16_max = 2**15
    tr_src_files = []
    dev_src_files = []
    test_src_files = []
    for lan in LANs:
        tr_dev_src_fs = sorted(glob(in_dir+f'{lan}/train/*.wav'))
        te_src_fs = sorted(glob(in_dir + f'{lan}/test/*/*.wav'))
        num = len(tr_dev_src_fs)
        dev_num = int(0.1 * num)
        tr_src_files.extend(tr_dev_src_fs[:-dev_num])
        dev_src_files.extend(tr_dev_src_fs[-dev_num:])
        test_src_files.extend(te_src_fs)
    print(f"total number of train utts {len(tr_src_files)} dev utts {len(dev_src_files)}")

    
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()   

    os.makedirs(out_dir + 'train_no_dev/',exist_ok=True)
    os.makedirs(out_dir + 'dev/',exist_ok=True)
    os.makedirs(out_dir + 'test/',exist_ok=True)

    os.makedirs(scp_dir,exist_ok=True)
    

    speakers = [] 
    tr_src_dst_files = []
    tr_src_dst_f = open(f'{scp_dir}train_src_dst.json','w')
    for src_path in tr_src_files:
        sr,x = read_wav(src_path)
        if x.dtype == np.int16:
            x = x.astype(np.float32) / signed_int16_max
        scaler.partial_fit(x.astype(np.float64).reshape(-1,1))
        lan = src_path.split('/')[-3]
        fname = src_path.split('/')[-1]
        sp = fname.split('.')[0]
        if sp not in speakers:
            speakers.append(sp)
        dst_path = out_dir + f'train_no_dev/{lan}/{sp}/'
        os.makedirs(dst_path,exist_ok=True)
        tr_src_dst_files.append( (src_path,dst_path))
        #copy2(src_path,dst_path)    
    json.dump(tr_src_dst_files,tr_src_dst_f)


    dev_src_dst_files = []
    dev_src_dst_f = open(f'{scp_dir}dev_src_dst.json','w')
    for src_path in dev_src_files:
        sr,x = read_wav(src_path)
        if x.dtype == np.int16:
            x = x.astype(np.float32) / signed_int16_max
        scaler.partial_fit(x.astype(np.float64).reshape(-1,1))
        lan = src_path.split('/')[-3]
        fname = src_path.split('/')[-1]
        sp = fname.split('.')[0]
        if sp not in speakers:
            speakers.append(sp)
        dst_path = out_dir + f'dev/{lan}/{sp}/'
        os.makedirs(dst_path,exist_ok=True)
        dev_src_dst_files.append( (src_path,dst_path) )
        #copy2(src_path,dst_path)    
    json.dump(dev_src_dst_files,dev_src_dst_f)

    test_src_dst_files = []
    test_src_dst_f = open(f'{scp_dir}test_src_dst.json','w')
    for src_path in test_src_files:
        sr,x = read_wav(src_path)
        if x.dtype == np.int16:
            x = x.astype(np.float32) / signed_int16_max
        scaler.partial_fit(x.astype(np.float64).reshape(-1,1))
        ti = src_path.split('/')[-2]
        fname = src_path.split('/')[-1]
        lan = src_path.split('/')[-4]
        ind = fname.split('.')[0]
        dst_path = out_dir + f'test/{lan}/{ti}/{ind}/'
        os.makedirs(dst_path,exist_ok=True)
        test_src_dst_files.append( (src_path,dst_path) )
        #copy2(src_path,dst_path)
    json.dump(test_src_dst_files,test_src_dst_f)


    speaker2ind = {sp:ind for ind,sp in enumerate(speakers)}
    f_sp = open('2017_speaker2ind.json','w')
    json.dump(speaker2ind,f_sp)
    print("Waveform min: {}".format(scaler.data_min_))
    print("Waveform max: {}".format(scaler.data_max_))
    absmax = max(np.abs(scaler.data_min_[0]), np.abs(scaler.data_max_[0]))
    print("Waveform absolute max: {}".format(absmax))
    if absmax > 1.0:
        print("There were clipping(s) in your dataset.")
    print("Global scaling factor would be around {}".format(1.0 / absmax))

