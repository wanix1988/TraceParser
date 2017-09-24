#!/usr/bin/env python2.7
#-*- coding:utf-8 -*-

import os
import re
import sys

OPPO_HELLOWORLD_PKG_NAME = r'com.example.testlaunch'

#必须手动输入主线程号用来过滤主线程的trace
PROCESS_MAIN_THREAD_TRACE = r'-%d\s+\[\d{3}\]'
TRACE_COMMON_PREFIX = r'-(%s)\s+\[\d{3}\]\s+.{4}\s+(\d+\.\d+):'
CPU_SCHED_INFO_TRACE = r'%s sched_' % TRACE_COMMON_PREFIX % r'\d+'
CPU_IDLE_INFO_TRACE = r'%s cpu_' % TRACE_COMMON_PREFIX % r'\d+'
APP_TRACE_COMMON_PREFIX = r'%s tracing_mark_write:\s+%s' % (TRACE_COMMON_PREFIX, r'%s')
PROCESS_TRACE_COMMON_PREFIX = APP_TRACE_COMMON_PREFIX % (r'%s', r'B\|\d+\|')
PROCESS_SYS_TRACE_COMMON_PREFIX = PROCESS_TRACE_COMMON_PREFIX % r'\d+'
PROCESS_APP_TRACE_COMMON_PREFIX = PROCESS_TRACE_COMMON_PREFIX % r'%d'

APP_TRACE_BEGIN_PATTERN = PROCESS_SYS_TRACE_COMMON_PREFIX + r'(.*?)$'
APP_TRACE_END_PATTERN = APP_TRACE_COMMON_PREFIX % (r'\d+', r'E$')

#系统重要流程点
IMPORTANT_SYS_KEY_FLOW_POINT = [
	# <1241>-1241  [001] ...1 252224.837539: tracing_mark_write: B|1000|AppLaunch_dispatchPtr:Up
	r'{prefix}(AppLaunch_dispatchPtr:Up)', # finger up
	#.flyme.launcher-2316  [003] ...1 252224.855007: tracing_mark_write: B|2316|amStartActivity
	r'{prefix}(amStartActivity)', # for launcher amStartActivity
	# <1057>-1057  [000] ...1 252224.862290: tracing_mark_write: B|1000|wmAddStarting
	#r'{prefix}wmAddStarting',
]
#住线程关键流程点
IMPORTANT_MAIN_THREAD_KEY_FLOW_POINT = [
	# Binder_6-1864  [000] ...1 252224.893494: tracing_mark_write: B|1000|Start proc: com.example.testlaunch
	r'{prefix}(Start proc: {launcher_pkg_name})$',
	# mple.testlaunch-20302 [008] ...1 252224.911797: tracing_mark_write: B|20302|PostFork
	r'{prefix}(PostFork)$',
	# mple.testlaunch-20302 [008] ...1 252224.913172: tracing_mark_write: B|20302|RuntimeInit
	r'{prefix}(RuntimeInit)$',
	# mple.testlaunch-20302 [008] ...1 252224.918593: tracing_mark_write: B|20302|ActivityThreadMain
	r'{prefix}(ActivityThreadMain)$',
	# mple.testlaunch-20302 [001] ...1 252224.937355: tracing_mark_write: B|20302|bindApplication
	r'{prefix}(bindApplication)$',
	# mple.testlaunch-20302 [008] ...1 252224.951128: tracing_mark_write: B|20302|activityStart
	r'{prefix}(activityStart)$',
	# mple.testlaunch-20302 [008] ...1 252225.058397: tracing_mark_write: B|20302|Choreographer#doFrame
	r'{prefix}(Choreographer#doFrame)$'
]

result_file = r'breakdown.result.csv'

def __init_trace(main_thread_pid):
	'''
	初始化重要节点正则表达式
	'''
	global IMPORTANT_SYS_KEY_FLOW_POINT, IMPORTANT_MAIN_THREAD_KEY_FLOW_POINT
	for i, line in enumerate(IMPORTANT_SYS_KEY_FLOW_POINT):
		IMPORTANT_SYS_KEY_FLOW_POINT[i] = line.format(prefix=PROCESS_SYS_TRACE_COMMON_PREFIX)
	for i, line in enumerate(IMPORTANT_MAIN_THREAD_KEY_FLOW_POINT):
		if i == 0:
			IMPORTANT_MAIN_THREAD_KEY_FLOW_POINT[i] = line.format(prefix=PROCESS_APP_TRACE_COMMON_PREFIX,
			                                                      launcher_pkg_name=OPPO_HELLOWORLD_PKG_NAME) % int(main_thread_pid)
			continue
		IMPORTANT_MAIN_THREAD_KEY_FLOW_POINT[i] = line.format(prefix=PROCESS_APP_TRACE_COMMON_PREFIX) % int(main_thread_pid)
	#print 'app_ley:', IMPORTANT_MAIN_THREAD_KEY_FLOW_POINT
	#print 'sys_key:', IMPORTANT_SYS_KEY_FLOW_POINT
	print 'Init DONE!!!'


def find_launcher_pid(trace):
	'''
	find the launcher's pid
	'''
	pass

