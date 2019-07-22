Performance Benchmarking of Java Null Safety Tools
------------
Evaluates build times for Java projects using [NullAway](https://github.com/uber/NullAway), [Checker Framework](https://github.com/typetools/checker-framework)'s [Nullness Checker](https://checkerframework.org/manual/#nullness-checker), and [Eradicate](https://fbinfer.com/docs/eradicate.html).
  - [Setup](#setup)
  - [Usage](#usage)
  - [Helper scripts](#helper-scripts)
  - [Troubleshooting](#troubleshooting)
___

### Setup ###
  * Install [JDK 8](https://docs.oracle.com/javase/8/docs/technotes/guides/install/install_overview.html), [Python 3](https://docs.python.org/3/using/index.html), [pip](https://pip.pypa.io/en/stable/installing/)
  * Install [Checker Framework](https://checkerframework.org/manual/#installation) and [Infer](https://fbinfer.com/docs/getting-started.html)
  * Optional for Android projects: Install [Android SDK Tools](https://developer.android.com/studio/#downloads) and use [sdkmanager](https://developer.android.com/studio/command-line/sdkmanager) to install required packages
  * `mkdir <working_dir> && cd <working_dir>`
  * `git clone git@github.com:subarnob/nullaway-eval.git`
  * `git clone -b sb_compile-bench git@github.com:subarnob/NullAway.git`
  * `cd nullaway-eval`
  * `pip install -r requirements.txt`
  * Update paths in `config.ini`
___

### Usage ###
```
python eval_repos.py [options] [tools] [projects]

Options:
    -w  or -warn              : Log all build warnings; only log first warning by default.
    -d  or -daemon            : Build with warmed up JIT cache on a daemonized compiler.
Tools:
    -ba or -base              : Disable Nullness Checking
    -nu or -nullaway          : NullAway
    -ch or -checkerframework  : Checker Framework's Nullness Checker
    -er or -eradicate         : Infer:Eradicate
  * All tools are used by default.

Projects: project names OR relative paths to root directories.
  * All projects listed in eval_repos.txt are evaluated by default.
```
#### Example ####
```
python eval_repos.py -daemon -nullaway -checkerframework okbuck jib
```
This builds 2 projects- `okbuck` and `jib`, using the 2 tools- NullAway and Checker Framework, with a daemonized compiler.
___

### Helper scripts ###
1. **Plotting build times**:
```
python plot.py [-n|-normalize] [input_file]
```
Expects `input_file` in [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) format, loads `result.csv` by default.  
Generates `<input_file_name>_abs.html` for absolute build times, or `<input_file_name>_norm.html` for normalized build times if `-normalize` option is set.

2. **Summarizing build warnings**:
```
python warns.py <log_file>
```
Generates `warns.txt`.

3. **Finding annotated projects**:  
Searches [GitHub](https://github.com/) for [Gradle](https://gradle.org/) projects that use [NullAway](https://github.com/uber/NullAway). Requires [GitHub API token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) in `~/.ghtoken`.
```
python list_repos.py
```
___

### Troubleshooting ###
If all builds of a project fail, the Gradle build cache is likely invalidated.  
To fix this, re-capture the Gradle compile tasks' arguments:
```
python javac_args.py [projects]
```
