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
    if dp == 'img16':
        image_size = 32
        bytes_per_pixel = 2
        is_ph = False
    elif dp == 'img8':
        image_size = 32
        bytes_per_pixel = 1
        is_ph = False
    elif dp == 'ph1024':
        image_size = 32
        bytes_per_pixel = 2
        is_ph = True
    elif dp in ['ph256', 'ph16']:
        image_size = 16
        bytes_per_pixel = 2
        is_ph = True
    else:
        raise Exception("bad data product %s"%dp)
    return image_size, bytes_per_pixel, is_ph

# split the mobo image to 4 quabo images
#
def split_data(d):
    d0 = np.array(d[   0:Q_S,   0:Q_S], dtype=float).reshape(Q_S,Q_S,1)
    d1 = np.array(d[   0:Q_S, Q_S:M_S], dtype=float).reshape(Q_S,Q_S,1)
    d2 = np.array(d[ Q_S:M_S,   0:Q_S], dtype=float).reshape(Q_S,Q_S,1)
    d3 = np.array(d[ Q_S:M_S, Q_S:M_S], dtype=float).reshape(Q_S,Q_S,1)
    return [d0, d1, d2, d3]

# read data from ph256 pff file 
#
def read_ph256(f, image_size, bytes_per_pixel):
    dat         = np.zeros((Q_S,Q_S,0))
    quabo_no    = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    packet_no   = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    tai         = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    nanosec     = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    localtime   = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    while True:
        # read metadata out
        x = pff.read_json(f)
        if(x==None):
            break
        y = json.loads(x)
        # read image data out
        x = pff.read_image(f,image_size,bytes_per_pixel)

        dat = np.append(dat, np.array(x, dtype=float).reshape(Q_S,Q_S,1), axis=2)
        quabo_no = np.append(quabo_no, int(y['quabo_num']))
        packet_no = np.append(packet_no, int(y['pkt_num']))
        # we changed 'pkt_utc' to 'pkt_tai' in the latest verison of code
        try:
            tai = np.append(tai, int(y['pkt_tai']))
        except:
            tai = np.append(tai, int(y['pkt_utc']))
        nanosec = np.append(nanosec, int(y['pkt_nsec']))
        lot = int(y['tv_sec']) + int(y['tv_usec'])/1000000
        localtime = np.append(localtime, lot)
    # convert list to np array
    d = (dat, quabo_no, tai, nanosec, packet_no, localtime)
    return d

# parse data from ph1024 pff file 
def read_ph1024(f, image_size, bytes_per_pixel):
    dat         = [np.zeros((Q_S,Q_S,0)), np.zeros((Q_S,Q_S,0)), np.zeros((Q_S,Q_S,0)) ,np.zeros((Q_S,Q_S,0))]
    tai         = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    nanosec     = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    packet_no   = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    localtime   = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
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
        # get the metadata and data, 
        # and then put the data into different lists
        for q in range(4):
            quabo = 'quabo_' + str(q)  
            dat[q] = np.append(dat[q], sdata[q], axis=2) 
            tai[q] = np.append(tai[q], int((y[quabo]['pkt_tai'])))
            nanosec[q] = np.append(nanosec[q], int((y[quabo]['pkt_nsec'])))
            packet_no[q] = np.append(packet_no[q], int((y[quabo]['pkt_num'])))
            lot = int(y[quabo]['tv_sec']) + int(y[quabo]['tv_usec'])/1000000
            localtime[q] = np.append(localtime[q], lot)
    # make the tuple for the return data
    # it looks like matlab likes a tuple as a return from a python script
    # convert list to np array
    d = (dat[0], tai[0], nanosec[0],  packet_no[0], localtime[0],
         dat[1], tai[1], nanosec[1],  packet_no[1], localtime[1],
         dat[2], tai[2], nanosec[2],  packet_no[2], localtime[2],
         dat[3], tai[3], nanosec[3],  packet_no[3], localtime[3])
    return d

# parse data from img pff file 
def read_img(f, image_size, bytes_per_pixel):
    dat         = [np.zeros((Q_S,Q_S,0)), np.zeros((Q_S,Q_S,0)), np.zeros((Q_S,Q_S,0)) ,np.zeros((Q_S,Q_S,0))]
    boardloc    = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    tai         = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    nanosec     = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    acq_mode    = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    packet_no   = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
    localtime   = [np.zeros(0), np.zeros(0), np.zeros(0) ,np.zeros(0)]
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
        # get the metadata and data, 
        # and then put the data into different lists
        for q in range(4):
            quabo = 'quabo_' + str(q)
            dat[q] = np.append(dat[q], sdata[q], axis=2) 
            boardloc[q] = np.append(boardloc[q], int(y[quabo]['mod_num']) * 4)
            # we changed 'pkt_utc' to 'pkt_tai' in the latest verison of code
            try:
                tai[q] = np.append(tai[q], int((y[quabo]['pkt_utc'])))
            except:
                tai[q] = np.append(tai[q], int((y[quabo]['pkt_tai'])))
            nanosec[q] = np.append(nanosec[q], int((y[quabo]['pkt_nsec'])))
            acq_mode[q] = np.append(acq_mode[q], int((y[quabo]['acq_mode'])))
            packet_no[q]= np.append(packet_no[q], int((y[quabo]['pkt_num'])))
            lot = int(y[quabo]['tv_sec'])+int(y[quabo]['tv_usec'])/1000000
            localtime[q] = np.append(localtime[q], lot)
    # make the tuple for the return data
    # it looks like matlab likes a tuple as a return from a python script
    # convert list to np array
    d = (dat[0], boardloc[0], tai[0], nanosec[0], acq_mode[0], packet_no[0], localtime[0],
         dat[1], boardloc[1], tai[1], nanosec[1], acq_mode[1], packet_no[1], localtime[1],
         dat[2], boardloc[2], tai[2], nanosec[2], acq_mode[2], packet_no[2], localtime[2],
         dat[3], boardloc[3], tai[3], nanosec[3], acq_mode[3], packet_no[3], localtime[3])
    return d

# read metadata and img or ph data from pff file
#
def read_pff(filename):
    # parse the filename
    [image_size, bytes_per_pixel, is_ph] = parse_pff(filename)
    f = open(filename, "rb")
    if(is_ph == False):
        # this is for img16 or img8 pff file 
        d = read_img(f, image_size, bytes_per_pixel)
    elif(image_size == 32):
        # this is for ph1024 pff file
        d = read_ph1024(f, image_size, bytes_per_pixel)
    elif(image_size == 16):
        # this is for ph256 or ph16 pff file
        d = read_ph256(f, image_size, bytes_per_pixel)
    return d

if __name__ == '__main__':
    f = sys.argv[1]
    print(f)
    d = read_pff(f)
