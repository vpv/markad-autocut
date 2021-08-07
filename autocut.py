"""Autoomatic VDR recording cut script using markad

This script will cut recordings made by VDR (http://www.tvdr.de/) using the
markad tool (https://github.com/kfb77/vdr-plugin-markad/).

This script accepts a single command line argument. It can be a path of a
single .rec directory or a path of VDR series recordings. For example:

python3 autocut.py /mnt/Videos/VDR/Wheeler_Dealers/Some_episode/2021-07-26.20.03.6-0.rec
or
python3 autocut.py /mnt/Videos/VDR/Wheeler_Dealers

This script will replace the original .ts files with the cut .ts file. Be
careful, you might lose data!

TODO:
- Use real logging instead of prints
- Allow changing configuration
- Add type hints
- Add tests


Copyright (C) 2021 Ville-Pekka Vainio

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import time


def is_epgsearch(dpath):
    """Check if the recording was made by epgsearch"""
    recdir = Path(dpath)
    info = recdir / 'info'
    return "epgsearch" in info.read_text()


def has_marks(dpath):
    """Check if the recording already has marks"""
    # Not sure if this is useful
    mpath = Path(dpath) / "marks"
    return mpath.exists()


def markad_successful(dpath):
    """Returns true if marks has more than two marks"""
    mpath = Path(dpath) / "marks"
    with mpath.open() as m_handle:
        line_count = len(m_handle.readlines())
    return line_count > 2


def run_markad(dpath):
    """Run markad for the recording"""
    eppath = Path(dpath)
    command = f"markad --log2rec --loglevel=3 --logocachedir=/tmp --cut nice {eppath}".split()
    #command.insert(0, "echo")
    subprocess.run(command, check=True)


def original_recording_length(dpath):
    """Get recording length for a show"""
    recdir = Path(dpath)
    orig_ts_files = list(recdir.glob("0000?.ts"))
    print(orig_ts_files)
    total = 0
    for ts_file in orig_ts_files:
        command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {ts_file}".split()
        result = subprocess.run(command, capture_output=True, text=True,
                                check=True)
        total += float(result.stdout.partition("\n")[0])
    return total


def get_cut_file_name(dpath):
    """Get the cut file name"""
    recdir = Path(dpath)
    epname = recdir.parts[-2]
    return recdir.joinpath(epname + ".ts")


def cut_recording_length(dpath):
    """Get recording length for a cut recording"""
    ts_file = get_cut_file_name(dpath)
    command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {ts_file}".split()
    result = subprocess.run(command, capture_output=True, text=True,
                            check=True)
    return float(result.stdout.partition("\n")[0])


def already_done(dpath):
    """Check if the done flag exists"""
    return Path(dpath).joinpath("info.autocut").exists()


def move_cut(dpath):
    """Move the cut version to place and run genindex"""
    pdpath = Path(dpath)
    print("move " + str(get_cut_file_name(dpath)) + " to " +
          str(pdpath.joinpath("00001.ts")))
    shutil.move(get_cut_file_name(dpath), pdpath.joinpath("00001.ts"))

    ts_list = pdpath.glob("*.ts")
    for rmpath in ts_list:
        if "00001" not in str(rmpath):
            print("unlink ", rmpath)
            rmpath.unlink()

    command = ["vdr", "--genindex"]
    command.append(dpath)
    subprocess.run(command, check=True)

    # The cut was successful, the marks file is not useful anymore, remove it
    pdpath.joinpath("marks").unlink()


def is_vdr_cut(dpath):
    """Check if the directory is already a VDR cut"""
    return str(Path(dpath).parts[-2]).startswith("%")


def is_del(dpath):
    """Check if the directory is marked as deleted"""
    return str(Path(dpath).parts[-2]).endswith(".del")


def old_enough(dpath):
    """Is the VDR index more than two hours old?"""
    orig_mtime = Path(dpath).joinpath("index").stat().st_mtime
    age = time.time() - orig_mtime
    print("Index age:", age)
    return age > 7200


def init_argparse():
    """Init argparse"""
    parser = argparse.ArgumentParser(
        usage="%(prog)s [FILE]",
        description="Automatic markad cutter")
    parser.add_argument("path", type=Path, help="directory path")
    return parser


def main():
    """The main"""
    parser = init_argparse()
    args = parser.parse_args()
    dest_path = args.path
    if dest_path.joinpath("index").exists():
        index_list = [dest_path.joinpath("index")]
    else:
        index_list = dest_path.glob("*/*.rec/index")

    for i in index_list:
        rec_path = i.parent
        if (already_done(rec_path) or is_vdr_cut(rec_path) or is_del(rec_path)
                or not is_epgsearch(rec_path) or not old_enough(rec_path)):
            print("skipping", rec_path)
            continue
        print("processing", rec_path)
        run_markad(rec_path)

        if not markad_successful(rec_path):
            print("It seems markad could not do the cuts. Exiting.")
            continue
        orig_length = original_recording_length(rec_path)
        cut_length = cut_recording_length(rec_path)
        print("Original length in seconds", orig_length)
        print("Cut length in seconds", cut_length)
        division = cut_length/orig_length
        print("Percentage of the cut length from the original legth", division)
        if division >= 0.55:
            print("The cut length seems ok, will move files")
            move_cut(rec_path)
            Path(rec_path).joinpath("info.autocut").touch(exist_ok=True)
        else:
            print("The cut length was too short, do nothing!")
    print("Done")


if __name__ == "__main__":
    main()
