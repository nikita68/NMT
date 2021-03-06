import argparse
import os
import subprocess
import shlex


# Usage: python3 launch_config.py <path to config>


def main(args):
    # Directory management
    args.p = os.path.abspath(args.p)
    file_dir = os.path.dirname(args.p)

    file_name_w_extension = os.path.basename(args.p)
    filename, file_extension = os.path.splitext(file_name_w_extension)

    logs_dir = file_dir + '/logs'
    config_dir = file_dir + '/logs/' + filename
    config_log_dir = file_dir + '/logs/' + filename + '/log'

    if not os.path.isdir(logs_dir):
        print('Making logs folder: ' + str(logs_dir))
        os.mkdir(logs_dir)

    if not os.path.isdir(config_dir):
        print('Making config folder: ' + str(config_dir))
        os.mkdir(config_dir)

    if not os.path.isdir(config_log_dir):
        print('Making config log folder: ' + str(config_log_dir))
        os.mkdir(config_log_dir)

    # Launching of config
    path_to_runner = "/work/smt2/makarov/NMT/train.sh" if not args.exp else "/work/smt2/makarov/NMT/train.experiments.sh"
    launch_command = "qsub -l gpu=1 -l h_rt=150:00:00 -l num_proc=5 -l h_vmem={}G -l qname='*1080*|*TITAN*' -m abe -js {} -cwd {} {}"
    launch_command = launch_command.format(args.memory, args.js, path_to_runner, args.p)
       
    #launch_command = shlex.split(launch_command)
    print('Running: ' + str(launch_command) + ' from ' + config_dir)

    #subprocess.Popen(launch_command, cwd=config_dir)
    subprocess.Popen(launch_command, cwd=config_dir, shell=True)
    print('Launched!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch config')
    parser.add_argument('p', metavar='p', type=str,
                        help='path to config that you want to launch')

    parser.add_argument('--memory', metavar='memory', type=str,
                        help='Max memory needed',
                        default="16",
                        required=False)

    parser.add_argument('--js', metavar='js', type=str,
                        help='Priority',
                        default="0",
                        required=False)

    parser.add_argument('--exp',
                        help='When using train.experiments.sh',
                        default=False,
                        action='store_true',
                        required=False)

    args = parser.parse_args()
    main(args)

