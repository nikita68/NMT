import argparse
import os
import subprocess
import shlex
from os import listdir
from os.path import isfile, join
import json


def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def launch_single(args, model_dir, config_path):
    
    assert args.lp in ["de-en", "zh-en"], "Language pair not supported"    

    search_dir = model_dir + "search/"
    search_dir_year = search_dir + args.year + "/"
    search_dir_year_beam = search_dir_year + "beam" + args.beam + "/"

    if not os.path.isdir(search_dir):
        print('Making logs folder: ' + str(search_dir))
        os.mkdir(search_dir)

    if not os.path.isdir(search_dir_year):
        print('Making logs folder: ' + str(search_dir_year))
        os.mkdir(search_dir_year)

    if not os.path.isdir(search_dir_year_beam):
        print('Making logs folder: ' + str(search_dir_year_beam))
        os.mkdir(search_dir_year_beam)

    with open(model_dir + "newbob.data") as json_file:
        data = json_file.readlines()

    if args.use_dev_score:
        data = [x for x in data if "dev_score" in x]
    else:
        data = [x for x in data if "dev_error_output/output_prob" in x]
    data = [x.split()[1] for x in data]
    data = [float(x.split(",")[0]) for x in data]

    # check by list of existing models
    all_available_epochs = [int(f[len("network."):-len(".meta")]) for f in listdir(model_dir + "/net-model/")
                            if isfile(join(model_dir + "/net-model/", f)) is True and
                            f[-len("meta"):] == "meta" and
                            f[:len("network")] == "network" and
                            isint(f[len("network."):-len(".meta")])]
    print("All available epochs: " + str(all_available_epochs))

    data = list(zip(data, range(len(data))))  # now tuple of (dev_score, epoch)     
    data = [d for d in data if d[1] in all_available_epochs]

    data.sort(key=lambda x: x[0])
    epochs_to_launch = data[:args.amount_of_epochs_to_try]

    for dev_score, epoch in epochs_to_launch:
        # TODO: make folder for epoch
        epoch = str(epoch)
        print("Picking epoch " + epoch + " with dev_score " + str(dev_score))
        search_dir_year_beam_epoch = search_dir_year_beam + epoch + "/"

        # Only launch if it hasn't been done before for these settings
        if not os.path.isdir(search_dir_year_beam_epoch):
            print('Making logs folder: ' + str(search_dir_year_beam_epoch))
            os.mkdir(search_dir_year_beam_epoch)
            # Launching of config
            if args.lp == "zh-en":
                path_to_runner = "/work/smt2/makarov/NMT/decode_zh-en.sh"
                launch_command = "qsub -l gpu=1 -l h_rt=1:00:00 -l num_proc=5 -l h_vmem=10G -m abe -cwd {} {} {} {} {} {} {} {}"
                print(args.year)
                if str(args.year) == "2015":
                    test_or_dev = "newsdev"
                    z_year = "2017"
                else:
                    test_or_dev = "newstest"
                    z_year = args.year

                launch_command = launch_command.format(path_to_runner, z_year, config_path, epoch, args.beam,
                                                       search_dir_year_beam_epoch, test_or_dev, args.max_seqs)

            if args.lp == "de-en":
                path_to_runner = "/work/smt2/makarov/NMT/decode_de-en.sh" if not args.exp else "/work/smt2/makarov/NMT/decode_de-en.experiments.sh"
                # path_to_runner = "/work/smt2/makarov/NMT/decode_zh-en.sh"
                launch_command = "qsub -l gpu=1 -l h_rt=1:00:00 -l num_proc=5 -l h_vmem=10G -m abe -cwd {} {} {} {} {} {} {}"
                launch_command = launch_command.format(path_to_runner, args.year, config_path, epoch, args.beam,
                                                       search_dir_year_beam_epoch, args.max_seqs)

            # launch_command = shlex.split(launch_command)
            print('Running: ' + str(launch_command) + ' from ' + model_dir)

            # subprocess.Popen(launch_command, cwd=config_dir)
            subprocess.Popen(launch_command, cwd=model_dir, shell=True)
            print('Launched!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch config')

    parser.add_argument('year', metavar='year', type=str,
                        help='Newstest year to use')
    parser.add_argument('beam', metavar='beam', type=str,
                        help='beam_size to use')

    parser.add_argument('amount_of_epochs_to_try', metavar='amount_of_epochs_to_try', type=int,
                        help='amount of epochs to launch from newbob')

    parser.add_argument('model_dir', metavar='model_dir', type=str,
                        help='Model experiment path')

    parser.add_argument('config_path', metavar='config_path', type=str,
                        help='Path to config')
    
    parser.add_argument('lp', metavar='lp', type=str,
                    help='language pair to use')

    parser.add_argument('--max_seqs', metavar='max_seqs', type=str,
                        help='max_seqs',
                        default="8000",
                        required=False)

    parser.add_argument('--exp',
                        help='When using experimental versions, only de-en',
                        default=False,
                        action='store_true',
                        required=False)


    parser.add_argument('--use_dev_score', dest='use_dev_score', action='store_true')

    args = parser.parse_args()
    launch_single(args, args.model_dir, args.config_path)
