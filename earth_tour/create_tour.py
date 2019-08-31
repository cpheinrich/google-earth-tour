from earth_tour.tour_generator import TourGenerator
import argparse


def main(args):
    tg = TourGenerator(input_path=args.input_csv, output_path=args.output_path)
    tg.create_tour()
    if args.capture:
        tg.open_tour()
        tg.capture_tour()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_csv', default='./sample.csv',
                        help="The path to the input csv file")
    parser.add_argument('--output_path', default=None, help="""Path to .kml file to output. If not supplied,
     it will use the input_csv path using the .kml extension""")
    parser.add_argument('--capture', action='store_false',
                        help="""Whether or not to capture the tour""")
    args = parser.parse_args()
    main(args)
