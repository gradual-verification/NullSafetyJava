import sys, os.path, re, random

repo_pat = ".*\| INFO\: > Build Begin - (\S+) - (\S+)"
cmd_pat = ".*\| DEBUG\: \| command '"
tool_order = ["nullaway", "eradicate", "checkerframework"]
warn_pat = [".*\.java\:\d+\: warning\: \[NullAway\] ((?:\S+) (?:\S+))", ".*\.java\:\d+\: error\: (\S+)", ".*\.java\:\d+\: warning\: \[(\S+)\] "]
noNA_targets = {
	'RIBs': [2,7,8,13,14,15,20,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47],
	'okbuck': [1,2,4,8,11,12,14,15,16,17,18,20,21,22,30,31,32,33,34,35,36,38,39,40],
	'FloatingActionButtonSpeedDial': [1,2],
	'test-ribs': [2,5,6,7,8,13,14,15,22],
	'ColdSnap': [1,2,3,4],
	'OANDAFX': [1,2],
	'caffeine': [2]
}

ncmd = 0
repo = ""
tool = ""
warn_lines = set()
warn_types = {}
skip_targets = []
skip = True

def summary(max=10):
	if repo:
		for typ, line in random.sample(warn_lines, max) if len(warn_lines) > max else warn_lines:
			res.write(line)
			if not warn_types.get(typ): warn_types[typ] = 1
			else: warn_types[typ] += 1
		res.write(">> "+repo+" - "+tool+": "+str(len(warn_lines))+"\n"+str(warn_types)+"\n\n")

if __name__ == "__main__":
	log_file = open(sys.argv[1],"r")
	res = open("warns.txt","w")
	for line in log_file:
		mat = re.findall(repo_pat,line)
		if mat:
			summary()
			repo = mat[0][0]; tool = mat[0][1]; skip_targets = noNA_targets.get(repo,[])
			warn_lines.clear(); warn_types.clear(); ncmd = 0; continue
		if repo and re.findall(cmd_pat,line):
			ncmd += 1; skip = ncmd in skip_targets; continue
		if not skip:
			mat = re.findall(warn_pat[tool_order.index(tool)],line)
			if mat and "/src/test/java/" not in line: warn_lines.add((mat[0], line))
	summary()
	res.close()
	log_file.close()
