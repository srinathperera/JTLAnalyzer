import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from os import walk
import sys
import zipfile

def find_all_files(dir):
    experiment_data = []
    for (dirpath, dirnames, filenames) in walk(dir):
        for filename in filenames:
            if ".jtl" in filename:
                experiment_data.append([dirpath.split('/')[-1],
                    dirpath + "/" + filename])
    return experiment_data


def calcuate_throughout_latency_over_window(df):
    min_timestemp =  df["timeStamp"].min()
    df["timestamp_second"] = np.round((df["timeStamp"] - min_timestemp)/1000)
    grouped_df = df.groupby(["timestamp_second"])["Latency"].agg(["count", "mean"]).reset_index()
    grouped_df["throughput_w30"] = grouped_df.rolling(30)["count"].mean()
    grouped_df["latency_w30"] = grouped_df.rolling(30)["mean"].mean()
    grouped_df = grouped_df.dropna()
    #print(grouped_df)
    return grouped_df

def print_value_stats(values):
    percentiles = np.percentile(values, [1, 5, 50, 95, 99])
    output = {"mean" :values.mean(), "stddev": values.std(), "percentiles":percentiles, "max":values.max()}
    return output

def plot_jtl_behaviours(windowed_stats, latency_sample, experiment_name):
    plt.figure(figsize=(20, 10))
    ax = plt.subplot(2, 2, 1)
    ax = sns.lineplot(x="timestamp_second", y="throughput_w30", data=windowed_stats)
    ax = plt.subplot(2, 2, 2)
    ax = sns.lineplot(x="timestamp_second", y="latency_w30", data=windowed_stats)
    ax = plt.subplot(2, 2, 3)
    ax = sns.distplot(windowed_stats["count"])
    ax.set_title("Throughput Distribution")
    ax = plt.subplot(2, 2, 4)
    ax = sns.distplot(latency_sample)
    ax.set_title("Latency Distribution")
    plt.savefig(experiment_name+ ".png")


def parse_jtl(df, experiment_name):
    #print(list(df))

    reading_count = df.shape[0]
    sucess_df = df[df["success"] == True]
    failed_count = reading_count - sucess_df.shape[0]
    print("readings=", reading_count, "failed_count", failed_count, "failed_percentage=", 100.0*failed_count/reading_count)
    print("latency=", print_value_stats(df["Latency"]))

    time_durationMins = (df["timeStamp"].max() - df["timeStamp"].min())/(1000*60)
    print("time_durationMins=", time_durationMins)

    windowed_stats = calcuate_throughout_latency_over_window(df)
    latency_sample = df.sample(min(1000000, df.shape[0]))["Latency"]
    plot_jtl_behaviours(windowed_stats, latency_sample, experiment_name)

    throughput_percentiles = np.percentile(windowed_stats["throughput_w30"], [10, 90])
    latency_percentiles = np.percentile(latency_sample, [10, 90])
    print("throughput_90percentiles, min=", throughput_percentiles[0],"max=" , throughput_percentiles[1])
    print("latency_90percentiles, min=", latency_percentiles[0], "max=", latency_percentiles[1])
    #throughput_min, throughput_max, latency_min, latency_max
    return throughput_percentiles[0], throughput_percentiles[1], latency_percentiles[0], latency_percentiles[1]

#parse_jtl("/Users/srinath/playground/Datasets/SystemsData/JTL/results-measurement-small.jtl")
#parse_jtl("/Users/srinath/playground/Datasets/SystemsData/JTL/results-measurement.jtl")

def parse_with_folder():
    print("received arguments", sys.argv)
    if len(sys.argv) != 2:
        raise Exception("expected one argument, a directory ( which we call root. Have JTLs in root/XX/yy.jtl and XX will be used as experiment name")
    experiment_list = find_all_files(sys.argv[1])
    all_stats = []
    for ex in experiment_list:
        print(ex[0], ex[1])
        df = pd.read_csv(ex[1])
        throughput_min, throughput_max, latency_min, latency_max = parse_jtl(df, ex[0])
        all_stats.append([ex[0], throughput_min, throughput_max, latency_min, latency_max])

    resultsDf = pd.DataFrame(all_stats, columns=["expriement", "throughput90p_min", "throughput90p_max", "latency90p_min", "latency90p_max"])
    resultsDf.to_csv("results.csv")

    #import pandas as pd
    #import zipfile

    #zf = zipfile.ZipFile('C:/Users/Desktop/THEZIPFILE.zip')
    #df = pd.read_csv(zf.open('intfile.csv'))
    print(resultsDf)


def parse_from_zip_file():
    print("received arguments", sys.argv)
    if len(sys.argv) != 2:
        raise Exception(
            "expected one argument, a directory ( which we call root. Have JTLs in root/XX/yy.jtl and XX will be used as experiment name")
    zipped_file = sys.argv[1]
    zf = zipfile.ZipFile(zipped_file)
    zip_file_to_read = None
    for zipfname in zf.namelist():
        if '/results-measurement.jtl' in zipfname:
            zip_file_to_read = zipfname
    if zip_file_to_read is None:
        raise Exception("No results-measurement.jtl found in ", zipped_file, "only found",  zf.namelist())

    print(zf.namelist())
    print("reading ", zip_file_to_read, "entry")
    df = pd.read_csv(zf.open(zip_file_to_read))
    print(list(df))
    experiment_name = zipped_file.split('/')[-1].replace(".zip", "")
    throughput_min, throughput_max, latency_min, latency_max = parse_jtl(df, experiment_name)
    all_stats = [[experiment_name, throughput_min, throughput_max, latency_min, latency_max]]

    resultsDf = pd.DataFrame(all_stats,
                             columns=["expriement", "throughput90p_min", "throughput90p_max", "latency90p_min",
                                      "latency90p_max"])
    resultsDf.to_csv("results.csv")

    # import pandas as pd
    #
    print(resultsDf)

parse_from_zip_file()