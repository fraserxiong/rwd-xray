#!/usr/bin/env python3
#
# Civic sedan torque tuning
#
import os
import sys
import argparse
import subprocess
import struct

original_torque_table = [
  0x0,   0x917, 0xDC5,  0x1017,  0x119F,  0x140B,  0x1680,  0x1680, 0x1680,
  0x0,   0x917, 0xDC5,  0x1017,  0x119F,  0x140B,  0x1680,  0x1680,  0x1680,
  0x0,   0x917, 0xDC5,  0x1017,  0x119F,  0x140B,  0x1680,  0x1680,  0x1680,
  0x0,   0x917, 0xDC5,  0x1017,  0x119F,  0x140B,  0x1680,  0x1680,  0x1680,
  0x0,   0x917, 0xDC5,  0x1017,  0x119F,  0x140B,  0x1680,  0x1680,  0x1680,
  0x0,   0x917, 0xDC5,  0x1017,  0x119F,  0x140B,  0x1680,  0x1680,  0x1680,
  0x0,   0x6B3, 0xB1A,  0xCCD,   0xE9A,   0x104D,  0x119A,  0x11DA,  0x11DA
]

torque_table_start_addr = 0x1379a
torque_table_size = len(original_torque_table) * 2


def main():
  # example: python3 torque_tuning.py --input_bin civic_tba_0_steering.bin --scale 2
  parser = argparse.ArgumentParser()
  parser.add_argument("--input_bin", required=True, help="Full firmware binary file")
  parser.add_argument("--scale", type=int, required=True, help="Scale factor, >= 2")
  args = parser.parse_args()

  print("Scale torque values to {}X, table size: {} bytes".format(args.scale, torque_table_size))
  with open(args.input_bin, 'rb') as f:
    full_fw = f.read()
    # Verify the table data
    cur_table = full_fw[torque_table_start_addr:(torque_table_start_addr + torque_table_size)]
    original_torque_table_bytes = bytearray()
    for v in original_torque_table:
      original_torque_table_bytes += struct.pack('!H', v)
    assert cur_table == original_torque_table_bytes, 'Incorrect full fw bin, torque table mismatched.'
    # Build new table data
    new_fw = bytearray()
    new_fw += full_fw[:torque_table_start_addr]
    for v in original_torque_table:
      scaled_v = v * args.scale
      new_fw += struct.pack('!H', scaled_v)
    new_fw += full_fw[(torque_table_start_addr + torque_table_size):]
    assert len(full_fw) == len(new_fw), 'New fw length error {}.'.format(len(new_fw))
    out_bin_path = os.path.join(os.path.dirname(args.input_bin), '{}_{}x.bin'.format(os.path.basename(args.input_bin).split('.')[0], args.scale))
    with open(out_bin_path, 'wb') as out_f:
      out_f.write(new_fw)
      print('New fw bin saved to %s.' % out_bin_path)
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    cmds = [
      'python3',
      'bin_to_rwd.py',
      '--input_bin', out_bin_path,
      '--model',  '39990-TBA-A030'
    ]
    subprocess.check_call(cmds, cwd=cur_dir)
    print('RWD file %s created.' % (out_bin_path[:-4] + '.rwd'))

if __name__== "__main__":
    main()
