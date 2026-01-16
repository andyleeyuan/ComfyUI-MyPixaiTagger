import torch
import numpy as np
from PIL import Image
from imgutils.tagging import get_pixai_tags
import comfy.utils # 用於顯示進度條

class MyPixaiTagger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { # 必須是字串 "required" 且後方有冒號
                "image": ("IMAGE",), # 鍵值對需要引號與冒號
                "threshold": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "char_threshold": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.01}),
                "exclude_tags": ("STRING", {"multiline": True, "default": "lowres, bad anatomy, text, error"}),
                "replace_underscore": ("BOOLEAN", {"default": True}),
                "add_trailing_comma": ("BOOLEAN", {"default": False}),
            } # 注意大括號閉合
        }

    # 輸出定義，所有值若為字串必須加引號
    RETURN_TYPES = ("STRING",)
    OUTPUT_IS_LIST = (True,) 
    FUNCTION = "tag_batch" # 必須是字串
    CATEGORY = "ImageTagging" # 必須是字串

    def tag_batch(self, image, threshold, char_threshold, exclude_tags, replace_underscore, add_trailing_comma):
        # 函式定義行末尾必須有冒號 ^
        results = []
        pbar = comfy.utils.ProgressBar(len(image)) 
        
        exclude_list = [t.strip().lower() for t in exclude_tags.split(',') if t.strip()]

        for i in range(len(image)):
            # 迴圈行末尾必須有冒號 ^
            img_tensor = image[i]
            # 這裡修正了乘號，原本少了 *
            img_np = 255. * img_tensor.cpu().numpy()
            img_pil = Image.fromarray(np.uint8(img_np))

            # 2. 呼叫 PixAI 模型 (移除不被支援的參數)
            general, character, _, _ = get_pixai_tags(
                img_pil,
                model_name='v0.9',
                fmt=('general', 'character', 'ips', 'ips_mapping'),
                # 這裡不再傳入 threshold，讓它回傳所有機率
            )

            # 3. 在此處手動過濾標籤 (根據你節點上的 threshold 設定)
            # 只有分數大於門檻，且不在排除清單中的標籤才會留下
            char_tags = [tag for tag, score in character.items() 
                         if score >= char_threshold and tag.lower() not in exclude_list]
            
            gen_tags = [tag for tag, score in general.items() 
                        if score >= threshold and tag.lower() not in exclude_list]
            
            final_tags = char_tags + gen_tags
            
            # 修正 join 語法，必須是 ", ".join(...)
            tag_string = ", ".join(final_tags)
            
            if replace_underscore: # 冒號
                # 修正 replace 語法，底線與空格必須是字串
                tag_string = tag_string.replace("_", " ")
            
            if add_trailing_comma and tag_string: # 冒號
                tag_string += ","

            results.append(tag_string)
            pbar.update(1) 

        return (results,)

NODE_CLASS_MAPPINGS = {
    "MyPixaiTagger": MyPixaiTagger
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MyPixaiTagger": "🌸 PixAI Tagger v0.9 (Batch)"
}