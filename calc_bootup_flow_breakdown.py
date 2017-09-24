#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-

import os
import re
import sys

REGEIES = [
    r'^\s+(\d+)\s+: lk', 
    r'^\s+(\d+\.\d+) :\s+.*?: Kernel_init_done', 
    r'^\s+(\d+\.\d+) :\s+\d+-init\s+: INIT:early-init',
    r'PlaceHolder for kernel init done to early-init',
    r'^\s+(\d+\.\d+) :\s+\d+-init\s+: INIT:late-init',
    r'PlaceHolder for early-init to late-init',
    r'^\s+(\d+\.\d+) :\s+\d+-init\s+: INIT:Mount_START',
    r'^\s+(\d+\.\d+) :\s+\d+-init\s+: INIT:Mount_END',
    r'PlaceHolder for mount_start-->mount_end',
    r'^\s+(\d+\.\d+) :\s+\d+-init\s+: INIT:post-fs$',
    r'^\s+(\d+\.\d+) :\s+\d+-init\s+: INIT:post-fs-data',
    r'PlaceHolder for post-fs-->post-fs-data',
    r'^\s+(\d+\.\d+) :\s+\d+-init\s+: USB ready',
    r'PlaceHolder for post-fs-data-->usb ready',
    r'^\s+(\d+\.\d+) :\s+\d+-vold\s+: vold:decrypt_master_key:START',
    r'^\s+(\d+\.\d+) :\s+\d+-vold\s+: vold:decrypt_master_key:END',
    r'PlaceHolder for decrypt_start-->decrypt_end',
    r'^\s+(\d+\.\d+) :\s+\d+-vold\s+: vold:cryptfs_restart_internal:START',
    r'^\s+(\d+\.\d+) :\s+\d+-vold\s+: vold:cryptfs_restart_internal:END',
    r'PlaceHolder for cryptfs_start-->cryptfs_end',
    r'^\s+(\d+\.\d+) :\s+(\d+)-zygote64\s+: boot_progress_start', 
    r'PlaceHolder for Gap1', 
    r'^\s+(\d+\.\d+) :\s+\d+-main\s+: Zygote:Preload End',  
    r'PlaceHolder for zygote', 
    r'^\s+(\d+\.\d+) :\s+\d+-system_server\s+: Android:PackageManagerService_Start', 
    r'^\s+(\d+\.\d+) :\s+\d+-system_server\s+: Android:PMS_READY', 
    r'PlaceHolder for PMS', 
    r'^\s+(\d+\.\d+) :\s+\d+-system_server\s+: AMS:systemReady', 
    r'PlaceHolder for systemReady', 
    r'^\s+(\d+\.\d+) :\s+\d+-system_server\s+: AMS:AMS_READY', 
    r'PlaceHolder for AMS_READY', 
    r'^\s+(\d+\.\d+) :\s+\d+-system_server\s+: Android:SysServerInit_END', 
    r'PlaceHolder for SysServerInit_END', 
    r'^\s+(\d+\.\d+) :\s+\d+-ActivityManager : AMS:ENABLE_SCREEN', #15
    r'PlaceHolder for ENABLE_SCREEN', 
    r'^\s+(\d+\.\d+) :\s+\d+-.*?\s+: BOOT_Animation:END', 
    r'PlaceHolder for BOOT_Animation:END', 
    r'^\s+(\d+\.\d+) : OFF' 
]   

def parse(bootprof):
    result = ['' for i in range(len(REGEIES))] 
    isFirstZygotePreloadEnd = False
    isFirstInitPostFsData = True
    with open(bootprof) as df:
        for line in df:
            for idx, regex in enumerate(REGEIES):
                matcher = re.match(regex, line, re.DOTALL)
                if matcher:              
                    if idx == 22: # Zygote:Preload End
                        if not isFirstZygotePreloadEnd:
                            isFirstZygotePreloadEnd = True
                            break
                    elif idx == 10: # INIT:post-fs-data
                        if isFirstInitPostFsData:
                            isFirstInitPostFsData = False
                        else:
                            break
                    print 'index:', idx
                    result[idx] =  matcher.group(1)
                    break
    result.insert(0, bootprof)                
    return result
    
def calc_bootup_flow_breakdown(bootprof_folder, result_output_file=r'result.csv'):
    with open(os.path.join(bootprof_folder, result_output_file), 'wb') as wf:
        for root, dirs, files in os.walk(bootprof_folder):
            for f in files:
                if f.startswith('bootprof'):
                    wf.write(','.join(parse(os.path.join(root, f))))
                    wf.write('\n')
    print 'DONE!!!'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s bootprof_folder' % sys.argv[0]
        sys.exit(-1)
    calc_bootup_flow_breakdown(sys.argv[1])