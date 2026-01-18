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
        results = []
        pbar = comfy.utils.ProgressBar(len(image)) 
        
        # 預處理排除清單：轉小寫並將空格統一轉為底線，確保比對基準一致
        exclude_list = [t.strip().lower().replace(" ", "_") for t in exclude_tags.split(',') if t.strip()]

        for i in range(len(image)):
            img_tensor = image[i]
            img_np = 255. * img_tensor.cpu().numpy()
            img_pil = Image.fromarray(np.uint8(img_np))

            # 呼叫 PixAI 模型
            general, character, _, _ = get_pixai_tags(
                img_pil,
                model_name='v0.9',
                fmt=('general', 'character', 'ips', 'ips_mapping'),
            )

            # 過濾標籤：在比對時同樣將 tag 轉為底線格式進行檢查
            char_tags = [
                tag for tag, score in character.items() 
                if score >= char_threshold and tag.lower().replace(" ", "_") not in exclude_list
            ]
            
            gen_tags = [
                tag for tag, score in general.items() 
                if score >= threshold and tag.lower().replace(" ", "_") not in exclude_list
            ]
            
            final_tags = char_tags + gen_tags
            
            # 組合成字串
            tag_string = ", ".join(final_tags)
            
            # 格式化處理
            if replace_underscore:
                tag_string = tag_string.replace("_", " ")
            
            if add_trailing_comma and tag_string:
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