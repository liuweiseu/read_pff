import sys
import json
import numpy as np
import pff

# define the quabo img size(16*16) and mobo image size(32*32) 
Q_S = 16
M_S = 32

# split the mobo image to 4 quabo images
#
def split_data(d):
    d0 = d[   0:Q_S,   0:Q_S]
    d1 = d[   0:Q_S, Q_S:M_S]
    d2 = d[ Q_S:M_S,   0:Q_S]
    d3 = d[ Q_S:M_S, Q_S:M_S]
    return [np.array(d0, dtype=float), 
            np.array(d0, dtype=float), 
            np.array(d0, dtype=float), 
            np.array(d0, dtype=float)]
    
def read_pff(filename):
    i = 0
    img         = [[], [], [] ,[]]
    boardloc    = [[], [], [] ,[]]
    utc         = [[], [], [] ,[]]
    nanosec     = [[], [], [] ,[]]
    acq_mode    = [[], [], [] ,[]]
    packet_no   = [[], [], [] ,[]]
    f = open(filename, "rb")
    while True:
        # read metadata out
        x = pff.read_json(f)
        if(x==None):
            break
        y = json.loads(x)
        # read image data out
        x = pff.read_image(f,32,2)
        # split the image to 4 quabo images
        data = np.array(x,dtype=float).reshape(32,32)
        sdata = split_data(data)
        # get the metadata and img data, 
        # and then put the data into different lists
        for q in range(4):
            if(i == 0):
                img[q] = np.zeros(shape=(Q_S, Q_S, 1))
                img[q][:,:,-1] = sdata[0]
            else:
                tmp = np.zeros(shape=(Q_S, Q_S, i+1))
                tmp[:,:,:-1] = img[q]
                tmp[:,:,-1] = sdata[0]
                img[q] = tmp
            quabo = 'quabo_' + str(q)
            boardloc[q].append(int(y[quabo]['mod_num']) * 4)
            utc[q].append(int((y[quabo]['pkt_utc'])))
            nanosec[q].append(int((y[quabo]['pkt_nsec'])))
            acq_mode[q].append(int((y[quabo]['acq_mode'])))
            packet_no[q].append(int((y[quabo]['pkt_num'])))
        i = i+1
    # make the tuple for the return data
    # it looks like matlab likes a tuple as a return from a python script
    d = (img[0], boardloc[0], utc[0], nanosec[0], acq_mode[0], packet_no[0],
         img[1], boardloc[1], utc[1], nanosec[1], acq_mode[1], packet_no[1],
         img[2], boardloc[2], utc[2], nanosec[2], acq_mode[2], packet_no[2],
         img[3], boardloc[3], utc[3], nanosec[3], acq_mode[3], packet_no[3])
    return d

if __name__ == '__main__':
    print('hello')
    f = sys.argv[1]
    print(f)
    d = read_pff(f)
