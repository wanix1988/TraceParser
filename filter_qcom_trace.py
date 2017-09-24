#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-

import os
import os.path as op
import re
import sys

BEGIN_TRACE_TAG = r'<!-- BEGIN TRACE -->'
END_TRACE_TAG = r'<!-- END TRACE -->'
def drop_systrace_html(trace, output=r'.raw.trace'):
	'''
	去除systrace中的网页显示相关的内容
	'''
	begin_trace = False
	output_file = op.join(op.dirname(trace), op.basename(trace).split('.')[0] + output)
	with open(trace) as rf, open(output_file, 'wb') as wf:
		for line in rf:
			if line.startswith('#'):
				wf.write(line)
				continue
			if BEGIN_TRACE_TAG in line:
				begin_trace = True
			if begin_trace:
				wf.write(line)
			if END_TRACE_TAG in line:
				break
	return begin_trace, output_file

def filter_qcom_tgid_trace(trace, output_prefix='filted-'):
	'''
	去除高通平台的tgid列
	'''
	pattern = r'(\(.{5}\))'
	output_file = op.join(op.dirname(trace), output_prefix+op.basename(trace).split('.')[0])
	with open(trace) as rf, open(output_file, 'wb') as wf:
		for line in rf:
			matcher = re.search(pattern, line, re.DOTALL)
			if matcher:
				line = line.replace(matcher.group(1), '')
				wf.write(line)
	
if __name__ == '__main__':
	for root, dirs, files in os.walk(sys.argv[1]):
		for f in files:
			if f.endswith('.html'):
				begin_trace, trace = drop_systrace_html(op.join(root, f))
				filter_qcom_tgid_trace(trace)
	print 'filter DONE'