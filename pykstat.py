#!/usr/bin/env python
import os
import sys
import getopt
import kstat
import itertools
import re
import time

class EqMatcher:
  def __init__(self, value):
    self.value = value
  def match(self, value):
    return value == self.value

class AnyMatcher(object):
  __object__ = None
  def __new__(cls):
    if cls.__object__ is None:
      cls.__object__ = object.__new__(cls)
    return cls.__object__
  def match(self, value):
    return True

def is_regexp(s):
  return type(s)==type('') and len(s)>1 and s[:1]=='/' and s[-1:]=='/'

def get_matcher(s):
  if s is None: return AnyMatcher().match
  if is_regexp(s): return re.compile(s[1:-1]).search
  return EqMatcher(s).match

def isint(s):
  try:
    int(s)
    return True
  except (ValueError,TypeError):
    return False

def print_usage(arg0):
  print>>sys.stderr, """Usage:
%s [ -qlp ] [ -T d|u ] [ -c class ]
      [ -LDRC ] [ -t type ] [ -r size ]
      [ -m module ] [ -i instance ] [ -n name ] [ -s statistic ]
      [ interval [ count ] ]
%s [ -qlp ] [ -T d|u ] [ -c class ]
      [ -LDRC ] [ -t type ] [ -r size ]
      [ module:instance:name:statistic ... ]
      [ interval [ count ] ]""" % (arg0,arg0)

