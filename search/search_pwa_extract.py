# -*- coding: utf-8 -*-


import os

import argparse
import importlib

from retrieval_tool_box.config import get_defaults_cfg
from retrieval_tool_box.datasets import build_folder, build_loader
from retrieval_tool_box.models import build_model
from retrieval_tool_box.extract import build_extract_helper


def load_datasets():
    data_json_dir = "/home/songrenjie/projects/RetrievalToolBox/new_data_jsons/"
    datasets = {
        "oxford_gallery": os.path.join(data_json_dir, "oxford_gallery.json"),
        "oxford_query": os.path.join(data_json_dir, "oxford_query.json"),
        "cub_gallery": os.path.join(data_json_dir, "cub_gallery.json"),
        "cub_query": os.path.join(data_json_dir, "cub_query.json"),
        "indoor_gallery": os.path.join(data_json_dir, "indoor_gallery.json"),
        "indoor_query": os.path.join(data_json_dir, "indoor_query.json"),
        "caltech101_gallery": os.path.join(data_json_dir, "caltech101_gallery.json"),
        "caltech101_query": os.path.join(data_json_dir, "caltech101_query.json"),
        "paris": os.path.join(data_json_dir, "paris.json"),
    }
    for data_path in datasets.values():
        assert os.path.exists(data_path), "non-exist dataset path {}".format(data_path)
    return datasets


def parse_args():
    parser = argparse.ArgumentParser(description='A tool box for deep learning-based image retrieval')
    parser.add_argument('opts', default=None, nargs=argparse.REMAINDER)
    parser.add_argument('--save_path', '-sp', default=None, type=str, help="the save path for feature")
    parser.add_argument("--search_modules", "-sm", default="", type=str, help="name of search module's directory")
    args = parser.parse_args()

    return args


def main():

    # init args
    args = parse_args()

    # init retrieval pipeline settings
    cfg = get_defaults_cfg()

    data_processes = importlib.import_module("{}.data_process_dict".format(args.search_modules)).data_processes
    models = importlib.import_module("{}.extract_dict".format(args.search_modules)).models
    extracts = importlib.import_module("{}.extract_dict".format(args.search_modules)).extracts

    datasets = load_datasets()

    for data_name, data_args in datasets.items():
        for data_proc_name, data_proc_args in data_processes.items():
            for model_name, model_args in models.items():

                feature_full_name = data_process_name + "_" + dataset_name + "_" + model_name
                print(feature_full_name)

                # load retrieval pipeline settings
                cfg.datasets.merge_from_other_cfg(data_proc_args)
                cfg.model.merge_from_other_cfg(model_args)
                cfg.extract.merge_from_other_cfg(extracts[model_name])

                pwa_train_fea_dir = os.path.join("/data/my_features/gap_gmp_gem_crow_spoc", feature_full_name)
                if "query" in pwa_train_fea_dir:
                    pwa_train_fea_dir.replace("query", "gallery")
                elif "paris" in pwa_train_fea_dir:
                    pwa_train_fea_dir.replace("paris", "oxford_gallery")
                print("[PWA Extractor]: train feature: {}".format(pwa_train_fea_dir))
                cfg.extract.aggregators.PWA.train_fea_dir = pwa_train_fea_dir

                # build dataset and dataloader
                dataset = build_folder(data_args, cfg.datasets)
                dataloader = build_loader(dataset, cfg.datasets)

                # build model
                model = build_model(cfg.model)

                # build helper and extract features
                extract_helper = build_extract_helper(model, cfg.extract)
                extract_helper.do_extract(dataloader, save_path=os.path.join(args.save_path, feature_full_name))


if __name__ == '__main__':
    main()
