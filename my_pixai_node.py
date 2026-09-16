"""ComfyUI node for the official PixAI Tagger v1.0 model."""

import re

import numpy as np
from PIL import Image
import torch

import comfy.utils


MODEL_ID = "pixai-labs/pixai-tagger-v1.0"
TAG_CATEGORIES = ("general", "character", "style", "copyright", "meta", "rating")

_tagger = None


def get_tagger():
    """Load the official v1.0 Transformers pipeline once per ComfyUI process."""
    global _tagger

    if _tagger is None:
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError(
                "PixAI Tagger v1.0 requires the packages in this custom node's "
                "requirements.txt. Install them and restart ComfyUI."
            ) from exc

        # The model card supplies a custom pipeline and image processor. The first
        # use downloads the official model to Hugging Face's local cache.
        _tagger = pipeline(
            model=MODEL_ID,
            image_processor=MODEL_ID,
            trust_remote_code=True,
            device=0 if torch.cuda.is_available() else -1,
        )

    return _tagger


def to_pil_image(image_tensor):
    """Convert one ComfyUI HWC image tensor to an RGB/RGBA PIL image."""
    image_array = image_tensor.detach().cpu().numpy()
    image_array = np.clip(image_array * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(image_array)


def normalise_exclusions(exclude_tags):
    return {
        tag.strip().lower().replace(" ", "_")
        for tag in re.split(r"[,\n]", exclude_tags)
        if tag.strip()
    }


def format_tags(tags, excluded, replace_underscore):
    """Apply exclusions and return highest-confidence tags first."""
    selected = [
        (tag, score)
        for tag, score in tags.items()
        if tag.lower().replace(" ", "_") not in excluded
    ]
    selected.sort(key=lambda item: item[1], reverse=True)

    names = [tag.replace("_", " ") if replace_underscore else tag for tag, _ in selected]
    return ", ".join(names)


class MyPixaiTagger:
    """Batch image tagging with the official PixAI Tagger v1.0 release."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold": (
                    "FLOAT",
                    {"default": 0.17, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "enable_characters": (
                    "BOOLEAN",
                    {"default": True, "label_on": "Enable Characters", "label_off": "Disable Characters"},
                ),
                "char_threshold": (
                    "FLOAT",
                    {"default": 0.27, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "enable_styles": (
                    "BOOLEAN",
                    {"default": True, "label_on": "Enable Styles", "label_off": "Disable Styles"},
                ),
                "style_threshold": (
                    "FLOAT",
                    {"default": 0.15, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "enable_copyrights": (
                    "BOOLEAN",
                    {"default": True, "label_on": "Enable Copyrights", "label_off": "Disable Copyrights"},
                ),
                "copyright_threshold": (
                    "FLOAT",
                    {"default": 0.24, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "enable_meta": (
                    "BOOLEAN",
                    {"default": False, "label_on": "Enable Meta", "label_off": "Disable Meta"},
                ),
                "meta_threshold": (
                    "FLOAT",
                    {"default": 0.17, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "enable_rating": (
                    "BOOLEAN",
                    {"default": False, "label_on": "Enable Rating", "label_off": "Disable Rating"},
                ),
                "rating_threshold": (
                    "FLOAT",
                    {"default": 0.41, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "exclude_tags": (
                    "STRING",
                    {"multiline": True, "default": "lowres, bad anatomy, text, error"},
                ),
                "replace_underscore": ("BOOLEAN", {"default": True}),
                "add_trailing_comma": ("BOOLEAN", {"default": False}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 16, "step": 1}),
            }
        }

    RETURN_TYPES = ("STRING",) * 7
    RETURN_NAMES = ("tags", "general", "character", "style", "copyright", "meta", "rating")
    OUTPUT_IS_LIST = (True,) * 7
    FUNCTION = "tag_batch"
    CATEGORY = "ImageTagging"

    def tag_batch(
        self,
        image,
        threshold,
        enable_characters,
        char_threshold,
        enable_styles,
        style_threshold,
        enable_copyrights,
        copyright_threshold,
        enable_meta,
        meta_threshold,
        enable_rating,
        rating_threshold,
        exclude_tags,
        replace_underscore,
        add_trailing_comma,
        batch_size,
    ):
        category_thresholds = {
            "general": threshold,
            "character": char_threshold,
            "style": style_threshold,
            "copyright": copyright_threshold,
            "meta": meta_threshold,
            "rating": rating_threshold,
        }
        enabled_categories = {
            "general": True,
            "character": enable_characters,
            "style": enable_styles,
            "copyright": enable_copyrights,
            "meta": enable_meta,
            "rating": enable_rating,
        }
        excluded = normalise_exclusions(exclude_tags)
        outputs = {category: [] for category in TAG_CATEGORIES}
        combined_outputs = []
        tagger = get_tagger()
        pbar = comfy.utils.ProgressBar(len(image))

        for start in range(0, len(image), batch_size):
            pil_batch = [to_pil_image(item) for item in image[start : start + batch_size]]
            batch_results = tagger(
                pil_batch,
                threshold=category_thresholds,
                batch_size=batch_size,
            )
            if isinstance(batch_results, dict):
                batch_results = [batch_results]

            for result in batch_results:
                categories = result["results"]
                formatted = {}
                for category in TAG_CATEGORIES:
                    if enabled_categories[category]:
                        formatted[category] = format_tags(
                            categories.get(category, {}), excluded, replace_underscore
                        )
                    else:
                        formatted[category] = ""
                    outputs[category].append(formatted[category])

                # Identity first, then source/style and visual tags. Separate outputs
                # retain each category for workflows that need them individually.
                combined = ", ".join(
                    tag
                    for category in ("character", "copyright", "style", "general", "meta", "rating")
                    if (tag := formatted[category])
                )
                if add_trailing_comma and combined:
                    combined += ","
                combined_outputs.append(combined)
                pbar.update(1)

        return (combined_outputs,) + tuple(outputs[category] for category in TAG_CATEGORIES)


NODE_CLASS_MAPPINGS = {
    "MyPixaiTagger": MyPixaiTagger,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MyPixaiTagger": "🌸 PixAI Tagger v1.0 (Batch)",
}
