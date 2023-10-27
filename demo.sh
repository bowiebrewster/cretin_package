# Get the argument name from the environment variable
arg_name0=$ARG_NAME0
arg_name1=$ARG_NAME1
cretin_bin_dir=$CRETIN_BIN_DIR
# Add the cretin.v2_19_test/bin directory to the PATH

export PATH="$cretin_bin_dir:$PATH"

# Change directory to the location of the input file
cd $arg_name1

# Execute the cretin_02_19_linux command with the input file
cretin_02_19_linux $arg_name0.gen