def main(argv):
  filter_module = None
  filter_instance = None
  filter_name = None
  filter_class = None
  filter_type = None
  filter_field = None
  do_quiet = False
  do_parsable = False
  do_list = False
  do_debug = False
  do_rawdebug = False
  do_compact = False
  compact_delta = False
  compact_average = False
  compact_collect = False
  list_what = 'parameters'
  loop_wait = None
  loop_iter = None
  loop_stamp = None
  arg0 = os.path.basename(argv[0])
  maxraw = 0
  try:
    opts,args = getopt.getopt(argv[1:],'m:i:n:s:c:qplT:'+'Lt:DRCr:', ['C','CD','CA','CC','CCD','CDC','CCA','CAC'])
  except getopt.error, e:
    print>>sys.stderr, e
    print_usage(arg0)
    return 2
  for opt,optarg in opts:
    if opt == '-m':
      filter_module = optarg
    elif opt == '-i':
      filter_instance = optarg
    elif opt == '-n':
      filter_name = optarg
    elif opt == '-s':
      filter_field = optarg
    elif opt == '-c':
      filter_class = optarg
    elif opt == '-q':
      do_quiet = True
    elif opt == '-p':
      do_parsable = True
    elif opt == '-l':
      do_list = True
    elif opt == '-T':
      if optarg == 'u':
        loop_stamp = (lambda:int(time.time()),)*2
      elif optarg == 'd':
        loop_stamp = (time.ctime,lambda:time.strftime('%H:%M:%S'))
      else:
        print 'Error: Invalid timestamp specifier '+optarg
        return 2
    # pykstat extended options
    elif opt == '-t':
      filter_type = optarg
    elif opt == '-D':
      if do_debug:
        do_rawdebug = True
      else:
        do_debug = True
    elif opt == '-R':
      do_rawdebug = True
    elif opt == '-r':
      try: maxraw = int(optarg)
      except ValueError: do_rawdebug = True
    elif opt == '-L':
      do_list = True
      list_what = 'types'
    elif opt in ('-C','--C'):
      do_compact = True
    elif opt in ('--CC',):
      do_compact = True
      compact_collect = True
    elif opt in ('--CD',):
      do_compact = True
      compact_delta = True
    elif opt in ('--CCD','--CDC'):
      do_compact = True
      compact_collect = True
      compact_delta = True
    elif opt in ('--CA',):
      do_compact = True
      compact_delta = True
      compact_average = True
    elif opt in ('--CCA','--CAC'):
      do_compact = True
      compact_collect = True
      compact_delta = True
      compact_average = True
  do_verbose = not (do_quiet or do_list or do_parsable or do_compact)

  #if (filter_module is None and filter_instance is None and
  #    filter_name is None and filter_field is None and args):
  if args and not isint(args[0]):
    l = args.pop(0).split(':',3)
    if l: filter_module = l.pop(0)
    if l: filter_instance = l.pop(0)
    if l: filter_name = l.pop(0)
    if l: filter_field = l.pop(0)

  # NB: This is special code to be bugcompatible with original (Solaris 10) kstat:
  # - don't checks for argument count
  # - uses last two numeric arguments
  iargs = []
  for s in args:
    try: iargs.append(int(s,0))
    except ValueError: pass
  iargs = iargs[-2:]
  if iargs: loop_wait = iargs.pop(0)
  if iargs: loop_iter = iargs.pop(0)

  if loop_wait is None and loop_iter is None: loop_iter = 1
  #if loop_iter is not None and loop_iter < 1: loop_iter = 1

  # This is also kstat-compatible input checks
  if loop_wait is not None and loop_wait < 1:
    print>>sys.stderr, "Error: Interval must be an integer >= 1"
    print_usage(arg0)
    return 2
  if do_quiet and do_list:
    print>>sys.stderr, "Error: -q and -l are mutually exclusive."
    print_usage(arg0)
    return 2
  if do_quiet and do_compact:
    print>>sys.stderr, "Error: -q and -C are mutually exclusive."
    print_usage(arg0)
    return 2
  if do_list and do_compact:
    print>>sys.stderr, "Error: -l and -C are mutually exclusive."
    print_usage(arg0)
    return 2

  # Start parsing...
  if not filter_module: filter_module = None
  if not filter_instance: filter_instance = None
  if not filter_name: filter_name = None
  filter_args = []
  if is_regexp(filter_module):
    filter_args.append(None)
  else:
    filter_args.append(filter_module)
  try:
    filter_instance = int(filter_instance)
    filter_args.append(filter_instance)
  except (TypeError,ValueError):
    filter_args.append(None)
  if is_regexp(filter_name):
    filter_args.append(None)
  else:
    filter_args.append(filter_name)
  if is_regexp(filter_class):
    filter_args.append(None)
  else:
    filter_args.append(filter_class)
  plain_fields = ['class','snaptime','crtime']
  if do_debug: plain_fields.extend(['-type','-data-size','-ndata','-flags'])

  #check0 = [get_matcher(s) for s in filter_args]
  check0 = [get_matcher(s) for s in (filter_module,filter_instance,filter_name,filter_class,filter_type)]
  check = [get_matcher(s) for s in (filter_module,filter_instance,filter_name,filter_class,filter_type,filter_field)]

  if filter_args[1] is None: filter_args[1] = -1
  ko = kstat.Kstat(*filter_args)
  ko.debug = do_debug
  if maxraw is not None: ko.maxraw = maxraw
  if do_rawdebug: ko.maxraw = None

  compact_field_names = []
  compact_field_sizes = []
  compact_fields_completed = False
  compact_fields_previous = None
  res = 1
  for loop_no in itertools.count():
    if loop_iter is not None and loop_no>=loop_iter: break
    if loop_no:
      # NB: Original kstat has bugs:
      # - quiet and list supports iterating
      # - quiet prints separator between iterations
      if not do_compact: print
      time.sleep(loop_wait)
      ko.chain_update()
    if do_quiet: res = 1
    compact_field_values = []
    if compact_average:
      compact_field_averages = []
    if loop_stamp is not None and not do_compact:
      print loop_stamp[0]()
    compact_fields_values_time = time.time()
    for module,instance,name,ks_class,ks_type,ksp in sorted(ko._iterksp()):
      test0 = [module,instance,name,ks_class,ks_type]
      if not all(m(t) for m,t in zip(check0,test0)): continue
      if not ko._can_parse_value(ksp): continue
      head = 1
      if list_what == 'types':
        if filter_field is not None and not any(check[-1](k) for k in plain_fields):
          if not any(check[-1](k) for k in ko[module,instance,name]): continue
        print '%s:%s:%s\t%s\t%s'%(module,instance,name,ks_class,ks_type)
        continue
      if compact_average:
        dtime = (long(ksp.contents.ks_snaptime)-long(ksp.contents.ks_crtime))/1000000000.0
      if not do_compact and filter_field in plain_fields:
        if filter_field == 'class':
          k,v = filter_field,ks_class
        elif filter_field == 'snaptime':
          k,v = filter_field,ksp.contents.ks_snaptime
        elif filter_field == 'crtime':
          k,v = filter_field,ksp.contents.ks_crtime
        elif filter_field == '-type':
          k,v = filter_field,ks_type
        elif filter_field == '-data-size':
          k,v = filter_field,ks.ks_data_size
        elif filter_field == '-ndata':
          k,v = filter_field,ks.ks_ndata
        elif filter_field == '-flags':
          k,v = filter_field,ks.ks_flags
        head = 0
        if do_verbose:
          print 'module: %-31s instance: %-6s\nname:   %-31s class:    %s' % \
                (module,instance,name,ks_class)
        elif do_quiet:
          pass
        elif do_list:
          print '%s:%s:%s:%s'%(module,instance,name,k)
        elif do_parsable:
          print '%s:%s:%s:%s\t%s'%(module,instance,name,k,v)
      else:
        items = ko[module,instance,name]
        if items is None: items = {}
        #if items is None: items = {'class':ks_class}
        items = items.items()
        if do_debug:
          ks = ksp.contents
          items = itertools.chain(items,[
            ('-type',ks_type),
            ('-data-size',ks.ks_data_size),
            ('-ndata',ks.ks_ndata),
            ('-flags',ks.ks_flags),
          ])
        for k,v in sorted(items):
          test = itertools.chain(test0,[k])
          if not all(m(t) for m,t in zip(check,test)): continue
          if do_verbose and head:
            print 'module: %-31s instance: %-6s\nname:   %-31s class:    %s' % \
                  (module,instance,name,ks_class)
          if head: head = 0
          res = 0
          if do_quiet:
            pass
          elif do_list:
            print '%s:%s:%s:%s'%(module,instance,name,k)
          elif do_compact:
            if k in ('class','snaptime','crtime') or k[:1]=='-' or type(v)==kstat.libkstat.hrtime_t:
              continue
            i = len(compact_field_values)
            if do_parsable:
              if compact_collect:
                k = '%s:%s'%(module,k)
              else:
                k = '%s:%s:%s:%s'%(module,instance,name,k)
            if compact_average:
              dv = v
              try: dv = v/dtime
              except: pass
            if compact_collect and k in compact_field_names:
              ni = compact_field_names.index(k)
              if i==ni:
                compact_field_values.append(v)
                if compact_average:
                  compact_field_averages.append(dv)
              else:
                compact_field_values[ni] += v
                if compact_average:
                  compact_field_averages[ni] += dv
            else:
              if compact_fields_completed:
                if len(compact_field_names) <= i:
                  compact_fields_completed = False
                elif compact_field_names[i] != k:
                  compact_field_names = compact_field_names[:i]
                  compact_field_sizes = compact_field_sizes[:i]
                  compact_fields_completed = False
              if not compact_fields_completed:
                compact_field_names.append(k)
                s = 0
                if not compact_collect:
                  s = min(max(len(k)+2,len(str(v))+3),20)
                compact_field_sizes.append(s)
              compact_field_values.append(v)
              if compact_average:
                compact_field_averages.append(dv)
          elif do_parsable:
            print '%s:%s:%s:%s\t%s'%(module,instance,name,k,v)
          elif k!='class':
            print '\t%-31s %s'%(k,v)
      if do_verbose and not head: print
    if do_compact:
      if not compact_fields_completed:
        for i,(k,v,s) in enumerate(zip(compact_field_names,compact_field_values,compact_field_sizes)):
          if not s:
            compact_field_sizes[i] = min(max(len(k)+2,len(str(v))+1),20)
        if loop_stamp is not None:
          print ' '*len(str(loop_stamp[1]())),
        print ('%*s'*len(compact_field_names))%sum(zip(compact_field_sizes,compact_field_names),())
      l = compact_field_values
      if compact_delta:
        if compact_fields_previous is not None:
          l = []
          for k,v in zip(compact_field_names,compact_field_values):
            if type(v) in (type(0),type(0l)):
              pv = compact_fields_previous.get(k)
              #print '-',k,v,pv
              if pv is not None:
                v -= pv
            #else:
            #  print '?',k,v,type(v)
            l.append(v)
          if compact_average:
            dtime = compact_fields_values_time-compact_fields_previous_time
            l = [round(v/dtime,2) or 0 for v in l]
        elif compact_average:
          l = [round(v,2) or 0 for v in compact_field_averages]
        #else:
        #  l = None
      if l is not None:
        if loop_stamp is not None:
          print loop_stamp[1](),
        print ('%*s'*len(compact_field_names))%sum(zip(compact_field_sizes,l),())
      compact_fields_completed = True
      compact_fields_previous = dict(zip(compact_field_names,compact_field_values))
      compact_fields_previous_time = compact_fields_values_time
  del ko
  return res

if __name__=='__main__':
  try:
    sys.exit(main(sys.argv))
  except KeyboardInterrupt:
    print
