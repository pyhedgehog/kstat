#!/usr/bin/env python
#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License (the "License").
# You may not use this file except in compliance with the License.
#
# See the License for the specific language governing permissions
# and limitations under the License.
#
#
# Copyright 2011 Grigale Ltd. All rigths reserved.
# Use is subject to license terms.
#

import itertools
import ctypes as C
import libkstat
import rawkstat

safechars = frozenset('0123456789,./;\'[]\\`~!@#$%^&*()_+:"<>?-= abcdefghijklmnopqrstuvwxyz')
def raw_string(s, sz=None):
    def splitby(s, size, step):
        if size is None: size = len(s)
        return reduce(lambda l,i:([l[0][:i],l[0][i:]]+l[1:]),reversed(range(step,size,step)),[s])
    if sz is None: sz = len(s)
    sprt = s[:sz]
    shex = sprt.encode('hex')
    sprt = ''.join(['.',c][c in safechars] for c in sprt)
    sprt = splitby(sprt,sz,16)
    shex = ' '.join(itertools.chain(splitby(shex,sz*2,2),['']))
    shex = splitby(shex,sz*3,16*3)
    shex[-1]+=' '*((-sz%16)*3)
    return '\n\t'+('\n\t'.join(h+p for h,p in zip(shex,sprt)))

class raw:
    def __init__(self, datap, size, prefix=''):
        self.prefix = prefix
        self.datap = datap
        self.value = C.string_at(datap,size)
        self.size = size

    def __repr__(self):
        if self.prefix:
            return '<'+self.prefix+'>'
        return '<%s(%d,%d)>' % (self.__class__.__name__,self.datap,self.size)

    def __str__(self):
        return self.prefix+raw_string(self.value,self.size)

