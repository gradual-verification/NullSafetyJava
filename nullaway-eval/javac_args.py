from common import *
import re

pattern = "Compiler arguments: "
args_need_value = ["-source","-target","-encoding","-d","-s","-extdirs","-endorseddirs","-sourcepath","-cp","-classpath","-processor","-processorpath","-bootclasspath"]
args_to_remove = ["-g","-Werror","-proc:none","-Xplugin:ErrorProne"]
EP_args = "-Xep(?!Opt).*|-XepOpt:(?!NullAway:AnnotatedPackages=)"
NA_paths = ".*/(jetified-)?nullaway-[\w\.]*\.jar$"
CF_processor_jar = os.path.abspath("cf.jar")
skip_targets = ["AutoDispose:25","picasso:0","picasso:1","caffeine:2"]

def arg_path(repo_url): return arg_prefix+"/"+repo_name(repo_url)+arg_suffix

def process_str(str,pattern,sep=" "):
	return sep.join([s for s in str.split(sep) if not re.match(pattern,s)])

def list_rindex(list, key):
	return max(index for index, value in enumerate(list) if value == key)

def add_arg(arg_list,opt,val="",action='replace',pivot=None):
	try:
		i = list_rindex(arg_list,opt)
		if val:
			if action == 'insert': arg_list.insert(i+(2 if opt in args_need_value else 1),val)
			if action == 'prepend': arg_list[i+1] = val+":"+arg_list[i+1]
			if action == 'replace': arg_list[i+1] = val
	except ValueError:
		i = list_rindex(arg_list,pivot)+(2 if pivot in args_need_value else 1) if pivot in arg_list else 0
		arg_list.insert(i,opt)
		if val: arg_list.insert(i+1,val)

def process_args(args):
	final_args = []
	a = re.sub("-\w+  ","",args).split() # remove options with missing values
	for i in range(len(a)):
		if is_opt(a[i]):
			if (a[i] == "-processorpath"):
				a[i+1] = process_str(a[i+1],NA_paths,":")
			if ((a[i] in args_to_remove) or 
			(a[i] in args_need_value and (is_opt(a[i+1]) or not a[i+1]))): continue
			if re.match(EP_args,a[i]): continue
		final_args.append(a[i])
	add_arg(final_args,"-Xmaxwarns","1")
	return " ".join(final_args)

if daemonBuild and "eradicate" in tools:
	print_and_log("Warning: Cannot daemonize Eradicate!")
	tools.remove("eradicate")
compile_bench_cmd = "./gradlew :compile-bench:run --args='"
compile_bench_na_cmd = "./gradlew :compile-bench-na:run --args='"
bench_arg = "-debug -w 5 -r 5 " if daemonBuild else "-debug -w 0 -r 1 "
infer_cmd = "time -f \"Average running time %E\" "+os.environ['FB_INFER']+"/bin/infer run -a checkers --eradicate -- javac "
def prepare_args(args,tool="base"):
	final_args = args.split()
	if allWarns: add_arg(final_args,"-Xmaxwarns","10000")
	if tool=="nullaway": add_arg(final_args,"-na")
	else: final_args = list(filter(lambda a: not re.match("-Xep.*",a), final_args))
	if tool=="base": add_arg(final_args,"-XepDisableAllChecks")
	if tool=="checkerframework":
		last_opt = list(filter(lambda a: is_opt(a), final_args))[-1]
		CFpath = os.environ['CHECKERFRAMEWORK']
		add_arg(final_args,"-processorpath",CFpath+"/checker/dist/checker.jar:"+CF_processor_jar,'prepend',last_opt)
		add_arg(final_args,"-classpath",CFpath+"/checker/dist/checker-qual.jar",'prepend',last_opt)
		add_arg(final_args,"-processorpath","-Xmaxerrs 10000 -Awarns -Xbootclasspath/p:"+CFpath+"/checker/dist/jdk8.jar -Astubs="+CFpath+"/checker/resources/javadoc.astub",'insert',last_opt)	# TODO: -AsafeDefaultsForUncheckedBytecode
	if tool == "eradicate":
		final_args = [a if is_opt(a) or "$" not in a else "'"+a+"'" for a in final_args]
	final_args = " ".join(final_args)
	if tool=="eradicate": return infer_cmd+final_args
	return (compile_bench_cmd if tool=="checkerframework" else compile_bench_na_cmd)+bench_arg+final_args+"'"

processed_suffix = ".clean"
def process_args_file(repo_url):
	if not os.path.exists(arg_path(repo_url)): capture_javac_args(repo_url)
	arg_file = open(arg_path(repo_url)+processed_suffix,"w")
	name = repo_name(repo_url)
	for i, args in enumerate(list_from_file(arg_path(repo_url))):
		if name+":"+str(i) not in skip_targets:
			arg_file.write(process_args(args)+"\n")
	arg_file.close()

def capture_javac_args(repo_url):
	if not apply_patch(repo_url): return
	print_and_log("> Capture javac args - "+repo_name(repo_url))
	cmd = str_from_file(patch_prefix+"/"+repo_name(repo_url)+"/"+script_file)
	cmd += (" && " if cmd else "")+"./gradlew clean && ./gradlew --no-build-cache build -d"
	cmd_in_repo(repo_url,cmd+"|grep '"+pattern+"'|sed 's/.*"+pattern+"//'>"+os.path.abspath(arg_path(repo_url)))

if not os.path.isdir(arg_prefix): os.system("mkdir -p "+arg_prefix)
if __name__ == "__main__":
	for url in repos:
		get_repo(url)
		capture_javac_args(url)
		process_args_file(url)
