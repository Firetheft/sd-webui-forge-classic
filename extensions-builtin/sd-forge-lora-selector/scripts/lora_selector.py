import os
import sys
import gradio as gr
from modules import scripts, shared

class StylezLoraSelector(scripts.Script):
    def title(self):
        return "Simple LoRA Selector"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        lora_count = 5
        lora_ctrls = []
        
        def get_lora_data():
            names = ["None"]
            
            try:
                candidates = []
                search_dirs = []
                opts = shared.cmd_opts

                if hasattr(opts, "lora_dir") and opts.lora_dir:
                    search_dirs.append(opts.lora_dir)
                if hasattr(opts, "lora_dirs") and opts.lora_dirs:
                    search_dirs.extend(opts.lora_dirs)

                if hasattr(opts, "forge_ref_comfy_home") and opts.forge_ref_comfy_home:
                    search_dirs.append(os.path.join(opts.forge_ref_comfy_home, "models", "loras"))
                    search_dirs.append(os.path.join(opts.forge_ref_comfy_home, "models", "Lora"))

                if hasattr(opts, "forge_ref_a1111_home") and opts.forge_ref_a1111_home:
                    search_dirs.append(os.path.join(opts.forge_ref_a1111_home, "models", "Lora"))
                    search_dirs.append(os.path.join(opts.forge_ref_a1111_home, "models", "loras"))

                if hasattr(opts, "model_ref") and opts.model_ref:
                    search_dirs.append(os.path.join(opts.model_ref, "Lora"))
                    search_dirs.append(os.path.join(opts.model_ref, "loras"))

                valid_dirs = []
                seen = set()
                for d in search_dirs:
                    if not d: continue
                    path = os.path.normpath(d.strip("'").strip('"'))
                    if os.path.isdir(path) and path not in seen:
                        valid_dirs.append(path)
                        seen.add(path)

                for root_dir in valid_dirs:
                    for root, _, files in os.walk(root_dir):
                        for file in files:
                            if file.endswith((".safetensors", ".pt", ".ckpt")):
                                full_path = os.path.join(root, file)
                                try:
                                    rel_path = os.path.relpath(full_path, root_dir)
                                    name = os.path.splitext(rel_path)[0]
                                    name = name.replace("\\", "/")
                                    
                                    if name not in candidates:
                                        candidates.append(name)
                                except ValueError:
                                    continue
                
                if candidates:
                    names += sorted(candidates)
                    
            except Exception as e:
                print(f"[LoRA Selector] Disk scan failed: {e}")

            return names

        lora_list = get_lora_data()

        with gr.Accordion("LoRA Selector", open=False):
            with gr.Row():
                gr.Markdown("Select LoRA model and set weights")
                refresh_btn = gr.Button("🔄 Refresh list", variant="secondary", size="sm", scale=0, min_width=100, elem_classes="stylez-lora-refresh")

            for i in range(lora_count):
                with gr.Row(variant="compact"): 
                    
                    model = gr.Dropdown(label=f"LoRA {i+1}", choices=lora_list, value="None", scale=10)
                    
                    weight = gr.Slider(label=f"weight {i+1}", minimum=-2.0, maximum=2.0, step=0.05, value=1.0, scale=4, elem_classes="lora-weight-slider")
                    
                    clear_btn = gr.Button("🗑️", variant="secondary", size="sm", min_width=40, scale=0.5, elem_classes="lora-delete-btn")
                    
                    def clear_slot():
                        return "None", 1.0
                    
                    clear_btn.click(fn=clear_slot, inputs=[], outputs=[model, weight])
                    
                    lora_ctrls.extend([model, weight])

            def refresh_callback():
                try:
                    for name, module in sys.modules.items():
                        if name.endswith("sd_forge_lora.networks"):
                            if hasattr(module, 'list_available_networks'):
                                module.list_available_networks()
                            break
                except:
                    pass
                
                new_list = get_lora_data()
                return [gr.update(choices=new_list) for _ in range(lora_count)]

            refresh_btn.click(fn=refresh_callback, inputs=[], outputs=lora_ctrls[0::2])

        return lora_ctrls

    def process(self, p, *args):
        lora_tags = []
        for i in range(0, len(args), 2):
            model_name = args[i]
            weight = args[i+1]
            
            if model_name and model_name != "None":
                
                if "/" in model_name:
                    name_only = model_name.split("/")[-1]
                elif "\\" in model_name:
                    name_only = model_name.split("\\")[-1]
                else:
                    name_only = model_name
                
                lora_tags.append(f"<lora:{name_only}:{weight}>")
        
        if lora_tags:
            lora_string = " " + " ".join(lora_tags)
            p.all_prompts = [prompt + lora_string for prompt in p.all_prompts]
            print(f"[LoRA Selector] Injected: {lora_string}")