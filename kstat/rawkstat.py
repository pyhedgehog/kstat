import ctypes as C

#from /usr/include/sys/sysinfo.h
CPU_IDLE = 0
CPU_USER = 1
CPU_KERNEL = 2
CPU_WAIT = 3
CPU_STATES = 4

W_IO = 0
W_SWAP = 1
W_PIO = 2
W_STATES = 3


class cpu_vminfo_t(C.Structure):
    _fields_ = [
        ('pgrec', C.c_uint),
        ('pgfrec', C.c_uint),
        ('pgin', C.c_uint),
        ('pgpgin', C.c_uint),
        ('pgout', C.c_uint),
        ('pgpgout', C.c_uint),
        ('swapin', C.c_uint),
        ('pgswapin', C.c_uint),
        ('swapout', C.c_uint),
        ('pgswapout', C.c_uint),
        ('zfod', C.c_uint),
        ('dfree', C.c_uint),
        ('scan', C.c_uint),
        ('rev', C.c_uint),
        ('hat_fault', C.c_uint),
        ('as_fault', C.c_uint),
        ('maj_fault', C.c_uint),
        ('cow_fault', C.c_uint),
        ('prot_fault', C.c_uint),
        ('softlock', C.c_uint),
        ('kernel_asflt', C.c_uint),
        ('pgrrun', C.c_uint),
        ('execpgin', C.c_uint),
        ('execpgout', C.c_uint),
        ('execfree', C.c_uint),
        ('anonpgin', C.c_uint),
        ('anonpgout', C.c_uint),
        ('anonfree', C.c_uint),
        ('fspgin', C.c_uint),
        ('fspgout', C.c_uint),
        ('fsfree', C.c_uint),
    ]


class cpu_sysinfo_t(C.Structure):
    _fields_ = [
        #('cpu', C.c_uint*CPU_STATES),
        ('idle', C.c_uint),
        ('user', C.c_uint),
        ('kernel', C.c_uint),
        ('wait', C.c_uint),
        #('wait', C.c_uint*W_STATES),
        ('wait_io', C.c_uint),
        ('wait_swap', C.c_uint),
        ('wait_pio', C.c_uint),
        ('bread', C.c_uint),
        ('bwrite', C.c_uint),
        ('lread', C.c_uint),
        ('lwrite', C.c_uint),
        ('phread', C.c_uint),
        ('phwrite', C.c_uint),
        ('pswitch', C.c_uint),
        ('trap', C.c_uint),
        ('intr', C.c_uint),
        ('syscall', C.c_uint),
        ('sysread', C.c_uint),
        ('syswrite', C.c_uint),
        ('sysfork', C.c_uint),
        ('sysvfork', C.c_uint),
        ('sysexec', C.c_uint),
        ('readch', C.c_uint),
        ('writech', C.c_uint),
        ('rcvint', C.c_uint),
        ('xmtint', C.c_uint),
        ('mdmint', C.c_uint),
        ('rawch', C.c_uint),
        ('canch', C.c_uint),
        ('outch', C.c_uint),
        ('msg', C.c_uint),
        ('sema', C.c_uint),
        ('namei', C.c_uint),
        ('ufsiget', C.c_uint),
        ('ufsdirblk', C.c_uint),
        ('ufsipage', C.c_uint),
        ('ufsinopage', C.c_uint),
        ('inodeovf', C.c_uint),
        ('fileovf', C.c_uint),
        ('procovf', C.c_uint),
        ('intrthread', C.c_uint),
        ('intrblk', C.c_uint),
        ('idlethread', C.c_uint),
        ('inv_swtch', C.c_uint),
        ('nthreads', C.c_uint),
        ('cpumigrate', C.c_uint),
        ('xcalls', C.c_uint),
        ('mutex_adenters', C.c_uint),
        ('rw_rdfails', C.c_uint),
        ('rw_wrfails', C.c_uint),
        ('modload', C.c_uint),
        ('modunload', C.c_uint),
        ('bawrite', C.c_uint),
        ('rw_enters', C.c_uint),
        ('win_uo_cnt', C.c_uint),
        ('win_uu_cnt', C.c_uint),
        ('win_so_cnt', C.c_uint),
        ('win_su_cnt', C.c_uint),
        ('win_suo_cnt', C.c_uint),
    ]


class cpu_syswait_t(C.Structure):
    _fields_ = [
        ('iowait', C.c_int),
        ('swap', C.c_int),
        ('physio', C.c_int),
    ]


