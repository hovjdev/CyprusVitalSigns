import os
import time
import shutil
import argparse

DIRNAME = os.path.dirname(__file__)
OUTPUT_DIR=os.path.join(DIRNAME, "output")
SUBDIR_NAME = "cvs_data_vids"
DAYS=5


def getOldDirs(dirPath, olderThanDays):
    """
    return a list of all subfolders under dirPath older than olderThanDays
    """

    olderThanDays *= 86400 # convert days to seconds
    present = time.time()

    items=[]
    for item in os.listdir(dirPath):
     if os.path.isdir(os.path.join(dirPath, item)):
        items.append(item)

        subDirPath = os.path.join(dirPath, item)
        if (present - os.path.getmtime(subDirPath)) > olderThanDays:
            yield subDirPath

if __name__ == "__main__":

    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-o", "--output", help = f"Provide path to output dir. Default={OUTPUT_DIR}")
    parser.add_argument("-s", "--subdir", help = f"Provide name of the subdir for cleanup. Default={SUBDIR_NAME}")
    parser.add_argument("-d", "--days", help = f"Provide number of days. Folders older than this number of days will be deleted. Default={DAYS}")


    # Read arguments from command line
    args = parser.parse_args()

    if args.output:
        OUTPUT_DIR=args.output

    if args.subdir:
        SUBDIR_NAME=args.subdir

    if args.days:
        DAYS=int(args.days)

    dirname = os.path.join(OUTPUT_DIR, SUBDIR_NAME)
    
    cmd = f"ls -lrth {dirname}"


    os.system(cmd)

    cmd = f"ls -lrth {dirname}"
    dirs = list(getOldDirs(dirPath=dirname, olderThanDays=DAYS))

    print(f"Directories older than {DAYS} days are: {dirs}")
    for dir in dirs:
        print(f'deleting {dir}')
        assert dir != '.'
        assert not dir.startswith('*')
        print(f'deleting {dir}')
        shutil.rmtree(dir)


