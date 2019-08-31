import pandas as pd
import xml.dom.minidom
import os
import subprocess
import time
import pyscreenshot as ImageGrab
import json

""""
The TourGenerator object is used to generate google earth tours. Assuming the google earth app is installed, opening the 
resulting .kml file will start the tour.

The input csv is expected to contain columns labeled 'latitude' and 'longitude'.
"""


class TourGenerator(object):
    def __init__(self, input_path, output_path=None):
        self.input_path = input_path
        if output_path:
            self.output_path = output_path
        else:
            self.output_path = input_path.replace('.csv', '.kml')
        self.data = pd.read_csv(input_path)
        # The years to capture in the historical tour
        self.years = ['2012', '2013', '2014', '2015', '2016', '2017', '2018']
        # The time to spend flying from one element in tour to the next
        self.fly_time = 1.0
        # The time to wait before proceeding
        self.wait_time = 10.0
        self.cycle_time = self.fly_time + self.wait_time
        self.altitude = 50  # Altitude of virtual camera in meters
        self.address_col = 'site_address'  # Name of column with address

    def create_fly_to(self, kmlDoc, row, size_range=100, year='2010'):
        """ Creates a FlyTo element for the tour """
        row = dict(row)
        flyto = kmlDoc.createElement('gx:FlyTo')
        duration = kmlDoc.createElement('gx:duration')
        duration.appendChild(kmlDoc.createTextNode(str(self.fly_time)))
        flyto.appendChild(duration)

        cameraElement = kmlDoc.createElement('Camera')

        # add timestamp for historical imagery
        timestamp = kmlDoc.createElement('gx:TimeStamp')
        when = kmlDoc.createElement('when')
        date = '{}-06-01'.format(year)  # We set date to May 1st on the year
        when.appendChild(kmlDoc.createTextNode(date))
        timestamp.appendChild(when)
        cameraElement.appendChild(timestamp)

        elements = {
            'latitude': str(row['latitude']),
            'longitude': str(row['longitude']),
            'range': str(size_range),
            'altitude': str(self.altitude),
            'tilt': '0',
            'heading': '0',
        }
        for e in elements:
            element = kmlDoc.createElement(e)
            element.appendChild(kmlDoc.createTextNode(elements[e]))
            cameraElement.appendChild(element)

        flyto.appendChild(cameraElement)
        return flyto

    def wait_element(self, kmlDoc):
        wait = kmlDoc.createElement('gx:Wait')
        duration = kmlDoc.createElement('gx:duration')
        duration.appendChild(kmlDoc.createTextNode(str(self.wait_time)))
        wait.appendChild(duration)
        return wait

    def create_tour(self):
      """ Creates the google earth tour and writes to .kml """
        kmlDoc = xml.dom.minidom.Document()
        kmlElement = kmlDoc.createElementNS(
            'http://earth.google.com/kml/2.2', 'kml')
        kmlElement.setAttribute('xmlns', 'http://earth.google.com/kml/2.2')
        kmlElement.setAttribute(
            'xmlns:gx', 'http://www.google.com/kml/ext/2.2')
        kmlElement = kmlDoc.appendChild(kmlElement)
        documentElement = kmlDoc.createElement('Document')
        documentElement = kmlElement.appendChild(documentElement)
        name = kmlDoc.createElement('name')
        name.appendChild(kmlDoc.createTextNode('A very nice tour'))
        documentElement.appendChild(name)
        openelem = kmlDoc.createElement('open')
        openelem.appendChild(kmlDoc.createTextNode('1'))
        documentElement.appendChild(openelem)

        tourElement = kmlDoc.createElement('gx:Tour')
        name = kmlDoc.createElement('name')
        name.appendChild(kmlDoc.createTextNode('Commercial Tour!'))
        tourElement.appendChild(name)

        playlistElement = kmlDoc.createElement('gx:Playlist')
        # Add each row in csv as a flyto element
        for index, row in self.data.iterrows():
            for year in self.years:
                placemarkElement = self.create_fly_to(kmlDoc, row, year=year)
                playlistElement.appendChild(placemarkElement)
                wait = self.wait_element(kmlDoc)
                playlistElement.appendChild(wait)
        tourElement.appendChild(playlistElement)
        documentElement.appendChild(tourElement)

        kmlFile = open(self.output_path, 'wb')
        kmlFile.write(kmlDoc.toprettyxml('  ', newl='\n', encoding='utf-8'))

    def open_tour(self):
        """ Opens the google earth tour file """
        subprocess.call(['/usr/bin/open', self.output_path])

    def write_metadata(self, row, path):
        """ Writes the metadata associated with a property to json. Requires this metadata to be in the .csv, otherwise
        this step is skipped. """
        try:
            metadata = {}
            metadata['address'] = row['site_address']
            metadata['latitude'] = row['latitude']
            metadata['longitude'] = row['longitude']
            metadata['reroof_permit_issue_date'] = row['reroof_permit_issue_date']
            metadata['reroof_permit_expiration_date'] = row['reroof_permit_expiration_date']
            metadata['reroof_type'] = row['reroof_type']
            with open(path, 'w+') as f:
                json.dump(metadata, f)
        except Exception as e:
            print('Failed to write metadata with error {}'.format(e))

    def capture_tour(self):
        output_dir = os.path.join(os.path.dirname(
            self.output_path), 'tour_images')
        os.makedirs(output_dir, exist_ok=True)
        # Bounding box for screenshot. Adjust depending on the location of your google earth app
        capture_box=(628,232,1396,816)
        resize_box = (512,384)
        for index, row in self.data.iterrows():
            # Directory for property uses address with spaces converted to underscores
            prop_dir = os.path.join(
                output_dir, row[self.address_col].replace(' ', '_'))
            metadata_path = os.path.join(prop_dir, 'metadata.json')
            os.makedirs(prop_dir, exist_ok=True)
            self.write_metadata(row, metadata_path)
            for year in self.years:
                try:
                    img_path = os.path.join(prop_dir, '{}.png'.format(year))
                    start = time.time()
                    im = ImageGrab.grab(bbox=capture_box)
                    im = im.resize(resize_box)
                    print('Captured image for path {}'.format(img_path))
                    im.save(img_path)
                    cap_time = time.time() - start
                    sleep_time = self.cycle_time - cap_time
                    time.sleep(sleep_time)
                    #print('Captured image and stored at {}'.format(img_path))
                except Exception as e:
                    print('Failed to capture / save image with exception {}'.format(e))
