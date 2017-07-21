#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

'''
@Author Linwei.Wang@mediatek.com
@Date 2017/7/22 1:37
'''

import os
import re
import sys

def reduce_irq_trace(trace_file, output_file='reduce_irq.m', pattern='irq_'):
        '''
        去除irq部分trace
        '''
        ret = __reduce_pattern_trace(trace_file, output_file, pattern)
        print 'reduce irq trace done!!!'
        return ret

def reduce_softirq_trace(trace_file, output_file='reduce_softirq.m', pattern='softirq_'):
        '''
        去除softirq部分trace
        '''
        ret = __reduce_pattern_trace(trace_file, output_file, pattern)
        print 'reduce softirq trace done!!!'
        return ret;

def reduce_ipi_trace(trace_file, output_file='reduce_ipi.m', pattern='ipi_'):
        '''
        去除ipi部分trace
        '''
        ret = __reduce_pattern_trace(trace_file, output_file, pattern)
        print 'reduce ipi trace done!!!'
        return ret

def __reduce_pattern_trace(trace_file, output_file, pattern):
        '''
        去除含有指定模式字符串的trace行
        '''
        with open(trace_file) as rf, open(output_file, 'wb') as wf:
            for line in rf:
                if pattern in line and not line.startswith('#'):
                    continue
                wf.write(line)
        return output_file

def process_statistic(trace_file):
        '''
        统计systrace中进程信息: pid comm
        '''
        REGEX = r'^.*?-\d{1,6}\s+\[\d{3}\]\s+.{4}\s+\d+\.\d+:\s+sched_wakeup:\s+comm=(.*?)\s+pid=(\d+)\s+prio=(\d+)\s+success=\d+\s+target_cpu=\d{3}\s+state=([DRSTtWXZ][+<NLsl]*)$'
        TITLE = 'pid\tcomm\tprio\tstate'
        print TITLE
        with open(trace_file) as rf:
            for line in rf:
                if line.startswith('#'):
                    continue
                matcher = re.match(REGEX, line, re.DOTALL)
                if matcher:
                    pid = matcher.group(2)
                    comm = matcher.group(1)
                    prio = matcher.group(3)
                    state = matcher.group(4)
                    print 'match: %s\t%s\t%s\t%s' % (pid, comm, prio, state)

def reduce_trace(trace_file, *reduce_pids):
	'''
	解析systrace，去掉指定pid进程的信息
	@trace_file systrace文件
	@reduce_pids 需要去掉信息的进程pid列表
    	'''
        process_statistic(trace_file)
        with open(trace_file) as rf:
            for line in rf:
                if line.startswith('#'):
                    continue
                print 'content found'
                break
        for pid in reduce_pids:
            print 'pid-->', pid

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print 'Usage: %s trace_file reduce_pid1 ...' % sys.argv[0]
		sys.exit(-1)
	#reduce_trace(sys.argv[1], *sys.argv[2:])
        reduce_irq_trace(reduce_softirq_trace(reduce_ipi_trace(sys.argv[1])))