class Kstat():
    def __init__(self, module=None, instance=-1, name=None, _class=None):
        self._ctl = libkstat.kstat_open()
        self._module = module
        if instance is None: instance = -1
        self._inst = instance
        self._name = name
        self._class = _class
        self.debug = False
        self.maxraw = 1024

    def __del__(self):
        libkstat.kstat_close(self._ctl)

    def __str__(self):
        s = 'Module: %s, instance: %s, name: %s'%(self._module, self._inst, self._name) 
        return s

    def __repr__(self):
        s = '<Kstat(%r, %s, %r)>'%(self._module, self._inst, self._name) 
        return s

    def _check_filter(self, ks):
        if self._module is not None and ks.ks_module != self._module:
            #print 'module:', ks.ks_module, '!=', self._module
            return False
        if self._inst != -1 and ks.ks_instance != self._inst:
            #print 'inst:', ks.ks_instance, '!=', self._inst
            return False
        if self._name is not None and ks.ks_name != self._name:
            #print 'name:', ks.ks_name, '!=', self._name
            return False
        if self._class is not None and ks.ks_class != self._class:
            #print 'class:', ks.ks_class, '!=', self._class
            return False
        return True

    def _iterksp(self):
        #ksp = libkstat.kstat_lookup(self._ctl, self._module, self._inst, self._name)
        ksp = self._ctl.contents.kc_chain
        while ksp:
            ks = ksp.contents
            if self._check_filter(ks):
                typename = libkstat.kstat_type_names[ks.ks_type]
                yield ks.ks_module,ks.ks_instance,ks.ks_name,ks.ks_class,typename,ksp
            ksp = ks.ks_next

    def keys(self):
        return list(self.iterkeys())

    def iterkeys(self):
        return ((m,i,n) for m,i,n,c,t,k in self._iterksp())

    __iter__ = iterkeys

    def classes(self):
        return list(self.iterclasses())

    def iterclasses(self):
        return ((m,i,n,c) for m,i,n,c,t,k in self._iterksp())

    def types(self):
        return list(self.itertypes())

    def itertypes(self):
        return ((m,i,n,c,t) for m,i,n,c,t,k in self._iterksp())

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        return (((m,i,n),self._read_value(k)) for m,i,n,c,t,k in self._iterksp())

    def __getitem__(self, triplet):
        if isinstance(triplet, libkstat.kstat):
            ksp = C.pointer(triplet)
        elif isinstance(triplet, libkstat.kstat_p):
            ksp = triplet
        else:
            module, instance, name = triplet
            ksp = libkstat.kstat_lookup(self._ctl, module, instance, name)
        if not ksp:
            raise KeyError(triplet)
        #if self._check_filter(ksp.contents):
        #    raise KeyError(triplet)
        return self._read_value(ksp)

    def chain_update(self):
        return libkstat.kstat_chain_update(self._ctl)

    def _read_value(self, ksp):
        libkstat.kstat_read(self._ctl, ksp, None)
        return self._parse_value(ksp)

    def _parse_value_named(self, ksp, value, datap):
        #print ks.ks_data
        for i in range(ksp.contents.ks_ndata):
            if datap[i].data_type == libkstat.KSTAT_DATA_CHAR:
                value[datap[i].name] = datap[i].value.c
            elif datap[i].data_type == libkstat.KSTAT_DATA_INT32:
                value[datap[i].name] = datap[i].value.i32
            elif datap[i].data_type == libkstat.KSTAT_DATA_UINT32:
                value[datap[i].name] = datap[i].value.ui32
            elif datap[i].data_type == libkstat.KSTAT_DATA_INT64:
                value[datap[i].name] = datap[i].value.i64
            elif datap[i].data_type == libkstat.KSTAT_DATA_UINT64:
                value[datap[i].name] = datap[i].value.ui64
            elif datap[i].data_type == libkstat.KSTAT_DATA_STRING and datap[i].value.str.addr.ptr:
                value[datap[i].name] = C.string_at(datap[i].value.str.addr.ptr,datap[i].value.str.len)
            #else:
            #    value[datap[i].name] = '<named entry(type=%d)>' % (datap[i].data_type,)
            #print datap.contents
            #print dir(datap[i].value)
            #value[datap[i].name] = 0

        return value

    def _parse_value_struct_(self, value, datap):
        for f in zip(*datap.contents._fields_)[0]:
            v = getattr(datap.contents,f)
            #if isinstance(v,C._SimpleCData):
            #    v = v.value
            if isinstance(v,C.Array):
                #for i,av in enumerate(v):
                #    value['%s[%d]'%(f,i)] = av
                #continue
                v = ','.join(str(av) for av in v)
            value[f] = v

        return value

    def _parse_value_intr(self, ksp, value, datap):
        assert ksp.contents.ks_ndata==1
        return self._parse_value_struct_(value, datap)

    def _parse_value_io(self, ksp, value, datap):
        assert ksp.contents.ks_ndata==1
        return self._parse_value_struct_(value, datap)

    def _parse_value_timer(self, ksp, value, datap):
        assert ksp.contents.ks_ndata==1
        return self._parse_value_struct_(value, datap)

    def _parse_ufs_directio_kstats(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==32, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.ufs_directio_kstats)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.ufs_directio_kstats),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.ufs_directio_kstats))
        self._parse_value_struct_(value, datap)
        return value

    def _parse_rawscmn_32_misc_unix_ncstats(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==32, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.ncstats)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.ncstats),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.ncstats))
        self._parse_value_struct_(value, datap)
        return value

    def _parse_rawscmn_244_hat_unix_sfmmu_global_stat(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==244, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.sfmmu_global_stat)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.sfmmu_global_stat),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.sfmmu_global_stat))
        self._parse_value_struct_(value, datap)
        return value

    def _parse_rawscmn_64_hat_unix_sfmmu_tsbsize_stat(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==64, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.sfmmu_tsbsize_stat)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.sfmmu_tsbsize_stat),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.sfmmu_tsbsize_stat))
        self._parse_value_struct_(value, datap)
        #del value['dummy[0]'],value['dummy[1]'],value['dummy[2]'],value['dummy[3]'],value['dummy[4]'],value['dummy[5]']
        del value['dummy']
        return value

    def _parse_rawscmn_24_hat_unix_flushmeter(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==24, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.flushmeter)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.flushmeter),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.flushmeter))
        self._parse_value_struct_(value, datap)
        return value

    def _parse_rawscmn_492_misc_nfs_mntinfo(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==492, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.mntinfo_kstat)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.mntinfo_kstat),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.mntinfo_kstat))
        self._parse_value_struct_(value, datap)
        # remove padders
        del value['_l']
        del value['_r']
        del value['_w']
        return value

    def _parse_rawscm_380_misc_cpu_stat(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==380, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.cpu_stat_t)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.cpu_stat_t),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.cpu_stat_t))
        self._parse_value_struct_(value, C.pointer(datap.contents.cpu_sysinfo))
        self._parse_value_struct_(value, C.pointer(datap.contents.cpu_syswait))
        self._parse_value_struct_(value, C.pointer(datap.contents.cpu_vminfo))
        # patch output to match original kstat (reason unknown)
        del value['rw_enters']
        del value['win_so_cnt']
        del value['win_su_cnt']
        del value['win_suo_cnt']
        del value['win_uo_cnt']
        del value['win_uu_cnt']
        return value

    def _parse_rawscmn_24_misc_unix_sysinfo(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==24, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.sysinfo_t)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.sysinfo_t),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.sysinfo_t))
        self._parse_value_struct_(value, datap)
        return value

    def _parse_rawscmn_60_misc_unix_var(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==60, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.var)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.var),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.var))
        self._parse_value_struct_(value, datap)
        return value

    def _parse_rawscmn_48_vm_unix_vminfo(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==48, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.vminfo_t)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.vminfo_t),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.vminfo_t))
        self._parse_value_struct_(value, datap)
        # for compatibility with original kstat
        del value['updates']
        return value

    def _parse_rawscmn_488_controller_emlxs_statistics(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata==488, "%d!=%d"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        assert C.sizeof(rawkstat.emlxs_stats_t)==ksp.contents.ks_ndata, "%d!=%d"%(C.sizeof(rawkstat.emlxs_stats_t),ksp.contents.ks_ndata)
        datap = C.cast(datap,C.POINTER(rawkstat.emlxs_stats_t))
        self._parse_value_struct_(value, datap)
        # for compatibility with original kstat
        #del value['dummy[0]'],value['dummy[1]']
        del value['dummy']
        return value

    # from http://src.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/uts/common/io/mem.c#mm_kstat_snapshot
    def _parse_rawcmn_misc_mm_phys_installed(self, ksp, value, datap):
        assert ksp.contents.ks_data_size==ksp.contents.ks_ndata*C.sizeof(C.c_uint64)*2, "%d!=%d*%d*2"%(ksp.contents.ks_data_size,ksp.contents.ks_ndata,C.sizeof(C.c_uint64))
        datap = C.cast(datap,C.POINTER(C.c_uint64))
        sz = len(str(max(0,ksp.contents.ks_ndata-1)))
        for i in xrange(ksp.contents.ks_ndata):
            value['memunit[%0*d]'%(sz,i)] = '{addr:0x%08X, size:%d}' % (datap[i*2],datap[i*2+1])
        return value

    # from http://src.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/uts/common/os/mem_cage.c#kcage_kstat_snapshot
    _parse_rawcmn_misc_kcage_kcage_page_list = _parse_rawcmn_misc_mm_phys_installed

    # from http://src.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/uts/common/vm/page_retire.c#pr_list_kstat_snapshot
    _parse_rawcmn_misc_unix_page_retire_list = _parse_rawcmn_misc_mm_phys_installed

    def _parse_rawcmn_kstat_unix_kstat_headers(self, ksp, value, datap):
        datap = C.cast(datap,libkstat.kstat_p)
        for i in itertools.count():
            ks = datap[i]
            if ks.ks_module=='' and ks.ks_name=='' and ks.ks_data_size==ks.ks_instance==ks.ks_kid==0:
                break
            value['kstat[0x%04X]'%(i,)] = '%s:%d:%s' % (ks.ks_module,ks.ks_instance,ks.ks_name)
            #typename = libkstat.kstat_type_names[ks.ks_type]
            #value['kstat[0x%04X]'%(i,)] = ', '.join('%s=%s'%t for t in {
            #    'ks_crtime':ks.ks_crtime,
            #    'ks_kid':ks.ks_kid,
            #    'ks_module':ks.ks_module,
            #    'ks_instance':ks.ks_instance,
            #    'ks_name':ks.ks_name,
            #    'ks_type':ks.ks_type,
            #    'typename':typename,
            #    'ks_class':ks.ks_class,
            #    'ks_flags':ks.ks_flags,
            #    'ks_ndata':ks.ks_ndata,
            #    'ks_data_size':ks.ks_data_size,
            #}.items())
        return value

    def _raw_get_parser(self, ksp):
        size = str(ksp.contents.ks_data_size)
        ksclass = ksp.contents.ks_class
        name = ksp.contents.ks_name
        module = ksp.contents.ks_module
        parser = '_parse_rawscmn_'+size+'_'+ksclass+'_'+module+'_'+name
        func = getattr(self, parser, None)
        if func is None:
            parser = '_parse_rawscm_'+size+'_'+ksclass+'_'+module
            func = getattr(self, parser, None)
        if func is None:
            parser = '_parse_rawsmn_'+size+'_'+module+'_'+name
            func = getattr(self, parser, None)
        if func is None:
            parser = '_parse_rawsm_'+size+'_'+module
            func = getattr(self, parser, None)
        if func is None:
            parser = '_parse_rawsc_'+size+'_'+ksclass
            func = getattr(self, parser, None)
        if func is None:
            parser = '_parse_rawcmn_'+ksclass+'_'+module+'_'+name
            func = getattr(self, parser, None)
        if func is None:
            parser = '_parse_rawcm_'+ksclass+'_'+module
            func = getattr(self, parser, None)
        if func is None:
            parser = '_parse_rawmn_'+module+'_'+name
            func = getattr(self, parser, None)
        if func is None:
            parser = '_parse_rawm_'+module
            func = getattr(self, parser, None)
        if func is None:
            parser = None
        return parser,func

    def _can_parse_value_raw(self, ksp):
        parser,func = self._raw_get_parser(ksp)
        if func is not None: return True
        return not (self.maxraw == 0 and not self.debug)

    def _parse_value_raw(self, ksp, value, datap):
        parser,func = self._raw_get_parser(ksp)
        if func is not None:
            if self.debug: value['-parser'] = parser
            return func(ksp, value, datap)
        info = "raw data (rs_data_size=%d, rs_ndata=%d)" % (ksp.contents.ks_data_size,ksp.contents.ks_ndata)
        if self.maxraw == 0 and not self.debug: return None
        size = ksp.contents.ks_data_size
        if self.maxraw is not None:
            size = min(size, self.maxraw)
        if size:
            value['raw'] = raw(datap, size, info)
        else:
            value['raw'] = info
        return value

    def _can_parse_value(self, ksp):
        ks = ksp.contents
        typename = libkstat.kstat_type_names[ks.ks_type]
        datap = getattr(ks.ks_data, typename)
        parser = '_parse_value_'+typename
        func = getattr(self, parser, None)
        if func is None: return False
        func = getattr(self, '_can_parse_value_'+typename, None)
        if func is None: return True
        return func(ksp)

    def _parse_value(self, ksp):
        ks = ksp.contents
        value = {
            'class':ks.ks_class,
            'crtime':ks.ks_crtime,
            'snaptime':ks.ks_snaptime,
        }

        typename = libkstat.kstat_type_names[ks.ks_type]
        datap = getattr(ks.ks_data, typename)
        parser = '_parse_value_'+typename
        if self.debug: value['-parser'] = parser
        func = getattr(self, parser)
        return func(ksp, value, datap)

    def dump(self):
        kc = self._ctl.contents
        ksp = kc.kc_chain
        while ksp:
            ks = ksp.contents
            print ks.ks_module, ks.ks_instance, ks.ks_name, libkstat.kstat_type_names[ks.ks_type], ks.ks_class, ks.ks_ndata, ks.ks_data_size
            ksp = ks.ks_next
        pass 

Kstat.__dict__['_parse_rawscmn_32_ufs directio_ufs directio_UFS DirectIO Stats'] = Kstat._parse_ufs_directio_kstats

class KstatValue():
    pass


class NamedKstat(KstatValue):
    def __init__(self):
        pass


def main():
    import pprint as pp
    k = Kstat()
    pp.pprint(k)
    #k.dump()
    pp.pprint(k['unix', 0, 'kstat_types'])
    #pp.pprint(k['unix', 0, 'zio_data_buf2560'])
    #pp.pprint(k['audiohd', 0, 'engine_0'])
    pp.pprint(k.classes())
    #k.chain_update()


def test():
    k = Kstat()
    d = k['unix',0,'kstat_types']
    del d['snaptime'],d['crtime']
    assert d == {
            'class':'kstat',
            'event_timer':libkstat.KSTAT_TYPE_TIMER,
            'i/o':libkstat.KSTAT_TYPE_IO,
            'interrupt':libkstat.KSTAT_TYPE_INTR,
            'name=value':libkstat.KSTAT_TYPE_NAMED,
            'raw':libkstat.KSTAT_TYPE_RAW,
        }

if __name__ == '__main__':
    main()
