# JTLAnalyzer
Simple Jmeter JTL Parser

## Install
Needs python 3, most likely it is already there, if not see https://docs.python-guide.org/starting/install3/linux/

install python packages via
pip3 install pandas, seaborn, matplotlib


# Run
To run the command, give a root directory. 
Have JTLs in root/XX/yy.jtl and XX will be used as experiment name
hopefully this is how you have the data already 

script will find all .jtl file parse them prints results against experiment name of each JTL 

(e.g. output)
  exprement  throughput90p_min  throughput90p_max  latency90p_min  latency90p_max
0       JTL        18137.65    18548.616667          2.0         10.0


throughput values are calculated as follows
1. calculate throughout per each second
2. take the average over 30 moving window
3. take 10th percentile and min and 90th percentile as max

10 and 90th percentile of avg throughput of 30second 
Also it creates plots with throughput latency behavior for each experiment

