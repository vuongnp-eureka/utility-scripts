
"""
Utility script to prepare disparity data set.
How to use:
1. Get all left images: 
    $ python prepare_data.py -d <data_dir> -sd <save_image_dir> --get_images
2. Get annotated objects: 
    $ python prepare_data.py -d <data_dir> -f <annotation_file> --get_objects
"""
import os
import shutil
import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_dir", type=str, help="a directory containing rectified scenes")
    parser.add_argument("--get_images", action="store_true", help="Get all left images")
    parser.add_argument("--get_objects", action="store_true", help="Get annotated objects for each scene")
    parser.add_argument("-sd", "--save_image_dir", type=str, default="left_images", help="a directory containing left images")
    parser.add_argument("-f", "--annotation_file", type=str, help="annotation file from ML Studio")
    args = parser.parse_args()
    return args

def get_images(data_dir: str, save_image_dir: str) -> None:
    """
    Get all left images and name them as sceneX_image_0.png.

    Args:
        data_dir (str): The directory containing the scenes.
        save_image_dir (str): The directory to save the left images.
    """
    if not os.path.exists(save_image_dir):
        os.makedirs(save_image_dir)
    for scene in os.listdir(data_dir):
        scene_path = os.path.join(data_dir, scene)
        if os.path.isdir(scene_path):
            left_path = os.path.join(scene_path, "image_0.png")
            assert os.path.exists(left_path), f"{left_path} does not exist"
            shutil.copy(left_path, os.path.join(save_image_dir, scene + "_image_0.png"))

def get_objects(annotation_file: str, data_dir: str) -> None:
    """
    Extracts object polygons from ML Studio annotation file.

    Args:
        annotation_file (str): The path to the annotation file.
        data_dir (str): The directory where the scene data is stored.
    """
    with open(annotation_file, "r") as f:
        data = json.load(f)
    annotations = data["_via_img_metadata"]
    for image_obj in annotations.values():
        image_name = image_obj["filename"]
        scene_name = image_name.split("/")[-1].split("_")[0]
        scene_path = os.path.join(data_dir, scene_name)
        if not os.path.exists(scene_path):
            print(f"{scene_path} does not exist")
            continue
        objects_path = os.path.join(scene_path, "objects3.json")

        polygons = []
        for k, v in image_obj["regions"].items():
            shape_att = v["shape_attributes"]
            all_points_x = shape_att["all_points_x"]
            all_points_y = shape_att["all_points_y"]
            polygon = []
            for x, y in zip(all_points_x, all_points_y):
                polygon.extend([int(x), int(y)])
            polygons.append(polygon)
        with open(objects_path, "w") as f:
            json.dump(polygons, f)

if __name__ == "__main__":
    args = parse_args()

    assert args.data_dir is not None, "Please specify --data_dir"
    if not args.get_images and not args.get_objects:
        print("Please specify either --get_images or --get_objects")
        exit(1)
    if args.get_images:
        print(f"Save left images to {args.save_image_dir}")
        get_images(args.data_dir, args.save_image_dir)
    if args.get_objects:
        assert args.annotation_file is not None, "Please specify --annotation_file"
        print(f"Extract objects from {args.annotation_file}")
        get_objects(args.annotation_file, args.data_dir)
