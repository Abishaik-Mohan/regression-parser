import re
import linecache
import sys
from os import path

encountered_scripts = {}
scripts_missing = set()
line_nums = []

# Infrastructure issues to be identified
TFTP_UNREACHABLE = "TFTP unreachable."
SERVER_UNREACHABLE = "Server unreachable."
CONSOLE_FAILURE = "Console Hung."
UPLOAD_FAILURE = "Config/Metric upload failure."
PING_FAILURE = "Ping failure."
CUSTOM_PING_FAILURE = "Unable to ping custom IP."
SPAWN_FAILURE = "Spawn process failure."
VARIABLE_MISSING = "Variable not found."
TRAFFIC_RX_FAILURE = "Traffic not received. Please check if any of the testbed ports are down."


def get_file_length(file):
    """ Returns the length of input file.

    Arguments:
        :file: File whose length is to be found.
    """

    counter = 0
    try:
        with open(file) as f:
            for counter, line in enumerate(f):
                pass
        return counter + 1
    except IOError:
        print("Error computing the file length!")


def is_string_exists(line, script, line_num):
    """ Checks if miscellaneous strings exist in the line. 

    Arguments:
        :line: Log line to be parsed.
        :script: Script name.
        :line_num: Line number.  
    """

    # Fail if the below strings are encountered in the line
    if "has run" in line or "Booted" in line or "ImageVer" in line:
        return 1

    global line_nums

    if line.find(script) != -1:
        # Fail if the script title is encountered in the middle
        if len(line_nums) != 0 and line_num < line_nums[-1]:
            return 1

        flag = 0
        words = line.split(" ")
        for word in words:
            # Pass if test title contains script along with "_ or :"
            if word == script or (word.find(script) != -1 and "_" in word) or (word.find(script) != -1 and ":" in word):
                flag = 1
                break
        if (flag == 0):
            return 1
        else:
            return 0


def is_same_encounter(line, script, line_num):
    """ Returns 1 if a script is encountered twice. Else, returns 0.

    Arguments:
        :line: Log line to be parsed.
        :script: Script whose line number is to be found.
        :line_num: Line number.
    """
    global line_nums

    if script in encountered_scripts:
        line_numbers = encountered_scripts[script]
        # Fail if script is encountered in a previously encountered line
        if line_num in line_numbers:
            return 1
        # Fail if script is encountered in the middle of log runs (before the actual line)
        elif line_num < line_nums[-1]:
            return 1
        elif "has run" in line:
            return 1
        else:
            encountered_scripts[script].append(line_num)
            return 0
    else:
        encountered_scripts[script] = [line_num]
        return 0


def get_scripts(flag=0):
    """Returns a list of all scripts or only failed scripts.

    Arguments:
        :flag: If 0, return failures. Else, return all.
    """

    tests = []
    try:
        with open("TestcaseStatusList.txt", mode='r') as file:
            for line in file:
                testcase = line.split(':')
                script = testcase[0]
                script = re.sub('\s+', '', script)
                status = testcase[1]
                status = re.sub('\s+', '', status)

                if (flag == 0):
                    if(status == "FAILED"):
                        tests.append(script)
                else:
                    tests.append(script)

        return tests

    except (IOError):
        print("Error in extracting failed tests.")


def parse_logs(flag, tests):
    """Returns a list of missing scripts or a list of line numbers.

    Arguments:
        :flag: If 0, return missing scripts. Else, return line numbers.
        :tests: List of all script names.
    """
    global encountered_scripts
    global scripts_missing
    global line_nums
    file_len = get_file_length('report.txt')

    try:
        if tests:
            test_len = len(tests)
            for x in range(0, test_len-1):
                script_start = tests[x]
                script_end = tests[x+1]
                index = 0
                with open("report.txt", mode='r') as file:
                    for line in file:
                        index = index + 1
                        line = re.sub('\n', '', line)
                        # Pass if script is found and miscellaneous strings are not found and script is not previously encountered in the same line
                        if((line.find(script_start) != -1) and (not is_string_exists(line, script_start, index)) and (not is_same_encounter(line, script_start, index))):
                            line_nums.append(index)
                            while index:
                                index += 1
                                l = linecache.getline('report.txt', index)
                                l = re.sub('\n', '', l)
                                if(l.find(script_end) != -1 and (not is_string_exists(l, script_end, index))):
                                    line_nums.append(index-2)
                                    break
                                # If EoF is reached and script_end is still not found
                                if (index >= file_len):
                                    scripts_missing.add(script_end)
                                    break
                            break
                        # If EoF is reached and script_start is still not found
                        if (index >= file_len):
                            scripts_missing.add(script_start)
                            break
    except IOError:
        print("Error parsing logs.")

    if flag == 0:
        encountered_scripts = {}
        line_nums = []
        return scripts_missing
    else:
        if len(line_nums) % 2 == 0:
            line_nums.append(line_nums[-1] + 2)

        line_nums.append(file_len)
        return line_nums


def get_missing_scripts():
    """Returns a list of scripts whose logs could not be found."""

    tests = get_scripts(1)    # Get all test scripts
    scripts_missing = parse_logs(0, tests)
    if scripts_missing is not None:
        return scripts_missing
    else:
        return None


