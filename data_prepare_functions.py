""" includes the necessary functions to load and manipulate DICOM images """

import os
import sys
import glob
import pydicom as dicom
from dicom_contour.contour import *
import cv2


def findfiles_CHUM(path):
    """
    find the paths paths to all CT/PET/contour files for a single patient from CHUM hospital

    Args:
        path (str): to root image folder
    returns:
        tuple(path for CT images, paths to PET images, path to CT contour file, path to PET contour file)
     """
    directories = []
    images = []
    ct_path = ''
    pet_path = ''
    cont_path = ''
    pet_cont_path = ''

    for directory, sub, files in os.walk(path):
        directories.append(directory)

    for dirs in directories:
        files = glob.glob(os.path.join(dirs, '*.dcm'))

        if (len(files) != 0) and (dirs.find('TomoTherapy') == -1):
            # print(f'found {len(files)} in ', dirs)
            # print(files)
            images.append(files)
            try:
                sample = dicom.read_file(files[0])
                if sample.Modality == 'CT':
                    # print('CT: ', dir(sample))
                    ct_path = dirs
                elif sample.Modality == 'PT':
                    # print('PET: ', dir(sample))
                    pet_path = dirs
                elif sample.Modality == 'RTSTRUCT':
                    for i in dict(sample.ROIContourSequence[1]):
                        # print('key ',i,'--->', 'value ',dict(sample.ROIContourSequence[1])[i][1])
                        if 'CT Image Storage' in str(dict(sample.ROIContourSequence[1])[i][1]):
                            cont_path = dirs
                        elif 'Positron Emission Tomography Image Storage':
                            # print(f'PET CONR {files[0]}')
                            pet_cont_path = dirs

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # print(exc_type, fname, exc_tb.tb_lineno)

    return ct_path, pet_path, cont_path, pet_cont_path


def get_datas(ct_path, pet_path, cont_path, index):
    """
    Generate image array and contour array
    Inputs:
        path (str): path of the the directory that has DICOM files in it
        contour_dict (dict): dictionary created by get_contour_dict
        index (int): index of the desired ROISequence
    Returns:
        images and contours np.arrays
    """
    images = []
    contours = []
    pets = []

    # handle `/` missing
    if ct_path[-1] != '/': ct_path += '/'
    if pet_path[-1] != '/': pet_path += '/'

    # get contour file
    contour_file = get_contour_file(cont_path)
    # get slice orders
    ordered_slices = slice_order(ct_path)
    ordered_pet = slice_order(pet_path)

    # get contour dict
    contour_dict = get_contour_dict(contour_file, ct_path, index)

    for k, v in ordered_slices:
        # get data from contour dict
        if k in contour_dict:
            images.append(contour_dict[k][0])
            contours.append(contour_dict[k][1])
        # get data from dicom.read_file
        else:
            img_arr = dicom.read_file(ct_path + k + '.dcm').pixel_array
            contour_arr = np.zeros_like(img_arr)
            images.append(img_arr)
            contours.append(contour_arr)

    # pet
    for x, y in ordered_pet:
        img_arrs = dicom.read_file(pet_path + x + '.dcm').pixel_array
        img_arrs = cv2.resize(img_arrs, (512, 512))
        pets.append(img_arrs)

    return np.array(images), np.array(contours), np.array(pets)