# ComfyUI PixAI Tagger v1.0

[繁體中文](README_zh-TW.md)

[Changelog](CHANGELOG.md) · [Third-party notice](NOTICE.md) · [MIT License](LICENSE)

A ComfyUI custom node for the official [PixAI Tagger v1.0](https://huggingface.co/pixai-labs/pixai-tagger-v1.0). On first use, the node downloads the official model from Hugging Face and stores it in the local cache. This repository **does not include or redistribute model weights**.

Unlike the older v0.9 release, v1.0 is a Transformers model that recognizes 30,877 tags in six categories: general, character, style, copyright, meta, and rating.

## Installation

Place this directory in `ComfyUI/custom_nodes`, then install the requirements with the Python environment used by ComfyUI:

```bash
pip install -r requirements.txt
```

Restart ComfyUI and add the **🌸 PixAI Tagger v1.0 (Batch)** node. The first run needs an internet connection to download about 1.9 GB of official model files. A CUDA GPU is recommended. Hugging Face manages the download and subsequent local cache.

> This node uses `trust_remote_code=True` to load custom Transformers code supplied by PixAI's official model repository. Only use it if you trust that official source.

## Settings

Each threshold is a minimum confidence score from 0 to 1. Raising it returns fewer, more conservative tags; lowering it improves recall but can add false positives. The defaults below follow the category thresholds recommended by the PixAI v1.0 model card.

| Setting | Default | Description |
| --- | ---: | --- |
| `threshold` | `0.17` | Minimum confidence for general tags, such as clothing, poses, objects, and composition. The legacy parameter name is retained for existing workflows. |
| `enable_characters` | On | Enables recognized character names. |
| `char_threshold` | `0.27` | Minimum confidence for character tags. Raise to `0.40–0.60` if character false positives are common. |
| `enable_styles` | On | Enables art-style and style tags. |
| `style_threshold` | `0.15` | Minimum confidence for style tags. |
| `enable_copyrights` | On | Enables work, series, and IP tags. |
| `copyright_threshold` | `0.24` | Minimum confidence for copyright tags. |
| `enable_meta` | Off | Enables metadata tags such as `highres`, `official_art`, and `ai-generated`. These are usually not useful in a generation prompt. |
| `meta_threshold` | `0.17` | Minimum confidence for meta tags. |
| `enable_rating` | Off | Enables `rating:g`, `rating:s`, `rating:q`, and `rating:e`. |
| `rating_threshold` | `0.41` | Minimum confidence for rating tags. |
| `exclude_tags` | — | Tags to exclude, separated with commas or new lines; for example, `lowres, text, watermark`. |
| `replace_underscore` | On | Converts `blue_hair` to `blue hair`. Disable it to preserve the original Danbooru form. |
| `add_trailing_comma` | Off | Appends a comma to the combined `tags` output, making it easier to continue writing a prompt. |
| `batch_size` | `1` | Number of images inferred at once. Start at `1`, then raise it gradually if GPU VRAM allows. |

## Outputs

For each input image, the node returns seven strings:

| Output | Contents |
| --- | --- |
| `tags` | Combined prompt text in this order: character → copyright → style → general → meta → rating. |
| `general` | Visible content such as clothing, poses, objects, and composition. |
| `character` | Recognized character names. |
| `style` | Art-style and style tags. |
| `copyright` | Works, series, and IP. |
| `meta` | Medium, resolution, provenance, and similar metadata. |
| `rating` | Danbooru rating tags. |

For batch input, every output is a list of strings matching the input image order.

## Suggested use

- Start with the defaults.
- If there are too many general tags, raise `threshold` to `0.25–0.35`.
- If character recognition has too many false positives, raise `char_threshold` instead of disabling general tags.
- For text-to-image prompts, keeping `meta` and `rating` disabled is usually best.
- For more control, use the separate `character`, `copyright`, `style`, and `general` outputs instead of the combined `tags` output.

## License and third-party content

The code in this repository is released under the root [MIT License](LICENSE). That license **only applies to code and documentation written for this repository**. It grants no rights to PixAI's model, model weights, custom code in the model repository, or Danbooru tag content.

- The model source is PixAI Labs' official [PixAI Tagger v1.0 repository](https://huggingface.co/pixai-labs/pixai-tagger-v1.0). This project does not commit, mirror, or distribute its weights or remote code.
- As of 2026-09-17, the v1.0 model card does not state an explicit license and the repository file list does not include a `LICENSE` file. Do not interpret this project's MIT License as permission to reproduce, modify, or redistribute v1.0 weights.
- PixAI's public announcement for v0.9 mentioned the MIT License but also noted that Danbooru tag content has its own licensing terms. That announcement is not a license grant for v1.0; follow the current v1.0 model card and PixAI terms.
- Obtain written confirmation from PixAI Labs before distributing model weights, copying `tagger_pipeline.py`, mirroring the model, or providing a commercial hosted service.

This information is not legal advice. If your public release or commercial use is license-sensitive, confirm the terms with PixAI Labs or qualified legal counsel.

## Credits

- [PixAI Labs](https://huggingface.co/pixai-labs) — PixAI Tagger v1.0.
- [Danbooru](https://danbooru.donmai.us/) — the tag ecosystem; comply with applicable terms.
