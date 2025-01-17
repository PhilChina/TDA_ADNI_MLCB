#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""persistence_image_generator.py

This script generates the persistence images for a given array, which represents
a patch of a structural MRI. This output can later be used as an input for a CNN
for classification purposes.


TODO:
    -
"""

__author__ = "Philip Hartout"
__email__ = "philip.hartout@protonmail.com"

import dotenv


import numpy as np

from gtda.diagrams import PersistenceImage
from gtda.homology import CubicalPersistence

import os


DOTENV_KEY2VAL = dotenv.dotenv_values()
N_JOBS = -1
HOMOLOGY_DIMENSIONS = (0, 1, 2)
N_BINS = 100


def get_all_available_patches(path_to_patches):
    """Obtains all array data in given path_to_patches and tracks loaded files.

    Args:
        path_to_patch (str): path to the patches of interest

    Returns:

    """
    data = []
    files_loaded = []
    for root, dirs, files in os.walk(path_to_patches):
        for fil in files:
            if fil.endswith(".npy"):
                files_loaded.append(fil)
                data.append(np.load(path_to_patches + fil))
    # Stack all arrays in one for multiprocessing later on
    data = np.stack(data, axis=0)
    print("Data loaded")
    return data, files_loaded


def cubical_persistence(patch):
    cp = CubicalPersistence(
        homology_dimensions=HOMOLOGY_DIMENSIONS,
        coeff=2,
        periodic_dimensions=None,
        infinity_values=None,
        reduced_homology=True,
        n_jobs=N_JOBS,
    )
    diagrams_cubical_persistence = cp.fit_transform(patch)
    # sc = Scaler(metric="bottleneck")
    # scaled_diagrams_cubical_persistence = sc.fit_transform(
    #     diagrams_cubical_persistence
    # )
    print("Computed cubical persistence")
    return diagrams_cubical_persistence


def get_persistence_images(persistence_diagram):
    pi = PersistenceImage(
        sigma=0.001, n_bins=N_BINS, weight_function=None, n_jobs=N_JOBS
    )
    print("Computed persistence images")
    return pi.fit_transform(persistence_diagram)


def export_persistence_images(
    persistence_images, files_loaded, path_to_persistence_images
):
    for i, fil in enumerate(files_loaded):
        persistence_image = persistence_images[i, :, :, :]
        with open(path_to_persistence_images + fil, "wb") as f:
            np.save(f, persistence_image)
    print("Export persistence images")


def main():
    path_to_patch = DOTENV_KEY2VAL["DATA_DIR"] + "patch_91/"
    path_to_persistence_images = (
        DOTENV_KEY2VAL["DATA_DIR"] + "patch_91_persistence_images/"
    )

    if not os.path.exists(path_to_persistence_images):
        os.mkdir(path_to_persistence_images)

    patch_data, files_loaded = get_all_available_patches(path_to_patch)
    persistence_diagrams = cubical_persistence(patch_data)
    persistence_images = get_persistence_images(persistence_diagrams)

    export_persistence_images(
        persistence_images, files_loaded, path_to_persistence_images
    )


if __name__ == "__main__":
    main()
