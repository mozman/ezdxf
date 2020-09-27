#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Tuple
from xml.etree import ElementTree as ET
from pathlib import Path
import json
import ezdxf
from ezdxf.math import Matrix44
from ezdxf.addons import geo

TRACK_DATA = Path(__file__).parent
GPX_NS = {'gpx': 'http://www.topografix.com/GPX/1/1'}


def load_gpx_track(p: Path) -> Iterable[Tuple[float, float]]:
    """ Load all track points from all track segments at once. """
    gpx = ET.parse(p)
    root = gpx.getroot()
    for track_point in root.findall('.//gpx:trkpt', GPX_NS):
        data = track_point.attrib
        # Elevation is not supported by the geo add-on.
        yield float(data['lon']), float(data['lat'])


def add_gpx_track(msp, track_data, layer: str):
    geo_mapping = {
        'type': 'LineString',
        'coordinates': track_data,
    }
    geo_track = geo.GeoProxy.parse(geo_mapping)

    # Project GPS globe (polar) representation longitude, latitude EPSG:4326
    # into 2D cartesian coordinates EPSG:3395
    geo_track.globe_to_map()

    # Load geo data information from the DXF file:
    geo_data = msp.get_geodata()
    if geo_data:
        # Get the transformation matrix and epsg code:
        m, epsg = geo_data.get_crs_transformation()
    else:
        # Identity matrix for DXF files without a geo location reference:
        m = Matrix44()
        epsg = 3395
    # Check if for compatible projection:
    if epsg == 3395:
        # Transform CRS coordinates into DXF WCS:
        geo_track.crs_to_wcs(m)
        # Create DXF entities (LWPOLYLINE)
        for entity in geo_track.to_dxf_entities(dxfattribs={'layer': layer}):
            # Add entity to the modelspace:
            msp.add_entity(entity)
    else:
        print(f'Incompatible CRS EPSG:{epsg}')


def export_geojson(entity, m):
    # Convert DXF entity into a GeoProxy object:
    geo_proxy = geo.proxy(entity)
    # Transform DXF WCS coordinates into CRS coordinates:
    geo_proxy.wcs_to_crs(m)
    # Transform 2D map projection EPSG:3395 into globe (polar)
    # representation EPSG:4326
    geo_proxy.map_to_globe()
    # Export GeoJSON data:
    name = entity.dxf.layer + '.geojson'
    with open(TRACK_DATA / name, 'wt', encoding='utf8') as fp:
        json.dump(geo_proxy.__geo_interface__, fp, indent=2)


def main(dxf_path: Path, out_path: Path, tracks):
    doc = ezdxf.readfile(str(dxf_path))
    msp = doc.modelspace()
    # Load GPX data into DXF
    for index, track_path in enumerate(tracks, 1):
        layer = f'track{index}'
        doc.layers.new(layer, dxfattribs={
            'color': index,
            'lineweight': 50,
        })

        track_data = list(load_gpx_track(track_path))
        add_gpx_track(msp, track_data, layer)

    # Store geo located DXF entities as GeoJSON data:
    # Get the geo location information from the DXF file:
    geo_data = msp.get_geodata()
    if geo_data:
        # Get transformation matrix and epsg code:
        m, epsg = geo_data.get_crs_transformation()
    else:
        # Identity matrix for DXF files without geo reference data:
        m = Matrix44()
    for track in msp.query('LWPOLYLINE'):
        export_geojson(track, m)
    doc.saveas(str(out_path))


if __name__ == '__main__':
    main(
        TRACK_DATA / "Graz_10km_3m.dxf",
        TRACK_DATA / "gpx_tracks.dxf",
        [
            TRACK_DATA / 'track1.gpx',
            TRACK_DATA / 'track2.gpx',
            TRACK_DATA / 'track3.gpx',
        ]
    )
