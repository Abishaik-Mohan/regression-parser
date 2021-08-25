import re
import constants
import linecache

from os import path

# Returns the length of the file
def find_file_length(report_file):

    with open(report_file) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

# Returns the list of failed tests
def identify_test_list(test_status_file, flag):

    test_list = []
    file = open(test_status_file, "r")

    for line in file:

        testcase_list = line.split(':')

        test_script = testcase_list[0]
        test_status = testcase_list[1]

        test_script = re.sub('\s+', '', test_script)
        test_status = re.sub('\s+', '', test_status)

        if (flag == 0):
            if(test_status == constants.TEST_FAILED):
                test_list.append(test_script)
        else:
            test_list.append(test_script)

    return test_list

# Returns the line number for the line
def find_line_number(string):

    index = 0
    report_file = constants.REPORT_FILE
    file = open(report_file, "r")

    for line in file:
        index = index + 1
        line = re.sub('\n', '', line)

        if(line.find(string) == -1):
            continue
        else:
            return index

# Returns a dictionary of failed test's boundaries
def identify_fail_test_boundaries(report_file):

    testcases = []
    line_nums = []
    test_dict = {}

    index = 0
    test_status_file = constants.TEST_STATUS_FILE
    report_file = constants.REPORT_FILE

    testcases = identify_test_list(test_status_file, 1)

    inital_test = testcases.pop(0)  # Removes the initial testcase
    initial_line = find_line_number(inital_test)

    file_length = find_file_length(report_file)

    file = open(report_file, "r")

    for test in testcases:
        for line in file:
            index = index + 1
            line = re.sub('\n', '', line)

            if(line.find(test) == -1):
                continue
            else:
                line_nums.append(index-2)  # Appends the end boundary
                line_nums.append(index)    # Appends the start boundary
                break

    testcases.insert(0, inital_test)
    line_nums.insert(0, initial_line)
    line_nums.append(file_length)

    index = 0
    linenum_length = len(line_nums)

    # Forms a dictionary of testcases and boundaries
    for counter in range(0, linenum_length-1, 2):
        test_dict[testcases[index]] = [
            line_nums[counter], line_nums[counter+1]]
        index += 1

    failed_tests = identify_test_list(test_status_file, 0)
    failed_tests_set = set(failed_tests)

    for key in list(test_dict):
        if key not in failed_tests_set:
            del test_dict[key]

    return test_dict

# Returns 0 if infra issue is present, else -1
def parse_logs(report_file, start, end):
    
    for line in range(start, end+1):
        
        particular_line = linecache.getline(report_file, line)
        particular_line = re.sub('\n', '', particular_line)
        

# Identifies the list of infra-failed scripts
def identify_infra_failures(report_file, failed_tests):

    for key in failed_tests:
        
        value = failed_tests[key]
        start_limit = value[0]
        end_limit = value[1]

        result = parse_logs(report_file,start_limit,end_limit)


if __name__ == "__main__":

    test_status_file = constants.TEST_STATUS_FILE
    report_file = constants.REPORT_FILE

    if (path.exists(test_status_file)):
        failed_tests = identify_test_list(test_status_file, 0)
        if not failed_tests:
            print(constants.NO_FAILED_MESSAGE)
            exit
    else:
        print(constants.TESTCASE_FILE_NOT_EXISTS_MESSAGE)
        exit

    if (path.exists(report_file)):
        fail_test_boundaries = identify_fail_test_boundaries(report_file)
        print(fail_test_boundaries)
        # infra_failed_tests = identify_infra_failures(
        #     report_file, fail_test_boundaries)

        # if not infra_failed_tests:
        #     print(constants.NO_INFRA_ISSUE_MESSAGE)
        #     exit
    else:
        print(constants.REPORT_FILE_NOT_EXISTS_MESSAGE)
        exit