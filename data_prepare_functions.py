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

    '''remove pet '''
    # pet_path = ''
    # cont_path = ''
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
                

                # elif sample.Modality == 'PT':
                #     # print('PET: ', dir(sample))
                #     pet_path = dirs
                elif sample.Modality == 'RTSTRUCT':
                    for i in dict(sample.ROIContourSequence[1]):
                        # print('key ',i,'--->', 'value ',dict(sample.ROIContourSequence[1])[i][1])
                        if 'CT Image Storage' in str(dict(sample.ROIContourSequence[1])[i][1]):
                            cont_path = dirs
                        # elif 'Positron Emission Tomography Image Storage':
                        #     # print(f'PET CONR {files[0]}')
                        #     pet_cont_path = dirs

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # print(exc_type, fname, exc_tb.tb_lineno)

    # return ct_path, pet_path, cont_path, pet_cont_path
    return ct_path, cont_path


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
    contour_file = get_contour_file(cont_path) # -> returns the name off the contour file

    # get slice orders
    ordered_slices = slice_order(ct_path) #-> returns a sequesnce (slice 1 is 1, slice 2 is 2)
    # ordered_pet = slice_order(pet_path)

    # get contour dict
    contour_dict = get_contour_dict(contour_file, ct_path, index)   # -> index is which stucture in the RTstruct file
                                                                    # assume index = 1
                                                                    # returns a dict with ct image, contour pairs

    for k, v in ordered_slices:
        # get data from contour dict
        if k in contour_dict:
            images.append(contour_dict[k][0]) # 0 is image 
            contours.append(contour_dict[k][1]) # 1 is contour
        # get data from dicom.read_file
        else:
            # if theres no tumor it will add an empty image 
            img_arr = dicom.read_file(ct_path + k + '.dcm').pixel_array 
            contour_arr = np.zeros_like(img_arr)
            images.append(img_arr)
            contours.append(contour_arr)

    # # pet
    # for x, y in ordered_pet:
    #     img_arrs = dicom.read_file(pet_path + x + '.dcm').pixel_array
    #     img_arrs = cv2.resize(img_arrs, (512, 512))
    #     pets.append(img_arrs)

    # return np.array(images), np.array(contours), np.array(pets)

    # this return numpy arrays 
    # to conver into .png image
    '''
    ct_images, contours, pet_images are lists of the images and their contours 
    depending on your project you may need to save them as .png to your location 
    you need to make sure that you also save the sequence 

    example just for reference:

    for i,ct,pt,mask in enumerate(zip(ct_images, pet_images, countours)):
        ct.imsave(f'./<path to final ct folder>/image_CT_{i}.png', cmap='gray)
        pt.imsave(f'./<path to final pet folder>/image_PT_{i}.png', cmap='gray)
        mask.imsave(f'./<path to final ground truth folder>/image_GT_{i}.png', cmap='gray)
    '''
    return np.array(images), np.array(contours)




path = 'C:/user/patients/9'
ct_path,  cont_path = findfiles_CHUM(path)

imgs, masks = get_datas(ct_path, cont_path)

'''
imgs is a list of slices for one image
to get the first one you need imgs[0]

imgs[0].imsave('filename.png', cmap='gray')
masks[0].imsave('filename.png', cmap='gray')

'''