def filter_main_thread_trace(trace, main_thread_pid, output=r'main_thread.trace'):
	'''
	过滤trace中的主线程信息， 存入文件备查
	@trace systrace文件
	@main_thread_pid 主线程pid
	@output 主线程输出文件名
	'''
	main_thread_trace_pattern = PROCESS_MAIN_THREAD_TRACE % int(main_thread_pid)
	print 'main_thread_trace_pattern:', main_thread_trace_pattern
	output_file = os.path.join(os.path.dirname(trace), output)
	with open(trace) as rf, open(output_file, 'wb') as wf:
		for line in rf:
			#print 'line:', line
			if line.startswith('#'):
				wf.write(line)
				continue
			'''
			else:
				matcher = re.search(CPU_SCHED_INFO_TRACE, line, re.DOTALL)
				if matcher:
					wf.write(line)
					continue
				#print 'pattern:', CPU_IDLE_INFO_TRACE
				matcher = re.search(CPU_IDLE_INFO_TRACE, line, re.DOTALL)
				if matcher:
					#print 'cpu_idle:', line
					wf.write(line)
					continue
			'''
			matcher = re.search(main_thread_trace_pattern, line, re.DOTALL)
			if matcher:
				wf.write(line)
	print 'Filter Main Thread Trace Done!!!'
	return output_file

def __is_matching_pattern(trace_line, regex):
	'''
	判断给定文本是否匹配正则表达式
	'''
	matcher = re.search(regex, trace_line, re.DOTALL)
	if matcher:
		return True
	return False

def __top_is_begin_trace(trace_line):
	'''
	判断给定文本行是否是app trace开始行
	'''
	return __is_matching_pattern(trace_line, APP_TRACE_BEGIN_PATTERN)

def __top_is_end_trace(trace_line):
	'''
	判断给定文本行是否是app trace结束
	'''
	return __is_matching_pattern(trace_line, APP_TRACE_END_PATTERN)

def calc_main_thread_key_flow_gap(main_thread_trace_output):
	'''
	计算主线程中阶段耗时
	'''
	stack = []
	with open(main_thread_trace_output) as rf:
		print 'app trace begin pattern:', APP_TRACE_BEGIN_PATTERN
		print 'app trace end pattern:', APP_TRACE_END_PATTERN
		for line in rf:
			#print 'line:', line
			matcher = re.search(APP_TRACE_BEGIN_PATTERN, line, re.DOTALL)
			if matcher:
				#print 'BEGIN', matcher.group()
				# 所有B节点都需入栈, 模式为第一段为文本行内容，第二段为时间戳，第三段是trace内容
				begin_content = line+'@#'+matcher.group(2)+'#@'+matcher.group(3)
				#print 'begin_content:', begin_content
				stack.append(begin_content)
			else:
				matcher = re.search(APP_TRACE_END_PATTERN, line, re.DOTALL)
				if matcher:
					#print 'END', matcher.group()
					# 如果此时栈为空， 则丢弃此次E
					if len(stack) == 0:
						continue
					# 如果栈顶是B，那么E必须和B一起pop，然后计算两者之间的gap
					elif len(stack) > 0 and __top_is_begin_trace(stack[-1]):
						end = float(matcher.group(2))
						top = stack.pop()
						top_content = top.split('@#')
						top_line = top_content[0]
						#print 'top_line:', top_line
						top_content_2 = top_content[1].split('#@')
						top_timestamp = top_content_2[0]
						top_keyword = top_content_2[1]
						# 此处判断是否是关键节点
						# 处理主线程关键结点
						for i, pattern in enumerate(IMPORTANT_MAIN_THREAD_KEY_FLOW_POINT):
							key_matcher = re.search(pattern, top_line, re.DOTALL)
							#print 'BEGIN_MATCH:%d:%s:%s' % (i, pattern, line)
							if key_matcher:
								#print 'begin key match', key_matcher.group()
								begin = float(top_timestamp)
								print 'gap: %s' % top_keyword, begin, end, (end - begin)
								break
					else:
						raise RuntimeError('IllegalStateError')
	print 'STACK:', stack

def get_sys_key_flow_data(trace_line, output_file_obj):
	'''
	获取系统重要流程信息，写入全局输出文件
	@trace_line trace文件中的一行
	@output_file_obj 全局统计结果输出文件
	'''
	for i, pattern in enumerate(IMPORTANT_SYS_KEY_FLOW_POINT):
		matcher = re.search(pattern, trace_line)
		if matcher:
			output_file_obj.write(matcher.group())

def app_launch_breakdown(trace, main_thread_pid):
	'''
	parse the trace file and output the breakdown data
	'''
	output = filter_main_thread_trace(trace, main_thread_pid)
	calc_main_thread_key_flow_gap(output)

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Usage: %s trace main_thread_pid' % sys.argv[0]
		sys.exit(-1)
	__init_trace(sys.argv[2])
	app_launch_breakdown(sys.argv[1], sys.argv[2])
	# for local test X230T
	#__init_trace('20302')
	#app_launch_breakdown('/home/wenix/work/mtk/performance/oppo-helloworld/oppo-helloworld.html', '20302')