import torch
import numpy as np
from PIL import Image
from imgutils.tagging import get_pixai_tags
import comfy.utils

class MyPixaiTagger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                # 一般標籤的閥值
                "threshold": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                # 新增：直接開關角色標籤，比調數值更方便
                "enable_characters": ("BOOLEAN", {"default": True, "label_on": "Enable Characters", "label_off": "Disable Characters"}),
                # 角色標籤的閥值 (只有在 enable_characters 為 True 時才有效)
                "char_threshold": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.01}),
                "exclude_tags": ("STRING", {"multiline": True, "default": "lowres, bad anatomy, text, error"}),
                "replace_underscore": ("BOOLEAN", {"default": True}),
                "add_trailing_comma": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "tag_batch"
    CATEGORY = "ImageTagging"

    # 記得更新函式參數，加入 enable_characters
    def tag_batch(self, image, threshold, enable_characters, char_threshold, exclude_tags, replace_underscore, add_trailing_comma):
        results = []
        pbar = comfy.utils.ProgressBar(len(image)) 
        
        # 預處理排除清單
        exclude_list = [t.strip().lower().replace(" ", "_") for t in exclude_tags.split(',') if t.strip()]

        for i in range(len(image)):
            img_tensor = image[i]
            img_np = 255. * img_tensor.cpu().numpy()
            img_pil = Image.fromarray(np.uint8(img_np))

            # 呼叫 PixAI 模型
            # 注意：即使不想要角色，模型通常還是一次跑完，所以我們在後處理過濾
            general, character, _, _ = get_pixai_tags(
                img_pil,
                model_name='v0.9',
                fmt=('general', 'character', 'ips', 'ips_mapping'),
            )

            # 處理角色標籤 (Character Tags)
            char_tags = []
            if enable_characters: # 只有在開關開啟時才處理角色
                char_tags = [
                    tag for tag, score in character.items() 
                    if score >= char_threshold and tag.lower().replace(" ", "_") not in exclude_list
                ]
            
            # 處理一般標籤 (General Tags)
            gen_tags = [
                tag for tag, score in general.items() 
                if score >= threshold and tag.lower().replace(" ", "_") not in exclude_list
            ]
            
            # 組合：角色在前，一般標籤在後 (這是常見的 Prompt 格式)
            final_tags = char_tags + gen_tags
            
            tag_string = ", ".join(final_tags)
            
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