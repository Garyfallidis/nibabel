# emacs: -*- mode: python-mode; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the NiBabel package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
from __future__ import division, print_function, absolute_import

from os.path import join as pjoin, dirname
import sys
import warnings

import numpy as np

import nibabel.gifti as gi
from nibabel.gifti.util import gifti_endian_codes
from nibabel.loadsave import load, save
from nibabel.nifti1 import xform_codes
from nibabel.tmpdirs import InTemporaryDirectory

from numpy.testing import assert_array_equal, assert_array_almost_equal

from nose.tools import (assert_true, assert_false, assert_equal,
                        assert_raises)
from ...testing import clear_and_catch_warnings


IO_DATA_PATH = pjoin(dirname(__file__), 'data')

DATA_FILE1 = pjoin(IO_DATA_PATH, 'ascii.gii')
DATA_FILE2 = pjoin(IO_DATA_PATH, 'gzipbase64.gii')
DATA_FILE3 = pjoin(IO_DATA_PATH, 'label.gii')
DATA_FILE4 = pjoin(IO_DATA_PATH, 'rh.shape.curv.gii')
# The base64bin file uses non-standard encoding and endian strings, and has
# line-breaks in the base64 encoded data, both of which will break other
# readers, such as Connectome workbench; for example:
# wb_command -gifti-convert ASCII base64bin.gii test.gii
DATA_FILE5 = pjoin(IO_DATA_PATH, 'base64bin.gii')
DATA_FILE6 = pjoin(IO_DATA_PATH, 'rh.aparc.annot.gii')

datafiles = [DATA_FILE1, DATA_FILE2, DATA_FILE3, DATA_FILE4, DATA_FILE5, DATA_FILE6]
numDA = [2, 1, 1, 1, 2, 1]

DATA_FILE1_darr1 = np.array(
       [[-16.07201 , -66.187515,  21.266994],
       [-16.705893, -66.054337,  21.232786],
       [-17.614349, -65.401642,  21.071466]])
DATA_FILE1_darr2 = np.array( [0,1,2] )

DATA_FILE2_darr1 = np.array([[ 0.43635699],
       [ 0.270017  ],
       [ 0.133239  ],
       [ 0.35054299],
       [ 0.26538199],
       [ 0.32122701],
       [ 0.23495001],
       [ 0.26671499],
       [ 0.306851  ],
       [ 0.36302799]], dtype=np.float32)

DATA_FILE3_darr1 = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0])

DATA_FILE4_darr1 = np.array([[-0.57811606],
       [-0.53871965],
       [-0.44602534],
       [-0.56532663],
       [-0.51392376],
       [-0.43225467],
       [-0.54646534],
       [-0.48011276],
       [-0.45624232],
       [-0.31101292]], dtype=np.float32)

DATA_FILE5_darr1 = np.array([[ 155.17539978,  135.58103943,   98.30715179],
       [ 140.33973694,  190.0491333 ,   73.24776459],
       [ 157.3598938 ,  196.97969055,   83.65809631],
       [ 171.46174622,  137.43661499,   78.4709549 ],
       [ 148.54592896,   97.06752777,   65.96373749],
       [ 123.45701599,  111.46841431,   66.3571167 ],
       [ 135.30892944,  202.28720093,   36.38148499],
       [ 178.28155518,  162.59469604,   37.75128937],
       [ 178.11087036,  115.28820038,   57.17986679],
       [ 142.81582642,   82.82115173,   31.02205276]], dtype=np.float32)

DATA_FILE5_darr2 = np.array([[ 6402, 17923, 25602],
       [14085, 25602, 17923],
       [25602, 14085,  4483],
       [17923,  1602, 14085],
       [ 4483, 25603, 25602],
       [25604, 25602, 25603],
       [25602, 25604,  6402],
       [25603,  3525, 25604],
       [ 1123, 17922, 12168],
       [25604, 12168, 17922]], dtype=np.int32)

DATA_FILE6_darr1 = np.array([9182740, 9182740, 9182740], dtype=np.float32)


