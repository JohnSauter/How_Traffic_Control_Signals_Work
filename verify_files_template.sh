#!/bin/bash
# File: verify_files_template.sh, author: John Sauter,
# date: December 23, 2024. 
# This file is executed as verify_files.sh during make check.

diff check_output.txt check_expected_output.txt
diff_result=$?
if [[ $diff_result -ne 0 ]]; then
  exit $diff_result
fi

# End of file verify_files_template.sh
