#!/usr/bin/env python3
# -*- coding: utf-8 -*-
prog_ver = 'extpia v1.0 Copyright (c) 2019-2020 Matjaz Rihtar'
# py_ver = sys.version_info.major
import sys, os, glob, re
import ntpath, argparse
import traceback
from pprint import pprint

from struct import unpack
import pickle, json

# -----------------------------------------------------------------------------
def ntdirname(path):
  try:
    head, tail = ntpath.split(path)
    dirname = head or ntpath.dirname(head)
  except: dirname = ''
  if len(dirname) == 0: dirname = '.'
  if dirname.endswith(os.sep):
    return dirname
  else:
    return dirname + os.sep
# ntdirname

def ntbasename(path):
  try:
    head, tail = ntpath.split(path)
    basename = tail or ntpath.basename(head)
  except: basename = ''
  return basename
# ntbasename

# -----------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def plot_tile(data, title=None):
  try:
    plt.rc('figure', figsize=(9, 9))
    D = np.array(data)
    cmap = cm.terrain
    cmap.set_bad(color='black')
    plt.imshow(D, origin='lower', cmap=cmap)
    if title is not None:
      plt.title(title)
    plt.show()
  except:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    exc = traceback.format_exception_only(exc_type, exc_obj)
    name = sys._getframe().f_code.co_name
    errmsg = '{}({}): {}\n'.format(name, exc_tb.tb_lineno, exc[-1].strip())
    sys.stderr.write(errmsg)
# plot_tile

# -----------------------------------------------------------------------------
def print_matrix(data, fd=sys.stdout, rev=False):
  sdata = [[str(val) for val in row] for row in data]
  lens = [max(map(len, col)) for col in zip(*sdata)]
  fmt = '\t'.join('{{:>{}}}'.format(x) for x in lens)
  table = [fmt.format(*row) for row in sdata]
  if rev: table = reversed(table)
  print('\n'.join(table), file=fd)
# print_matrix

# -----------------------------------------------------------------------------
def procfile(fpath):
  rc = 0
  try:
    fdir = ntdirname(fpath)
    fname = ntbasename(fpath)

    fn = fname.split('_')
    if fn[0].startswith('n') or fn[0].startswith('s'): # SRTM1
      sys.stderr.write('Nothing to be done for SRTM data\n')
      return rc
    if fn[1].startswith('e') or fn[1].startswith('w'): # SRTM1
      sys.stderr.write('Nothing to be done for SRTM data\n')
      return rc

    lat0 = int(fn[0][1:4])
    lon0 = int(fn[0][5:8])

    fns = []
    for ii in range(4):
      fns.append({})

    fns[0]['name'] = fpath
    if fn[0][0] == 'N':
      if fn[0][4] == 'E':
        fns[1]['name'] = '{}N{:03d}E{:03d}_AVE_DSM.pickle'.format(fdir, lat0, lon0+1)
        fns[2]['name'] = '{}N{:03d}E{:03d}_AVE_DSM.pickle'.format(fdir, lat0+1, lon0)
        fns[3]['name'] = '{}N{:03d}E{:03d}_AVE_DSM.pickle'.format(fdir, lat0+1, lon0+1)
      else:
        fns[1]['name'] = '{}N{:03d}W{:03d}_AVE_DSM.pickle'.format(fdir, lat0, lon0+1)
        fns[2]['name'] = '{}N{:03d}W{:03d}_AVE_DSM.pickle'.format(fdir, lat0+1, lon0)
        fns[3]['name'] = '{}N{:03d}W{:03d}_AVE_DSM.pickle'.format(fdir, lat0+1, lon0+1)
    else:
      if fn[0][4] == 'E':
        fns[1]['name'] = '{}S{:03d}E{:03d}_AVE_DSM.pickle'.format(fdir, lat0, lon0+1)
        fns[2]['name'] = '{}S{:03d}E{:03d}_AVE_DSM.pickle'.format(fdir, lat0+1, lon0)
        fns[3]['name'] = '{}S{:03d}E{:03d}_AVE_DSM.pickle'.format(fdir, lat0+1, lon0+1)
      else:
        fns[1]['name'] = '{}S{:03d}W{:03d}_AVE_DSM.pickle'.format(fdir, lat0, lon0+1)
        fns[2]['name'] = '{}S{:03d}W{:03d}_AVE_DSM.pickle'.format(fdir, lat0+1, lon0)
        fns[3]['name'] = '{}S{:03d}W{:03d}_AVE_DSM.pickle'.format(fdir, lat0+1, lon0+1)

    for ii in range(4):
      fpath_ = fns[ii]['name']
      fd = open(fpath_, 'rb')
      sys.stderr.write('Reading {}\n'.format(fpath_))
      fns[ii]['data'] = pickle.load(fd)
      fd.close()

    data = fns[0]['data']
    max_lat_idx = len(data)
    max_lon_idx = len(data[0])

    #with open('0.org', 'w') as fd:
    #  print_matrix(data, fd)

    data1 = fns[1]['data']
    for ii in range(max_lat_idx):
      data[ii].extend([data1[ii][0]])

    data2 = fns[2]['data']
    data.append(data2[0])
        
    data3 = fns[3]['data']
    data[max_lat_idx].extend([data3[0][0]])

    if plot:
      plot_tile(data, '{} (raw)'.format(fname))

    #with open('0.ext', 'w') as fd:
    #  print_matrix(data, fd)

    ppath = fpath.replace('DSM.pickle', 'EXT.pickle')

    sys.stderr.write('Writing {}\n'.format(ppath))
    fd = open(ppath, 'wb')
    pickle.dump(data, fd)
    fd.close()
  except:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    exc = traceback.format_exception_only(exc_type, exc_obj)
    name = sys._getframe().f_code.co_name
    errmsg = '{}({}): {}\n'.format(name, exc_tb.tb_lineno, exc[-1].strip())
    sys.stderr.write(errmsg)
    rc = 1
  return rc
# procfile

# =============================================================================
def main(argv):
  global where, prog, datadir, plot

# argv = ['extpia.py', 'data\s17_w068_1arc_v3.pickle']
  where = ntdirname(argv[0])
  prog = ntbasename(argv[0]).replace('.py', '').replace('.PY', '')

  parser = argparse.ArgumentParser(description='Extends PointInArea data files',
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('inp_files', metavar='<input.pickle>', nargs='+',
                       help='Input file(s) in pickle format')
  parser.add_argument('-d', metavar='<datadir>', default='<prog>{}data'.format(os.sep),
                      dest='datadir', help='SRTM/ALOS data directory')
  parser.add_argument('-p', action='store_true', default=False, dest='plot',
                       help='Plot read SRTM/ALOS data')

  args = parser.parse_args()
  datadir = args.datadir
  plot = args.plot

  rc = 0

  nfiles = 0
  for arg in args.inp_files:
    files = glob.glob(arg)
    for file in files:
      nfiles += 1
      rc += procfile(file)

  if nfiles == 0:
    sys.exit('No files found')

  return rc
# main

# -----------------------------------------------------------------------------
if __name__ == '__main__':
  rc = main(sys.argv)
  sys.exit(rc)
