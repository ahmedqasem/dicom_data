""" script for extracting and pre-processing the DICOM images """

from data_prepare_functions import *
import os
import glob
import pydicom as dicom
from dicom_contour.contour import *
import pandas as pd


# select the source folder for each image
'''
you need to change the directory based on the folder structure and image name 
to match the dataset and folder that you have
'''

hospital = 'CHUM'
data_root = f'C:/Users/<username>/Desktop/data/Head-Neck-PET-CT/{hospital}/' # update path
patients = os.listdir(data_root)
gtv_index_df_path = 'C:/Users/<username>/Desktop/data/GTVcontours.xls' # update path
data = pd.read_excel(gtv_index_df_path, sheet_name=hospital)

for n, patient in enumerate(patients):
    if n > 0:
        break

    # find location of CT PET and Contour file
    ct_location, pet_location, ct_contour_location, pet_contour_location = findfiles_CHUM(os.path.join(data_root, patient))
    print(f'ct: {ct_location}')
    print(f'pet: {pet_location}')
    print(f'cont: {ct_contour_location}')

    # find the GTV index
    '''
    ['Name GTV Primary'] and ['Patient'] might be different in your dataset
    '''
    gtv_index = data[data['Patient'] == patient]['Name GTV Primary']

    ct_images, contours, pet_images = get_datas(ct_location, pet_location, ct_contour_location, gtv_index)

    

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