def test_read_ordering():
    # DATA_FILE1 has an expected darray[0].data shape of (3,3).  However if we
    # read another image first (DATA_FILE2) then the shape is wrong
    # Read an image
    img2 = load(DATA_FILE2)
    assert_equal(img2.darrays[0].data.shape, (143479, 1))
    # Read image for which we know output shape
    img = load(DATA_FILE1)
    assert_equal(img.darrays[0].data.shape, (3,3))


def test_load_metadata():
    for i, dat in enumerate(datafiles):
        img = load(dat)
        me = img.meta
        assert_equal(numDA[i], img.numDA)
        assert_equal(img.version,'1.0')


def test_metadata_deprecations():
    img = load(datafiles[0])
    me = img.meta

    # Test deprecation
    with clear_and_catch_warnings() as w:
        warnings.filterwarnings('once', category=DeprecationWarning)
        assert_equal(me, img.get_meta())

    with clear_and_catch_warnings() as w:
        warnings.filterwarnings('once', category=DeprecationWarning)
        img.set_metadata(me)
    assert_equal(me, img.meta)


def test_load_dataarray1():
    img1 = load(DATA_FILE1)
    # Round trip
    with InTemporaryDirectory():
        save(img1, 'test.gii')
        bimg = load('test.gii')
    for img in (img1, bimg):
        assert_array_almost_equal(img.darrays[0].data, DATA_FILE1_darr1)
        assert_array_almost_equal(img.darrays[1].data, DATA_FILE1_darr2)
        me=img.darrays[0].meta.metadata
        assert_true('AnatomicalStructurePrimary' in me)
        assert_true('AnatomicalStructureSecondary' in me)
        assert_equal(me['AnatomicalStructurePrimary'], 'CortexLeft')
        assert_array_almost_equal(img.darrays[0].coordsys.xform, np.eye(4,4))
        assert_equal(xform_codes.niistring[img.darrays[0].coordsys.dataspace],'NIFTI_XFORM_TALAIRACH')
        assert_equal(xform_codes.niistring[img.darrays[0].coordsys.xformspace],'NIFTI_XFORM_TALAIRACH')


def test_load_dataarray2():
    img2 = load(DATA_FILE2)
    # Round trip
    with InTemporaryDirectory():
        save(img2, 'test.gii')
        bimg = load('test.gii')
    for img in (img2, bimg):
        assert_array_almost_equal(img.darrays[0].data[:10], DATA_FILE2_darr1)


def test_load_dataarray3():
    img3 = load(DATA_FILE3)
    with InTemporaryDirectory():
        save(img3, 'test.gii')
        bimg = load('test.gii')
    for img in (img3, bimg):
        assert_array_almost_equal(img.darrays[0].data[30:50], DATA_FILE3_darr1)


def test_load_dataarray4():
    img4 = load(DATA_FILE4)
    # Round trip
    with InTemporaryDirectory():
        save(img4, 'test.gii')
        bimg = load('test.gii')
    for img in (img4, bimg):
        assert_array_almost_equal(img.darrays[0].data[:10], DATA_FILE4_darr1)


def test_dataarray5():
    img5 = load(DATA_FILE5)
    for da in img5.darrays:
        assert_equal(gifti_endian_codes.byteorder[da.endian], 'little')
    assert_array_almost_equal(img5.darrays[0].data, DATA_FILE5_darr1)
    assert_array_almost_equal(img5.darrays[1].data, DATA_FILE5_darr2)
    # Round trip tested below


def test_base64_written():
    with InTemporaryDirectory():
        with open(DATA_FILE5, 'rb') as fobj:
            contents = fobj.read()
        # Confirm the bad tags are still in the file
        assert_true(b'GIFTI_ENCODING_B64BIN' in contents)
        assert_true(b'GIFTI_ENDIAN_LITTLE' in contents)
        # The good ones are missing
        assert_false(b'Base64Binary' in contents)
        assert_false(b'LittleEndian' in contents)
        # Round trip
        img5 = load(DATA_FILE5)
        save(img5, 'fixed.gii')
        with open('fixed.gii', 'rb') as fobj:
            contents = fobj.read()
        # The bad codes have gone, replaced by the good ones
        assert_false(b'GIFTI_ENCODING_B64BIN' in contents)
        assert_false(b'GIFTI_ENDIAN_LITTLE' in contents)
        assert_true(b'Base64Binary' in contents)
        if sys.byteorder == 'little':
            assert_true(b'LittleEndian' in contents)
        else:
            assert_true(b'BigEndian' in contents)
        img5_fixed = load('fixed.gii')
        darrays = img5_fixed.darrays
        assert_array_almost_equal(darrays[0].data, DATA_FILE5_darr1)
        assert_array_almost_equal(darrays[1].data, DATA_FILE5_darr2)


