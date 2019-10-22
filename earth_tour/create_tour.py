from earth_tour.tour_generator import TourGenerator
import argparse
import time


def main(args):
    tg = TourGenerator(input_path=args.input_csv, output_path=args.output_path, max_rows=args.max_rows)
    if args.create:
        tg.create_tour()
    if args.capture:
        tg.open_tour()
        time.sleep(6)
        tg.capture_tour(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_csv', default='./sample.csv',
                        help="The path to the input csv file")
    parser.add_argument('--output_path', default=None, help="""Path to .kml file to output. If not supplied,
     it will use the input_csv path using the .kml extension""")
    parser.add_argument('--create', action='store_true',
                        help="""Whether or not to capture the tour""")
    parser.add_argument('--capture', action='store_true',
                        help="""Whether or not to capture the tour""")
    parser.add_argument('--max_rows', type=int,
                        help="""Max number of rows. If not set defaults to all rows""")
    parser.add_argument('--no_reroof', action='store_true',
                        help="Will write that a reroof did not occur in the metadata if passed")
    args = parser.parse_args()
    main(args)
