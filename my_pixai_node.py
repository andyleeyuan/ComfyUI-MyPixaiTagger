import torch
import numpy as np
from PIL import Image
from imgutils.tagging import get_pixai_tags
import comfy.utils # 用於顯示進度條

class MyPixaiTagger
    @classmethod
    def INPUT_TYPES(s)
        return {
            required {
                image (IMAGE,),
                threshold (FLOAT, {default 0.3, min 0.0, max 1.0, step 0.01}),
                char_threshold (FLOAT, {default 0.75, min 0.0, max 1.0, step 0.01}),
                exclude_tags (STRING, {multiline True, default lowres, bad anatomy, text, error}),
                replace_underscore (BOOLEAN, {default True}),
                add_trailing_comma (BOOLEAN, {default False}),
            }
        }

    # 輸出改為 LIST，以便與其他批量節點對接
    RETURN_TYPES = (STRING,)
    OUTPUT_IS_LIST = (True,) 
    FUNCTION = tag_batch
    CATEGORY = ImageTagging

    def tag_batch(self, image, threshold, char_threshold, exclude_tags, replace_underscore, add_trailing_comma)
        results = []
        pbar = comfy.utils.ProgressBar(len(image)) # 建立 ComfyUI 頂部的進度條
        
        # 處理排除清單
        exclude_list = [t.strip().lower() for t in exclude_tags.split(',') if t.strip()]

        # 遍歷 Batch 中的每一張圖
        for i in range(len(image))
            # 1. 預處理單張圖
            img_tensor = image[i]
            img_np = 255.  img_tensor.cpu().numpy()
            img_pil = Image.fromarray(np.uint8(img_np))

            # 2. 呼叫 PixAI 模型
            general, character, _, _ = get_pixai_tags(
                img_pil,
                model_name='v0.9',
                fmt=('general', 'character', 'ips', 'ips_mapping'),
                threshold=threshold,
                character_threshold=char_threshold
            )

            # 3. 過濾並組合標籤
            char_tags = [t for t in character.keys() if t.lower() not in exclude_list]
            gen_tags = [t for t in general.keys() if t.lower() not in exclude_list]
            
            final_tags = char_tags + gen_tags
            
            # 4. 格式化處理
            tag_string = , .join(final_tags)
            if replace_underscore
                tag_string = tag_string.replace(_,  )
            
            if add_trailing_comma and tag_string
                tag_string += ,

            results.append(tag_string)
            pbar.update(1) # 更新進度條

        return (results,)

NODE_CLASS_MAPPINGS = {
    "MyPixaiTagger": MyPixaiTagger
}

# 這裡的鍵必須是字串 "MyPixaiTagger"，值也要是字串
NODE_DISPLAY_NAME_MAPPINGS = {
    "MyPixaiTagger": "PixAI Tagger v0.9 (Batch)"
}