class cpu_stat_t(C.Structure):
    _fields_ = [
        ('__cpu_stat_lock', C.c_uint*2),
        ('cpu_sysinfo', cpu_sysinfo_t),
        ('cpu_syswait', cpu_syswait_t),
        ('cpu_vminfo', cpu_vminfo_t),
    ]


class sysinfo_t(C.Structure):
    _fields_ = [
        ('updates', C.c_uint),
        ('runque', C.c_uint),
        ('runocc', C.c_uint),
        ('swpque', C.c_uint),
        ('swpocc', C.c_uint),
        ('waiting', C.c_uint),
    ]


class vminfo_t(C.Structure):
    _fields_ = [
        ('freemem', C.c_uint64),
        ('swap_resv', C.c_uint64),
        ('swap_alloc', C.c_uint64),
        ('swap_avail', C.c_uint64),
        ('swap_free', C.c_uint64),
        ('updates', C.c_uint64),
    ]


# from /usr/include/sys/var.h
class var(C.Structure):
    _fields_ = [
        ('v_buf', C.c_int),
        ('v_call', C.c_int),
        ('v_proc', C.c_int),
        ('v_maxupttl', C.c_int),
        ('v_nglobpris', C.c_int),
        ('v_maxsyspri', C.c_int),
        ('v_clist', C.c_int),
        ('v_maxup', C.c_int),
        ('v_hbuf', C.c_int),
        ('v_hmask', C.c_int),
        ('v_pbuf', C.c_int),
        ('v_sptmap', C.c_int),
        ('v_maxpmem', C.c_int),
        ('v_autoup', C.c_int),
        ('v_bufhwm', C.c_int),
    ]


# from /usr/include/sys/vmmeter.h
class flushmeter(C.Structure):
    _fields_ = [
        ('f_ctx', C.c_uint),
        ('f_segment', C.c_uint),
        ('f_page', C.c_uint),
        ('f_partial', C.c_uint),
        ('f_usr', C.c_uint),
        ('f_region', C.c_uint),
    ]


# from /usr/include/rpc/clnt.h
KNC_STRSIZE = 128

# from /usr/include/sys/utsname.h or /usr/include/limits.h
SYS_NMLN = 257


# from /usr/include/nfs/nfs_clnt.h
class mik_timers(C.Structure):
    _fields_ = [
        ('srtt', C.c_uint32),
        ('deviate', C.c_uint32),
        ('rtxcur', C.c_uint32),
    ]


class mntinfo_kstat(C.Structure):
    _fields_ = [
        ('mik_proto', C.c_char*KNC_STRSIZE),
        ('mik_vers', C.c_uint32),
        ('mik_flags', C.c_uint),
        ('mik_secmod', C.c_uint),
        ('mik_curread', C.c_uint32),
        ('mik_curwrite', C.c_uint32),
        ('mik_timeo', C.c_int),
        ('mik_retrans', C.c_int),
        ('mik_acregmin', C.c_uint),
        ('mik_acregmax', C.c_uint),
        ('mik_acdirmin', C.c_uint),
        ('mik_acdirmax', C.c_uint),
        ('lookup_srtt', C.c_uint32),
        ('lookup_deviate', C.c_uint32),
        ('lookup_rtxcur', C.c_uint32),
        ('_l', C.c_uint32), #filler
        ('read_srtt', C.c_uint32),
        ('read_deviate', C.c_uint32),
        ('read_rtxcur', C.c_uint32),
        ('_r', C.c_uint32), #filler
        ('write_srtt', C.c_uint32),
        ('write_deviate', C.c_uint32),
        ('write_rtxcur', C.c_uint32),
        ('_w', C.c_uint32), #filler
        ('mik_noresponse', C.c_uint32),
        ('mik_failover', C.c_uint32),
        ('mik_remap', C.c_uint32),
        ('mik_curserver', C.c_char*SYS_NMLN),
    ]


# from /usr/include/sys/dnlc.h
class ncstats(C.Structure):
    _fields_ = [
        ('hits', C.c_int),
        ('misses', C.c_int),
        ('enters', C.c_int),
        ('dbl_enters', C.c_int),
        ('long_enter', C.c_int),
        ('long_look', C.c_int),
        ('move_to_front', C.c_int),
        ('purges', C.c_int),
    ]


# from http://src.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fc.h#emlxs_stats
MAX_CHANNEL = 8 # EMLXS_MSI_MAX_INTRS

