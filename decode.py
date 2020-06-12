import serial
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse


parser = argparse.ArgumentParser(description='Decodes !!')
parser.add_argument('-p',"--path", type=str,
                    help='Specify path of data file.')


magic_word = b'\x02\x01\x04\x03\x06\x05\x08\x07'

def decode_header(header):
    header = np.frombuffer(header, dtype=np.uint32)
    d = {}
    d['version'] = header[0]
    d['totalPacketLength'] = header[1]
    d['platform'] = header[2]
    d['frame_number'] = header[3]
    d['timeCpuCycles'] = header[4]
    d['numDetectedObj'] = header[5]
    d['n_tlvs'] = header[6]
    d['subFrameNumber'] = header[7]
    return d

def decode_objs(buffer,msg_len, header, frame_no):
    no_objs = int(msg_len/16)
    no_objs_header = header['numDetectedObj']
    if(no_objs != no_objs_header):
        print("Mismatch while reading objs")
        return None
    obj_iter = 0
    objs = []
    for k in range(no_objs):
        o = np.frombuffer(readBuffer[obj_iter:obj_iter+16], dtype=np.float32)
        objs.append(o)
        obj_iter = obj_iter + 16
    objs = np.stack(objs)
    objs = np.insert(objs,0,frame_no,axis=1)
    return objs


def main():
    args = parser.parse_args()
    with open(args.path, 'rb') as f:
        readBuffer = f.read()
    i_history = []
    start_idx = 0
    all_objs = np.array([[0,0,0,0,0]], dtype=np.float32)
    total_objs_seen = 0
    total_objs_header = 0
    frames = []
    actual_frame = 0
    while True:
        i = readBuffer.find(magic_word,start_idx,len(readBuffer))
        if(i==-1):
            break
        i_history.append(i)
        start_idx = i + 8
        idx = start_idx
        header = decode_header(readBuffer[idx:idx+32])
        idx += 32
        if(header['totalPacketLength'] > len(readBuffer[i:])):
            print("Incomplete Package. Breaking.")
            break
        frames.append(header['frame_number'])
        total_objs_header += header['numDetectedObj']
        try:
            for tlv in range(header['n_tlvs']):
                msg_type = np.frombuffer(readBuffer[idx:idx+4], dtype=np.uint32)[0]
                idx += 4
                msg_len = np.frombuffer(readBuffer[idx:idx+4], dtype=np.uint32)[0]
                idx += 4
                # If msg is of type detected objs read, else continue
                if(msg_type == 1):
                    no_objs = header['numDetectedObj']
                    points = []
                    for o in range(no_objs):
                        point = np.frombuffer(readBuffer[idx:idx+16], dtype=np.float32)
                        points.append(point)
                        idx += 16
                    objs = np.stack(points)
                    objs = np.insert(objs, 0, actual_frame,axis=1)
                    if(objs is None):
                        print("Error reading packet")
                        break
                    all_objs = np.concatenate([all_objs,objs])
                    total_objs_seen += objs.shape[0]
                    break
                else:
                    idx += msg_len
        except Exception as e:
            print(e)
            print("skipping packet")

        actual_frame += 1
            
    print("Len frame ", len(frames))
    print("Objs seen ", total_objs_seen)
    print("objs total ", total_objs_header)
    df = pd.DataFrame(all_objs, columns=['frame','x','y','z','v'])
    df.to_csv(args.path[:-3]+str(".csv"))

if __name__ == "__main__":
    main()