import sys
if sys.version_info[0] < 3:
	raise Exception("Must use Python 3!")
import os.path, subprocess, configparser, logging, time, atexit

repo_prefix = "repos"
log_file = "eval.log"
stats_file = "result.csv"

#--- Do NOT change these ---
repo_list = "eval_repos.txt"
patch_prefix = "patches"
script_file = "script.sh"
arg_prefix = "compile_args"
arg_suffix = ".arg"
processors = ["nullaway","base","checkerframework","eradicate","nullsafe","gradual"]

config = configparser.ConfigParser()
config.read('config.ini')
nullaway_root = os.path.abspath(config.get('PATHS','nullaway'))
if not os.path.isdir(nullaway_root):
	exit("Error: NullAway not found!")
os.environ["ANDROID_HOME"] = config.get('PATHS','android_sdk')
os.environ["CHECKERFRAMEWORK"] = config.get('PATHS','checkerframework')
os.environ["FB_INFER"] = config.get('PATHS','infer')

log = logging.getLogger("log")
log.setLevel(logging.DEBUG)
hdlr = logging.FileHandler(log_file)
hdlr.setFormatter(logging.Formatter('%(asctime)s| %(levelname)s: %(message)s'))
log.addHandler(hdlr)

def print_and_log(msg): log.info(msg); print(msg)

def str_from_file(path, default=""):
	if os.path.exists(path):
		return open(path,'r').read().replace('\n','')
	return default

def list_from_file(path):
	ret = []
	if os.path.exists(path):
		for line in open(path, 'r').read().splitlines():
			if not line: break
			if line.startswith('#'): continue
			ret.append(line)
	return ret

nerr = 0
nerr_before = 0
def check_errors():
	global nerr_before
	print("\033[F\t\033[1;3"+("1mFAIL" if nerr > nerr_before else "2mPASS")+" \033[0m")
	nerr_before = nerr

def cmd_in_dir(dir, cmd, subdir="", tag="", outlines=20):
	if not cmd: return
	try:
		output = subprocess.check_output("cd "+dir+"/"+subdir+" && "+cmd,shell=True,stderr=subprocess.STDOUT).decode(encoding='UTF-8')
		log.debug("{}| command '{}' output:\n{}".format(tag,cmd,output))
	except subprocess.CalledProcessError as e:
		output = e.output.decode()
		log.error("{}| command '{}' with return code {}:\n{}".format(tag,e.cmd,e.returncode,output))
		global nerr
		nerr += 1
	return '\n'.join(output.splitlines()[-outlines:])

def is_opt(arg): return arg[0]=='-' if arg else False

start_time = time.time()

allWarns = False
daemonBuild = False
repos = []
tools = []
if len(sys.argv) > 1:
	for arg in sys.argv[1:]:
		if is_opt(arg):
			if arg.lower() in ["-w","-warn"]: allWarns = True
			if arg.lower() in ["-d","-daemon"]: daemonBuild = True
			else: tools.extend(filter(lambda p: p.startswith(arg[1:].lower()), processors))
			sys.argv.remove(arg)
		else:
			url = cmd_in_dir(".","grep "+arg.replace(repo_prefix,'').rstrip('/')+"$ "+repo_list).rstrip()
			if url: repos.append(url)
if len(sys.argv) == 1: repos = list_from_file(repo_list)
if not len(repos): exit("Error: No repos found!")
if not len(tools): tools = processors

def repo_name(repo_url): return repo_url.rpartition('/')[2]
def repo_dir(repo_url): return repo_prefix+"/"+repo_name(repo_url)
def cmd_in_repo(repo_url, cmd, subdir=""): return cmd_in_dir(repo_dir(repo_url), cmd, subdir)

def clean_repo(repo_url):
	if os.path.isdir(repo_dir(repo_url)):
		hash = str_from_file(patch_prefix+"/"+repo_name(repo_url)+"/hash")
		if hash: cmd_in_repo(repo_url,"git checkout -f "+hash)
		else: cmd_in_repo(repo_url,"git stash")
		cmd_in_repo(repo_url,"git clean -fx && echo \"sdk.dir = ${ANDROID_HOME}\" > local.properties && chmod +x ./gradlew || true")

def get_repo(repo_url):
	# if os.path.isdir(repo_dir(repo_url)):
	# 	os.system("rm -rf "+repo_dir(repo_url))
	if not os.path.isdir(repo_dir(repo_url)):
		print_and_log("@ "+repo_name(repo_url)+": downloading...")
		cmd_in_dir(".", "git clone "+repo_url+" "+repo_dir(repo_url))
		clean_repo(repo_url)

def patch_file(repo_url, patch_type):
	if patch_type < len(processors):
		patch_path = patch_prefix+"/"+repo_name(repo_url)+"/"+processors[patch_type]
		if os.path.exists(patch_path):
			return os.path.abspath(patch_path)
	return None

def apply_patch(repo_url, patch_type=0):
	patch = patch_file(repo_url, patch_type)
	if not patch: return False
	print_and_log("@ "+repo_name(repo_url)+": applying patch... "+ patch)
	clean_repo(repo_url)
	cmd_in_repo(repo_url,"git apply "+patch)
	return True

@atexit.register
def exit_fnc():
    if nerr: print_and_log(str(nerr)+" errors: Check log! "+os.path.abspath(log_file))
    print_and_log(time.strftime("%H:%M:%S", time.gmtime(time.time()-start_time)))