class emlxs_stats_t(C.Structure):
    _fields_ = [
        ('LinkUp', C.c_uint32),
        ('LinkDown', C.c_uint32),
        ('LinkEvent', C.c_uint32),
        ('LinkMultiEvent', C.c_uint32),

        ('MboxIssued', C.c_uint32),
        ('MboxCompleted', C.c_uint32),
        ('MboxGood', C.c_uint32),
        ('MboxError', C.c_uint32),
        ('MboxBusy', C.c_uint32),
        ('MboxInvalid', C.c_uint32),

        ('IocbIssued', C.c_uint32*MAX_CHANNEL),
        ('IocbReceived', C.c_uint32*MAX_CHANNEL),
        ('IocbTxPut', C.c_uint32*MAX_CHANNEL),
        ('IocbTxGet', C.c_uint32*MAX_CHANNEL),
        ('IocbRingFull', C.c_uint32*MAX_CHANNEL),
        ('IocbThrottled', C.c_uint32),

        ('IntrEvent', C.c_uint32*8),

        ('FcpIssued', C.c_uint32),
        ('FcpCompleted', C.c_uint32),
        ('FcpGood', C.c_uint32),
        ('FcpError', C.c_uint32),

        ('FcpEvent', C.c_uint32),
        ('FcpStray', C.c_uint32),
#ifdef SFCT_SUPPORT
        ('FctRingEvent', C.c_uint32),
        ('FctRingError', C.c_uint32),
        ('FctRingDropped', C.c_uint32),
#endif /* SFCT_SUPPORT */

        ('ElsEvent', C.c_uint32),
        ('ElsStray', C.c_uint32),

        ('ElsCmdIssued', C.c_uint32),
        ('ElsCmdCompleted', C.c_uint32),
        ('ElsCmdGood', C.c_uint32),
        ('ElsCmdError', C.c_uint32),

        ('ElsRspIssued', C.c_uint32),
        ('ElsRspCompleted', C.c_uint32),

        ('ElsRcvEvent', C.c_uint32),
        ('ElsRcvError', C.c_uint32),
        ('ElsRcvDropped', C.c_uint32),
        ('ElsCmdReceived', C.c_uint32),
        ('ElsRscnReceived', C.c_uint32),
        ('ElsFlogiReceived', C.c_uint32),
        ('ElsPlogiReceived', C.c_uint32),
        ('ElsPrliReceived', C.c_uint32),
        ('ElsPrloReceived', C.c_uint32),
        ('ElsLogoReceived', C.c_uint32),
        ('ElsAdiscReceived', C.c_uint32),
        ('ElsAuthReceived', C.c_uint32),
        ('ElsGenReceived', C.c_uint32),

        ('CtEvent', C.c_uint32),
        ('CtStray', C.c_uint32),

        ('CtCmdIssued', C.c_uint32),
        ('CtCmdCompleted', C.c_uint32),
        ('CtCmdGood', C.c_uint32),
        ('CtCmdError', C.c_uint32),

        ('CtRspIssued', C.c_uint32),
        ('CtRspCompleted', C.c_uint32),

        ('CtRcvEvent', C.c_uint32),
        ('CtRcvError', C.c_uint32),
        ('CtRcvDropped', C.c_uint32),
        ('CtCmdReceived', C.c_uint32),

        ('IpEvent', C.c_uint32),
        ('IpStray', C.c_uint32),

        ('IpSeqIssued', C.c_uint32),
        ('IpSeqCompleted', C.c_uint32),
        ('IpSeqGood', C.c_uint32),
        ('IpSeqError', C.c_uint32),

        ('IpBcastIssued', C.c_uint32),
        ('IpBcastCompleted', C.c_uint32),
        ('IpBcastGood', C.c_uint32),
        ('IpBcastError', C.c_uint32),

        ('IpRcvEvent', C.c_uint32),
        ('IpDropped', C.c_uint32),
        ('IpSeqReceived', C.c_uint32),
        ('IpBcastReceived', C.c_uint32),

        ('IpUbPosted', C.c_uint32),
        ('ElsUbPosted', C.c_uint32),
        ('CtUbPosted', C.c_uint32),
#ifdef SFCT_SUPPORT
        ('FctUbPosted', C.c_uint32),
#endif /* SFCT_SUPPORT */
        ('ResetTime', C.c_uint32),
        ('dummy', C.c_uint32*2),
    ]


