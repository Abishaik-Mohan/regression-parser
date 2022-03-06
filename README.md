# Usage
Download `parser.py` and place it in a particular module's `Report` directory which contains `report.txt` and `TestcaseStatusList.txt`.

Execute the script using:

### `python3 parser.py`

Produces a list of TCL scripts for the batch which have failed due to infrastructure issues or a message indicating no infrastructure failures.

#### `Note`: 
The accuracy of the result is dependent on both the `TestcaseStatusList.txt` and `report.txt`, i.e, all scripts present in `TestcaseStatusList.txt` should be properly reflected in the test titles of `report.txt`. 

If a script contains multiple infra failures, the results would be appended. Check sample outputs below for more details.

# Sample Runs

When testcase titles are properly reflected in `report.txt`, the below output can be observed:

1. `(base) Abishaik's-Macbook-Pro  ~ python3 parser.py`                                                                                
`**************************************** INFRASTRUCTURE ISSUES ****************************************` <br />
`29.3: {'Traffic not received. Please check if any of the testbed ports are down.'}` <br />
`29.24: {'Console Hung.', 'Traffic not received. Please check if any of the testbed ports are down.'}` <br />
`29.25: {'Traffic not received. Please check if any of the testbed ports are down.', 'Config/Metric upload failure.'}` <br />
`29.26: {'Config/Metric upload failure.'}` <br />

2. `(base) Abishaik's-Macbook-Pro  ~ python3 parser.py` <br />
`**************************************** INFRASTRUCTURE ISSUES ****************************************` <br />
`2.3.9: {'Ping failure.'}` <br />
`2.6.2: {'Ping failure.'}` <br />
`5.2.2.8: {'Ping failure.', 'Server unreachable.', 'Unable to ping custom IP.'}` <br />
`5.2.4.8: {'Ping failure.'}` <br />
`5.3.2.10: {'Unable to ping custom IP.'}` <br />

When testcase titles are not properly reflected in `report.txt`, the below output can be observed:

1. `(base) Abishaik's-Macbook-Pro  ~ python3 parser.py` <br />
`Script title '5.2.2.7' is not appropriately present in the log runs.` <br />
`Infra failures for the script (if found below) may not be correctly reflected. Please cross-confirm the results.` <br />
`**************************************** INFRASTRUCTURE ISSUES ****************************************` <br />
`5.5.1.1: {'Traffic not received. Please check if any of the testbed ports are down.'}` <br />
`5.5.1.7: {'Traffic not received. Please check if any of the testbed ports are down.'}` <br />
`5.5.1.11: {'Traffic not received. Please check if any of the testbed ports are down.'}` <br />
`5.12.1.1: {'Spawn process failure.'}` <br />

2. `(base) Abishaik's-Macbook-Pro  ~ python3 parser.py` <br />
`Script title '5.4.3_4' is not appropriately present in the log runs.` <br />
`Infra failures for the script (if found below) may not be correctly reflected. Please cross-confirm the results.` <br />
`**************************************** INFRASTRUCTURE ISSUES ****************************************`<br />
`1.1: {'Server unreachable.'}` <br />
`2.3.3: {'Server unreachable.'}` <br />
`2.3.4: {'Server unreachable.'}` <br />
`1.3.6: {'Traffic not received. Please check if any of the testbed ports are down.'}` <br />
`2.1: {'Server unreachable.'}` <br />
`2.2.5: {'Traffic not received. Please check if any of the testbed ports are down.'}` <br />

In this case, the failures may span multiple scripts until the next script with the title reflected properly is encountered.




