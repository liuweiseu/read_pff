import sys
import json
import numpy as np
import pff

# define the quabo img size(16*16) and mobo image size(32*32) 
# if it's image mode, M_S should be the same as image_size returned by parse_pff()
Q_S = 16
M_S = 32

# parse the name of pff file.
# the name contains some useful information.
#
def parse_pff(filename):
    dict = pff.parse_name(filename)
    dp = dict['dp']
    if dp == 'img16' or dp =='1':
        image_size = 32
        bytes_per_pixel = 2
        is_ph = False
    elif dp == 'ph16' or dp =='3':
        image_size = 16
        bytes_per_pixel = 2
        is_ph = True
    elif dp == 'img8' or dp == '2':
        image_size = 32
        bytes_per_pixel = 1
        is_ph =False
    else:
        raise Exception("bad data product %s"%dp)
    return image_size, bytes_per_pixel, is_ph

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
    localtime   = [[], [], [] ,[]]
    # parse the filename
    [image_size, bytes_per_pixel, is_ph] = parse_pff(filename)

    f = open(filename, "rb")
    while True:
        # read metadata out
        x = pff.read_json(f)
        if(x==None):
            break
        y = json.loads(x)
        # read image data out
        x = pff.read_image(f,image_size,bytes_per_pixel)
        # split the image to 4 quabo images
        data = np.array(x,dtype=float).reshape(image_size,image_size)
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
            lot = int(y[quabo]['tv_sec'])+int(y[quabo]['tv_usec'])/1000000
            localtime[q].append(lot)
        i = i+1
    # make the tuple for the return data
    # it looks like matlab likes a tuple as a return from a python script
    d = (img[0], boardloc[0], utc[0], nanosec[0], acq_mode[0], packet_no[0], localtime[0],
         img[1], boardloc[1], utc[1], nanosec[1], acq_mode[1], packet_no[1], localtime[1],
         img[2], boardloc[2], utc[2], nanosec[2], acq_mode[2], packet_no[2], localtime[2],
         img[3], boardloc[3], utc[3], nanosec[3], acq_mode[3], packet_no[3], localtime[3])
    return d

if __name__ == '__main__':
    print('hello')
    f = sys.argv[1]
    print(f)
    d = read_pff(f)
