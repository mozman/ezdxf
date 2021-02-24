#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
import sys
import argparse

import os
import glob
import time
import ezdxf
from ezdxf import recover
from ezdxf import EZDXF_TEST_FILES
from itertools import chain

DIRS = [
    "AutodeskSamples/*.dxf",
    "AutodeskProducts/*.dxf",
    "CADKitSamples/*.dxf",
    "*.dxf",
]

files = list(
    chain(*[glob.glob(os.path.join(EZDXF_TEST_FILES, d)) for d in DIRS]))


@pytest.mark.parametrize('filename', files)
def test_readfile(filename):
    try:
        recover.readfile(filename)
    except ezdxf.DXFStructureError:
        pytest.fail(f'{filename}: DXFStructureError in recover mode.')
    else:
        assert True


if __name__ == '__main__':
    import logging
    from ezdxf import bbox, print_config
    from ezdxf.math import Vec3
    import warnings
    # Suppress Matplotlib font replacement warnings
    warnings.filterwarnings("ignore")

    parser = argparse.ArgumentParser("stress")
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="give more output",
    )
    parser.add_argument(
        '-e', '--extends',
        action='store_true',
        help="perform extends calculation",
    )
    parser.add_argument(
        '-c', '--cadkit',
        action='store_true',
        help="use only CADKit samples",
    )
    parser.add_argument(
        '-l', '--log',
        action='store_true',
        help="turn logging on",
    )

    args = parser.parse_args(sys.argv[1:])
    print_config()
    print('-' * 79)
    if args.cadkit:  # only CADKit samples
        files = glob.glob(os.path.join(EZDXF_TEST_FILES, "CADKitSamples/*.dxf"))
    if args.log:
        logging.basicConfig(level=logging.WARNING)

    for name in files:
        print(f'Loading file: "{name}"')
        try:
            t_start = time.perf_counter()
            doc = ezdxf.readfile(name)
            t_read = time.perf_counter()
            auditor = doc.audit()
            t_audit = time.perf_counter()
        except ezdxf.DXFStructureError:
            if args.verbose:
                print('Regular loading function failed, using recover mode.')
            t_start = time.perf_counter()
            doc, auditor = recover.readfile(name)
            t_read = time.perf_counter()
            t_audit = t_read
        if auditor.has_errors and args.verbose:
            print(f'Found {len(auditor.errors)} unrecoverable error(s).')
        if auditor.has_fixes and args.verbose:
            print(f'Fixed {len(auditor.fixes)} error(s).')

        ex_run = 0
        if args.extends:
            ex_start = time.perf_counter()
            extends = bbox.extents(doc.modelspace())
            ex_run = time.perf_counter() - t_start
            if args.verbose:
                extmin = doc.header.get('$EXTMIN')
                extmax = doc.header.get('$EXTMAX')
                if extmin is not None:
                    e1 = Vec3(extmin).round(3)
                    e2 = Vec3(extmax).round(3)
                    print(f"Header var $EXTMIN/$EXTMAX: {e1}; {e2}")
                if extends.has_data:
                    e1 = extends.extmin.round(3)
                    e2 = extends.extmax.round(3)
                    print(f"Calculated $EXTMIN/$EXTMAX: {e1}; {e2}")

        if args.verbose:
            print('Timing: ', end='')
            t_run = t_read - t_start
            print(f" loading: {t_run:.3f}s", end='')
            if t_read != t_audit:
                print(f" audit: {t_audit - t_read:.3f}s", end='')
            if ex_run:
                print(f" extends: {ex_run:.3f}s", end='')
            print()
            print('-' * 79)
