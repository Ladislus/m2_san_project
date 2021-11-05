from argparse import ArgumentParser


def parse() -> (str, str, int):
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument('APKFile', type=str, help='Path to the APK file to analyse')
    parser.add_argument('Class', type=str, help='Name of the class to analyse')
    parser.add_argument('Flag', type=int, help='Type of analyse', choices=[1, 2, 3], nargs='?', default=1)

    args = parser.parse_args()

    return args.APKFile, args.Class, args.Flag