def get_failed_tests():
    """Returns a dictionary of failed tests and its boundaries."""

    test_dict = {}
    tests = get_scripts(1)

    if tests and scripts_missing is not None:
        for script in scripts_missing:
            tests = list(filter((script).__ne__, tests))

    line_nums = parse_logs(1, tests)

    # print('********************** LINE NUMBERS **********************')
    # line_len = len(line_nums)
    # for x in range(0, line_len-1, 2):
    #     print(line_nums[x], line_nums[x+1])

    index = 0
    linenum_length = len(line_nums)

    if tests:
        # Forms a dictionary of all testcases and boundaries
        for counter in range(0, linenum_length-1, 2):
            test_dict[tests[index]] = [
                line_nums[counter], line_nums[counter+1]]
            index += 1

    failed_tests = get_scripts()

    # Retains scripts which have only failed
    if failed_tests:
        failed_tests_set = set(failed_tests)
        for key in list(test_dict):
            if key not in failed_tests_set:
                del test_dict[key]

    if test_dict is not None:
        return test_dict
    else:
        return None


def get_failure_type(text):
    """ Returns the type of infrastructure failure, if present. Else, returns None.

    Arguments:
        :text: Script log to be parsed.
    """

    text = text.lower()

    if "tftp servers" in text:
        return TFTP_UNREACHABLE
    elif "server" in text:
        return SERVER_UNREACHABLE
    elif "uploading" in text:
        return UPLOAD_FAILURE
    elif "pingable ping" in text:
        return PING_FAILURE
    elif "flag pingable" in text:
        return CUSTOM_PING_FAILURE
    elif "spawn id" in text or "exp21 not open" in text:
        return SPAWN_FAILURE
    elif "console hung" in text:
        return CONSOLE_FAILURE
    elif "no such variable" in text:
        return VARIABLE_MISSING
    elif "txrate" in text and "rxrate" in text:
        tx_rate = 0
        rx_rate = 0

        split_text = text.split(" ")
        if "=" in split_text[1]:
            tx_split = split_text[1].split("=")
            tx_rate = int(tx_split[1])
        if "=" in split_text[3]:
            rx_split = split_text[3].split("=")
            rx_rate = int(rx_split[1])

        if tx_rate > 0 and rx_rate == 0:
            return TRAFFIC_RX_FAILURE
        else:
            return None

    return None


def get_infra_failures(failed_tests):
    """ Returns a dictionary of scripts having infrastructure failures.

    Arguments:
        :failed_tests: Dictionary of failed tests and its boundaries.
    """

    infra_failures = {}

    if failed_tests is not None:
        for script in failed_tests:
            infra_failures.setdefault(script, [])

            script_boundaries = failed_tests[script]
            start_boundary = script_boundaries[0]
            end_boundary = script_boundaries[1]

            for line_num in range(start_boundary, end_boundary+1):
                log_line = linecache.getline("report.txt", line_num)
                log_line = re.sub('\n', '', log_line)

                if "[" in log_line and "]" in log_line:
                    split_line = log_line.split("[")
                    if split_line[1][:-1].strip() == "FAILED":
                        failure_type = get_failure_type(split_line[0].strip())

                        if failure_type is not None:
                            infra_failures[script].append(failure_type)

    return infra_failures


if __name__ == "__main__":
    if (path.exists("TestcaseStatusList.txt")):
        failed_tests = get_scripts()
        if not failed_tests:
            sys.exit("No tests have failed!")
    else:
        sys.exit("TestcaseStatusList.txt not found!")

    if (path.exists("report.txt")):
        flag = 0

        missing_scripts = get_missing_scripts()
        # print('********************** MISSING SCRIPTS **********************')
        # print(missing_scripts)
        if missing_scripts is not None:
            for script in missing_scripts:
                if script != "cleanup":
                    flag = 1
                    break
            if flag == 1:
                missing_scripts = list(
                    filter(("cleanup").__ne__, missing_scripts))
                script_string = ', '.join(missing_scripts)
                if len(missing_scripts) == 1:
                    print("Script title '{}' is not appropriately present in the log runs.".format(
                        script_string))
                    print(
                        "Infra failures for the script (if found below) may not be correctly reflected. Please cross-confirm the results.\n")
                else:
                    print("Script titles '{}' are not appropriately present in the log runs.".format(
                        script_string))
                    print(
                        "Infra failures for these scripts (if found below) may not be correctly reflected. Please cross-confirm the results.\n")

        failed_tests = get_failed_tests()
        # print('********************** FAILED TESTS **********************')
        # print(failed_tests)
        if failed_tests is not None:
            flag = 0
            infra_issues = ""
            infra_failures = get_infra_failures(failed_tests)

            for key, value in infra_failures.items():
                if value:
                    flag = 1
                    failure_set = set(value)
                    infra_issues += key + ": " + str(failure_set) + "\n"

            if flag == 1:
                print(
                    "**************************************** INFRASTRUCTURE ISSUES ****************************************")
                print(infra_issues)
            else:
                sys.exit("No infrastructure issues found in the test run.")
        else:
            sys.exit("Error identifying test boundaries.")
    else:
        sys.exit("report.txt not found!")
