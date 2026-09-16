# ComfyUI PixAI Tagger v1.0

[English](README.md)

[變更紀錄](CHANGELOG.md) · [第三方聲明](NOTICE.md) · [MIT License](LICENSE)

使用官方 [PixAI Tagger v1.0](https://huggingface.co/pixai-labs/pixai-tagger-v1.0) 的 ComfyUI 自訂節點。節點會在第一次執行時，從 Hugging Face 下載官方模型並儲存至本機快取；本儲存庫**不包含或重新散布模型權重**。

v1.0 是不同於舊版 v0.9 的 Transformers 模型，能輸出 30,877 個標籤，並分成 general、character、style、copyright、meta、rating 六個類別。

## 安裝

將此資料夾放進 `ComfyUI/custom_nodes`，然後使用 ComfyUI 所使用的 Python 安裝依賴：

```bash
pip install -r requirements.txt
```

重新啟動 ComfyUI 後，加入 **🌸 PixAI Tagger v1.0 (Batch)** 節點。首次執行需要網路連線以下載約 1.9 GB 的官方模型；建議使用 CUDA GPU。模型下載與後續快取均由 Hugging Face 管理。

> 此節點以 `trust_remote_code=True` 載入 PixAI 官方模型庫提供的自訂 Transformers 程式碼。請只在你信任該官方來源時使用。

## 設定

每個 threshold 都是最低信心值（0 至 1）。提高數值會減少標籤數量並提高保守程度；降低數值會增加召回率，也可能增加誤判。以下預設值採用 PixAI v1.0 模型卡建議的分類閾值。

| 設定 | 預設值 | 說明 |
| --- | ---: | --- |
| `threshold` | `0.17` | General 標籤的最低信心值；例如服裝、姿勢、物件、構圖。舊版工作流的同名參數仍可使用。 |
| `enable_characters` | 開啟 | 是否輸出已辨識的角色名稱。 |
| `char_threshold` | `0.27` | Character 標籤的最低信心值。角色誤判時可提高至 `0.40–0.60`。 |
| `enable_styles` | 開啟 | 是否輸出畫風與風格標籤。 |
| `style_threshold` | `0.15` | Style 標籤的最低信心值。 |
| `enable_copyrights` | 開啟 | 是否輸出作品、系列與 IP 標籤。 |
| `copyright_threshold` | `0.24` | Copyright 標籤的最低信心值。 |
| `enable_meta` | 關閉 | 是否輸出 `highres`、`official_art`、`ai-generated` 等中繼資料標籤。通常不適合直接作為 prompt。 |
| `meta_threshold` | `0.17` | Meta 標籤的最低信心值。 |
| `enable_rating` | 關閉 | 是否輸出 `rating:g`、`rating:s`、`rating:q`、`rating:e`。 |
| `rating_threshold` | `0.41` | Rating 標籤的最低信心值。 |
| `exclude_tags` | — | 要排除的標籤，可用逗號或換行分隔，例如 `lowres, text, watermark`。 |
| `replace_underscore` | 開啟 | 將 `blue_hair` 輸出為 `blue hair`；若要保留 Danbooru 格式請關閉。 |
| `add_trailing_comma` | 關閉 | 為合併輸出末尾加上逗號，方便後接手寫 prompt。 |
| `batch_size` | `1` | 單次推論圖片數。從 `1` 開始；顯示卡 VRAM 足夠時再逐步提高。 |

## 輸出

節點對每張輸入圖片輸出下列七個字串：

| 輸出 | 內容 |
| --- | --- |
| `tags` | 合併的 prompt 文字，順序為 character → copyright → style → general → meta → rating。 |
| `general` | 服裝、姿勢、物件、構圖等可見內容。 |
| `character` | 角色名稱。 |
| `style` | 畫風與風格。 |
| `copyright` | 作品、系列與 IP。 |
| `meta` | 圖片媒材、解析度、來源等資訊。 |
| `rating` | Danbooru 分級標籤。 |

批次輸入時，每個輸出都會是一組與輸入圖片順序對應的字串清單。

## 建議使用方式

- 先直接使用預設值。
- General 標籤太多時，將 `threshold` 提高到 `0.25–0.35`。
- 角色辨識誤判較多時，提高 `char_threshold`，而不是關閉 general 標籤。
- 要用於圖像生成 prompt 時，通常保持 `meta` 和 `rating` 關閉。
- 想自行控制提示詞時，分別使用 `character`、`copyright`、`style`、`general` 輸出會比直接使用合併 `tags` 更彈性。

## 授權與第三方內容

本儲存庫的程式碼以根目錄的 [MIT License](LICENSE) 發布；此授權**只適用於本專案自行撰寫的程式碼與文件**，不授予 PixAI 模型、模型權重、模型庫內的自訂程式碼，或 Danbooru 標籤內容的任何權利。

- 模型來源為 PixAI Labs 的官方 [PixAI Tagger v1.0 模型庫](https://huggingface.co/pixai-labs/pixai-tagger-v1.0)。本專案不將其權重或遠端程式碼提交進版本庫，也不提供鏡像下載。
- 截至 2026-09-17，該 v1.0 模型卡未列出明確授權條款，模型庫檔案清單亦未包含 `LICENSE`。因此，請勿把本專案的 MIT 授權理解為 v1.0 權重可自由重製、修改或重新散布的許可。
- PixAI 對舊版 v0.9 的公開公告曾提到 MIT 授權，但同時指出 Danbooru 標籤內容有其自身授權；該公告不等於 v1.0 的授權聲明。請依 v1.0 模型卡與 PixAI 的最新條款為準。
- 若要發佈含有模型權重、複製 `tagger_pipeline.py`、建立模型鏡像，或提供商業託管服務，請先取得 PixAI Labs 的書面確認。

本說明不是法律意見。若你的公開或商業用途對授權風險敏感，請向 PixAI Labs 或合格法律專業人士確認。

## 致謝

- [PixAI Labs](https://huggingface.co/pixai-labs) — PixAI Tagger v1.0。
- [Danbooru](https://danbooru.donmai.us/) — 標籤生態系統；請遵守其適用條款。
