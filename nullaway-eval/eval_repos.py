from common import *
from javac_args import *

import subprocess

def get_time(str):
	sec = 0.0
	times = str.split()[-1].split(":")
	for t in range(len(times)):
		sec += float(times[-t-1])*[1, 60, 3600][t]
	return sec

def parse_out(out):
	time_str = "Average running time "
	for line in out.splitlines():
		if line.startswith(time_str): return get_time(line)
	return 0.0

ncmd = 0
def eval_repo(repo_url, tool):
	if not os.path.exists(arg_path(repo_url)+processed_suffix):
		process_args_file(repo_url)
	print_and_log("> Build Begin - "+repo_name(repo_url)+" - "+tool)
	time = 0.0
	n = 0
	the_list = list_from_file(arg_path(repo_url)+processed_suffix)
	for args in the_list:
		global ncmd
		ncmd += 1
		time += parse_out(cmd_in_dir(nullaway_root, prepare_args(args,tool)))
		pattern = 'cp /home/sam/sandbox/NullSafetyJava-master/NullAway/infer-out/bugs.txt bugs{}.txt'
		padded = str(n).rjust(len(str(len(the_list)-1)), '0')
		subprocess.run(pattern.format(padded), shell=True)
		n += 1
	check_errors()
	return time

if __name__ == "__main__":
	res = open(stats_file,"ab",0)
	for url in repos:
		get_repo(url)
		for tool in tools:
			res.write((repo_name(url)+","+tool+",{:.2f}\n".format(eval_repo(url,tool))).encode("utf-8"))
	res.close()
	print_and_log(str(ncmd)+" compiles.")
