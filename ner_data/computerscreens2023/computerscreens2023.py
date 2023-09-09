# coding=utf-8
# Copyright 2020 HuggingFace Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import datasets

logger = datasets.logging.get_logger(__name__)


_DESCRIPTION = """
"""

_URL = ""  # zip file
_TRAINING_FILE = "train.txt"
_DEV_FILE = "valid.txt"
_TEST_FILE = "test.txt"


LABELS = [
    "type-hdmi",
    "count-hdmi",
    "version-hdmi",
    "details-hdmi",
]

# automatically create B- and I- tags and empty string tag (O)
LABEL_NAMES = ["0"] + ["B-" + label for label in LABELS] + ["I-" + label for label in LABELS]


class ComputerScreens2023Config(datasets.BuilderConfig):
    """BuilderConfig for ComputerScreens2023"""

    def __init__(self, **kwargs):
        """BuilderConfig for ComputerScreens2023.
        Args:
          **kwargs: keyword arguments forwarded to super.
        """
        super(ComputerScreens2023Config, self).__init__(**kwargs)


class ComputerScreens2023(datasets.GeneratorBasedBuilder):
    """ComputerScreens2023 dataset."""

    BUILDER_CONFIGS = [
        ComputerScreens2023Config(
            name="computerscreens2023",
            version=datasets.Version("1.0.0"),
            description="Computer screens dataset from 2023",
        ),
    ]

    def _info(self):
        return datasets.DatasetInfo(
            # description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "id": datasets.Value("string"),
                    # "tokens": datasets.Sequence(datasets.Value("string")),
                    "ner_tags": datasets.Sequence(datasets.features.ClassLabel(names=LABEL_NAMES)),
                }
            ),
            supervised_keys=None,
            homepage="https://www.tuwien.at/",
        )

    def _split_generators(self):
        """Returns SplitGenerators."""
        datafiles_path = "./"
        data_files = {
            "train": os.path.join(datafiles_path, _TRAINING_FILE),
            "dev": os.path.join(datafiles_path, _DEV_FILE),
            "test": os.path.join(datafiles_path, _TEST_FILE),
        }

        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"filepath": data_files["train"]}),
            datasets.SplitGenerator(name=datasets.Split.VALIDATION, gen_kwargs={"filepath": data_files["dev"]}),
            datasets.SplitGenerator(name=datasets.Split.TEST, gen_kwargs={"filepath": data_files["test"]}),
        ]

    def _generate_examples(self, filepath):
        logger.info("⏳ Generating examples from = %s", filepath)
        with open(filepath, encoding="utf-8") as f:
            guid = 0
            tokens = []
            ner_tags = []
            for line in f:
                if line.startswith("-DOCSTART-") or line == "" or line == "\n":
                    if tokens:
                        yield guid, {
                            "id": str(guid),
                            "tokens": tokens,
                            "ner_tags": ner_tags,
                        }
                        guid += 1
                        tokens = []
                        ner_tags = []
                else:
                    # ComputerScreens2023 tokens are space separated
                    splits = line.split(" ")
                    tokens.append(splits[0])
                    ner_tags.append(splits[1].rstrip())
            # last example
            if tokens:
                yield guid, {
                    "id": str(guid),
                    "tokens": tokens,
                    "ner_tags": ner_tags,
                }