# from http://src.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/cmd/perl/contrib/Sun/Solaris/Kstat/Kstat.xs
class sfmmu_global_stat(C.Structure):
    _fields_ = [
        ('sf_tsb_exceptions', C.c_int),
        ('sf_tsb_raise_exception', C.c_int),
        ('sf_pagefaults', C.c_int),
        ('sf_uhash_searches', C.c_int),
        ('sf_uhash_links', C.c_int),
        ('sf_khash_searches', C.c_int),
        ('sf_khash_links', C.c_int),
        ('sf_swapout', C.c_int),
        ('sf_tsb_alloc', C.c_int),
        ('sf_tsb_allocfail', C.c_int),
        ('sf_tsb_sectsb_create', C.c_int),
        ('sf_scd_1sttsb_alloc', C.c_int),
        ('sf_scd_2ndtsb_alloc', C.c_int),
        ('sf_scd_1sttsb_allocfail', C.c_int),
        ('sf_scd_2ndtsb_allocfail', C.c_int),
        ('sf_tteload8k', C.c_int),
        ('sf_tteload64k', C.c_int),
        ('sf_tteload512k', C.c_int),
        ('sf_tteload4m', C.c_int),
        ('sf_tteload32m', C.c_int),
        ('sf_tteload256m', C.c_int),
        ('sf_tsb_load8k', C.c_int),
        ('sf_tsb_load4m', C.c_int),
        ('sf_hblk_hit', C.c_int),
        ('sf_hblk8_ncreate', C.c_int),
        ('sf_hblk8_nalloc', C.c_int),
        ('sf_hblk1_ncreate', C.c_int),
        ('sf_hblk1_nalloc', C.c_int),
        ('sf_hblk_slab_cnt', C.c_int),
        ('sf_hblk_reserve_cnt', C.c_int),
        ('sf_hblk_recurse_cnt', C.c_int),
        ('sf_hblk_reserve_hit', C.c_int),
        ('sf_get_free_success', C.c_int),
        ('sf_get_free_throttle', C.c_int),
        ('sf_get_free_fail', C.c_int),
        ('sf_put_free_success', C.c_int),
        ('sf_put_free_fail', C.c_int),
        ('sf_pgcolor_conflict', C.c_int),
        ('sf_uncache_conflict', C.c_int),
        ('sf_unload_conflict', C.c_int),
        ('sf_ism_uncache', C.c_int),
        ('sf_ism_recache', C.c_int),
        ('sf_recache', C.c_int),
        ('sf_steal_count', C.c_int),
        ('sf_pagesync', C.c_int),
        ('sf_clrwrt', C.c_int),
        ('sf_pagesync_invalid', C.c_int),
        ('sf_kernel_xcalls', C.c_int),
        ('sf_user_xcalls', C.c_int),
        ('sf_tsb_grow', C.c_int),
        ('sf_tsb_shrink', C.c_int),
        ('sf_tsb_resize_failures', C.c_int),
        ('sf_tsb_reloc', C.c_int),
        ('sf_user_vtop', C.c_int),
        ('sf_ctx_inv', C.c_int),
        ('sf_tlb_reprog_pgsz', C.c_int),
        ('sf_region_remap_demap', C.c_int),
        ('sf_create_scd', C.c_int),
        ('sf_join_scd', C.c_int),
        ('sf_leave_scd', C.c_int),
        ('sf_destroy_scd', C.c_int),
    ]


class sfmmu_tsbsize_stat(C.Structure):
    _fields_ = [
        ('sf_tsbsz_8k', C.c_int32),
        ('sf_tsbsz_16k', C.c_int32),
        ('sf_tsbsz_32k', C.c_int32),
        ('sf_tsbsz_64k', C.c_int32),
        ('sf_tsbsz_128k', C.c_int32),
        ('sf_tsbsz_256k', C.c_int32),
        ('sf_tsbsz_512k', C.c_int32),
        ('sf_tsbsz_1m', C.c_int32),
        ('sf_tsbsz_2m', C.c_int32),
        ('sf_tsbsz_4m', C.c_int32),
        ('dummy', C.c_int32*6),
    ]


# from http://src.opensolaris.org/source/xref/onnv/onnv-gate/usr/src/uts/sfmmu/vm/hat_sfmmu.h#sfmmu_percpu_stat
class sfmmu_percpu_stat(C.Structure):
    _fields_ = [
        ('sf_itlb_misses', C.c_int),
        ('sf_dtlb_misses', C.c_int),
        ('sf_utsb_misses', C.c_int),
        ('sf_ktsb_misses', C.c_int),
        ('sf_tsb_hits', C.c_int),
        ('sf_umod_faults', C.c_int),
        ('sf_kmod_faults', C.c_int),
    ]


# from http://www.44342.com/oracle-f254-t4193-p1.htm
class ufs_directio_kstats(C.Structure):
    _fields_ = [
        ('logical_reads', C.c_uint),
        ('phys_reads', C.c_uint),
        ('hole_reads', C.c_uint),
        ('nread', C.c_uint),
        ('logical_writes', C.c_uint),
        ('phys_writes', C.c_uint),
        ('nwritten', C.c_uint),
        ('nflushes', C.c_uint),
    ]
