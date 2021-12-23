from argparse import ArgumentParser


def parse() -> (str, str, int, str | None, bool):
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument('APKFile', type=str, help='Path to the APK file to analyse')
    parser.add_argument('Class', type=str, help='Name of the class to analyse')
    parser.add_argument('Flag', type=int, help='Type of analyse', choices=[1, 2, 3])
    parser.add_argument('-i', '--input', dest='File', type=str, help='Path to the input file (Analyse 3)')
    parser.add_argument('-v', "--verbose", dest='Verbose', action='store_true', help='Verbose mode')

    args = parser.parse_args()

    return args.APKFile, args.Class, args.Flag, args.File, args.Verbose
