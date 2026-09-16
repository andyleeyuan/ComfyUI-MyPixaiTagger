# Changelog

All notable changes to this project are documented in this file.

## [1.0.0] - 2026-09-17

### Changed

- Replaced the PixAI Tagger v0.9 `imgutils` integration with the official [PixAI Tagger v1.0](https://huggingface.co/pixai-labs/pixai-tagger-v1.0) Transformers pipeline.
- Added v1.0 category controls and outputs for general, character, style, copyright, meta, and rating tags.
- Added configurable batch inference, tag exclusions, and confidence-sorted output.
- Updated dependencies for the official v1.0 Transformers model and removed obsolete ONNX/imgutils dependencies.

### Compatibility

- The node identifier remains `MyPixaiTagger`.
- The legacy `threshold`, `enable_characters`, and `char_threshold` inputs are retained.
- The node now exposes seven string outputs instead of one: combined `tags` plus one output per v1.0 tag category.

## [0.9.x]

- Previous releases used PixAI Tagger v0.9 through `imgutils`.