def test_readwritedata():
    img = load(DATA_FILE2)
    with InTemporaryDirectory():
        save(img, 'test.gii')
        img2 = load('test.gii')
        assert_equal(img.numDA,img2.numDA)
        assert_array_almost_equal(img.darrays[0].data,
                                  img2.darrays[0].data)


def test_write_newmetadata():
    img = gi.GiftiImage()
    attr = gi.GiftiNVPairs(name = 'mykey', value = 'val1')
    newmeta = gi.GiftiMetaData(attr)
    img.meta = newmeta
    myme = img.meta.metadata
    assert_true('mykey' in myme)
    newmeta = gi.GiftiMetaData.from_dict( {'mykey1' : 'val2'} )
    img.meta = newmeta
    myme = img.meta.metadata
    assert_true('mykey1' in myme)
    assert_false('mykey' in myme)


def test_load_getbyintent():
    img = load(DATA_FILE1)
    da = img.get_arrays_from_intent("NIFTI_INTENT_POINTSET")
    assert_equal(len(da), 1)

    with clear_and_catch_warnings() as w:
        warnings.filterwarnings('once', category=DeprecationWarning)
        da = img.getArraysFromIntent("NIFTI_INTENT_POINTSET")
        assert_equal(len(da), 1)
        assert_equal(len(w), 1)
        assert_equal(w[0].category, DeprecationWarning)

    da = img.get_arrays_from_intent("NIFTI_INTENT_TRIANGLE")
    assert_equal(len(da), 1)

    da = img.get_arrays_from_intent("NIFTI_INTENT_CORREL")
    assert_equal(len(da), 0)
    assert_equal(da, [])


def test_load_labeltable():
    img6 = load(DATA_FILE6)
    # Round trip
    with InTemporaryDirectory():
        save(img6, 'test.gii')
        bimg = load('test.gii')
    for img in (img6, bimg):
        assert_array_almost_equal(img.darrays[0].data[:3], DATA_FILE6_darr1)
        assert_equal(len(img.labeltable.labels), 36)
        labeldict = img.labeltable.get_labels_as_dict()
        assert_true(660700 in labeldict)
        assert_equal(labeldict[660700], 'entorhinal')
        assert_equal(img.labeltable.labels[1].key, 2647065)
        assert_equal(img.labeltable.labels[1].red, 0.0980392)
        assert_equal(img.labeltable.labels[1].green, 0.392157)
        assert_equal(img.labeltable.labels[1].blue, 0.156863)
        assert_equal(img.labeltable.labels[1].alpha, 1)


def test_labeltable_deprecations():
    img = load(DATA_FILE6)
    lt = img.labeltable

    # Test deprecation
    with clear_and_catch_warnings() as w:
        warnings.filterwarnings('once', category=DeprecationWarning)
        assert_equal(lt, img.get_labeltable())

    with clear_and_catch_warnings() as w:
        warnings.filterwarnings('once', category=DeprecationWarning)
        img.set_labeltable(lt)
    assert_equal(lt, img.labeltable)


def test_parse_dataarrays():
    fn = 'bad_daa.gii'
    img = gi.GiftiImage()

    with InTemporaryDirectory():
        save(img, fn)
        with open(fn, 'r') as fp:
            txt = fp.read()
        # Make a bad gifti.
        txt = txt.replace('NumberOfDataArrays="0"', 'NumberOfDataArrays ="1"')
        with open(fn, 'w') as fp:
            fp.write(txt)

        with clear_and_catch_warnings() as w:
            warnings.filterwarnings('once', category=UserWarning)
            load(fn)
            assert_equal(len(w), 1)
            assert_equal(img.numDA, 0)
