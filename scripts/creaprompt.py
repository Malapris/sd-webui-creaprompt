import contextlib
import os
import gradio as gr
import random
import pandas as pd
from gradio import components as grc
from modules import scripts
from modules import script_callbacks

script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, "../csv/" )


def send_text_to_prompt(new_text, old_text, Prefix, sufix):
    if Prefix:
        new_text = Prefix + "," + new_text
    if sufix:
        new_text = new_text + "," + sufix
    return new_text
    
def send_before_prompt(new_text, old_text):
    return new_text + "," + old_text
    
def send_after_prompt(new_text, old_text):
    return old_text + "," + new_text    
    
def auto_send_to_final(randprompt):
    return randprompt
    
def read_random_line_from_csv_files(checkbox_group):
    chosen_lines = []
    for idx, filename in enumerate(os.listdir(folder_path)):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            if not df.empty:
                random_index = random.randint(0, len(df))
                random_row = df.iloc[random_index - 1]
                for i, choice in enumerate(checkbox_group):
                    if choice == filename[3:-4]:
                        chosen_lines.extend(map(str, random_row.tolist()))
    concatenated_lines = ",".join(chosen_lines)

    if not any(checkbox_group):
        concatenated_lines = "Please, select a category."
    return concatenated_lines
    
def select_random_line_from_collection():
    file_path = os.path.join(folder_path, "collection.txt")
    if os.path.exists(file_path) and file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            readline = random.choice(lines).strip()
            if lines:
                return readline, readline
            else:
                return "The file is empty."
    else:
        return "The specified file does not exist or is not a text file."    
        
def getfilename():
    name = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
           name.append(filename[3:-4])
    return name
    
def check_all():
        return checkboxes  
        
def uncheck_all():
        return
        
def get_config_files():
    config_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".config"):
            config_files.append(filename[:-7])
    return config_files
    
def load_checkbox_state(selected_file):
    if not selected_file:
        print("Please select a file.")
        return
    file_path = os.path.join(folder_path, selected_file + ".config")
    with open(file_path, "r") as file:
        lines = file.readlines()
        selected_checkboxes = [line.strip() for line in lines]
    return selected_checkboxes
    
def save_checkbox_state(checkbox_group, file_name):
                if not file_name:
                  print("Please enter a file name.")
                  return gr.update(choices=get_config_files())
                if not file_name.endswith('.config'):
                  file_name += '.config'
                  file_path = os.path.join(folder_path, file_name)
                with open(file_path, "w") as file:
                  for checkbox in checkbox_group:
                    file.write(f"{checkbox}\n")
                print("Checkbox state saved successfully.")
                return gr.update(choices=get_config_files(), value= file_name[:-7])            
        
checkboxes = getfilename()          

class CreaPromptScript(scripts.Script):
    def __init__(self) -> None:
        super().__init__()
        
    #checkboxes = getfilename()
    final_element = None

    def title(self):
        return "CreaPrompt"

    def show(self, is_img2img):
        return scripts.AlwaysVisible
        
    def ui(self, is_img2img):
        with gr.Group():
            with gr.Accordion("CreaPrompt", open=False):
              gr.Markdown("# CreaPrompt")
              gr.Markdown("Select the categories you want to use to create the prompt or build your prompt category by category")
              with gr.Row():
                      save_state_button = gr.Button("Save a preset of the selected categories", elem_id="save_state", variant="primary")
                      check_all_button = gr.Button("Select all categories", elem_id="check_all_box", variant="primary")
                      uncheck_all_button = gr.Button("Deselect all categories", elem_id="uncheck_all_box", variant="primary")
              with gr.Row():
                      file_name_textbox = grc.Textbox(label="Enter a file name to save the preset:", elem_id="file_name", show_label=True, placeholder="Enter file name here", container=True)
                      file_dropdown_component = gr.Dropdown(label="Choose your category preset:", choices=get_config_files(), elem_id="file_dropdown", value="Select a categories preset")
              with gr.Column():
                      gr.Markdown("#")
                      checkbox_group = grc.CheckboxGroup(label="Select Categories", choices=checkboxes, default=['base'], min_width=50)
              with gr.Column(scale=3):
                      gr.Markdown("#")
                      final = grc.Textbox(label="Final prompt which will be used to generate the image:", elem_id="creaprompt_prompt_final", show_label=True, lines=2, placeholder="The final prompt is displayed here", container=True)
                      CreaPromptScript.final_element = final
                      Prefix = grc.Textbox(label="Prefix of the Prompt:", elem_id="promptgen_prompt_prefix", show_label=True, lines=2, placeholder="Type your prefix or leave blank if you don't want it", container=True)
                      sufix = grc.Textbox(label="Suffix of the Prompt:", elem_id="promptgen_prompt_sufix", show_label=True, lines=2, placeholder="Type your suffix or leave blank if you don't want it", container=True)
                      prompt = grc.Textbox(label="Created Prompt from categories:", elem_id="promptgen_prompt", show_label=True, lines=2, placeholder="Make the selection of your choice and Click Generate button", container=True)
                      with gr.Row():
                            gr.Markdown("# ")
                      with gr.Row():
                            gr.Markdown("# Create prompt manually")
                      with gr.Row():      
                            gr.Markdown("Press the normal generate button to start generating image with the final prompt")
                      with gr.Row():
                            Sendbefore = gr.Button('Add before final prompt', elem_id="promptgen_sendto_img", variant='primary')
                            send_text_button = gr.Button(value='Replace final prompt', variant='primary')
                            Sendafter = gr.Button('Add after final prompt', elem_id="promptgen_sendto_txt", variant='primary')                            
                      with gr.Column(scale=1):
                            gr.Markdown("#")
                            with gr.Row():
                                submit = gr.Button('Create prompt from categories', elem_id="promptgen_generate", variant='primary')
                            with gr.Column(scale=1):
                                 gr.Markdown("# ")
                                 gr.Markdown("# Prompts collection")
                                 gr.Markdown("Choose one prompt from the collection and press the normal generate button")
                                 with gr.Row():
                                    submitcollection = gr.Button('Choose one prompt from collection', elem_id="promptgen_generate_collection", variant='primary')
                                 with gr.Column(scale=1):
                                    gr.Markdown("# ")
                                    gr.Markdown("# Auto prompting")
                                    gr.Markdown("When activated, just press the normal generate button, it also works with batch, don't forget to choose your categories")
                                    is_enabled = grc.Checkbox(label="Enable auto prompting", info="Enable Or Disable auto prompting", value=False)
                                    is_randomize = grc.Checkbox(label="Enable random prompts", info="Enable or Disable random prompts for each images in batch", value=False)
                                    gr.Markdown("# ")
                                    
        with contextlib.suppress(AttributeError):
   
            check_all_button.click(check_all, inputs=[], outputs=[checkbox_group])
            uncheck_all_button.click(uncheck_all, inputs=[], outputs=[checkbox_group])
            save_state_button.click(save_checkbox_state, inputs= [checkbox_group, file_name_textbox], outputs=[file_dropdown_component])                        
            file_dropdown_component.change(load_checkbox_state, inputs=[file_dropdown_component], outputs=[checkbox_group])
            
            if is_img2img:
                submitcollection.click(
                           fn=select_random_line_from_collection,
                           outputs=[self.boxxIMG, final]
                          ) 
                submit.click(
                           fn=read_random_line_from_csv_files,
                           inputs=checkbox_group,
                           outputs=prompt
                          )        
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxxIMG], outputs=[self.boxxIMG])
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxxIMG], outputs=[final])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxxIMG], outputs=[self.boxxIMG])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxxIMG], outputs=[final])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxxIMG, Prefix, sufix], outputs=[self.boxxIMG])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxxIMG, Prefix, sufix], outputs=[final])
            else:
                submitcollection.click(
                           fn=select_random_line_from_collection,
                           outputs=[self.boxx, final]
                          ) 
                submit.click(
                           fn=read_random_line_from_csv_files,
                           inputs=checkbox_group,
                           outputs=prompt
                          )        
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxx], outputs=[self.boxx])
                Sendbefore.click(fn=send_before_prompt, inputs=[prompt, self.boxx], outputs=[final])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxx], outputs=[self.boxx])
                Sendafter.click(fn=send_after_prompt, inputs=[prompt, self.boxx], outputs=[final])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxx, Prefix, sufix], outputs=[self.boxx])
                send_text_button.click(fn=send_text_to_prompt, inputs=[prompt, self.boxx, Prefix, sufix], outputs=[final])
        return [is_enabled, Prefix, sufix, checkbox_group, is_randomize]
        
    def process(self, p, is_enabled, prefix, sufix, checkbox_group, is_randomize):
        if not is_enabled:
            return

        batchCount = len(p.all_prompts)

        if(batchCount == 1):
            # for each image in batch
            for i, prompt in enumerate(p.all_prompts):
                randprompt= read_random_line_from_csv_files(checkbox_group)
                if prefix:
                   randprompt = prefix + "," + randprompt
                if sufix:
                   randprompt = randprompt + "," + sufix
            p.all_prompts[i] = randprompt
            print("Prompt used for auto prompting:" + " " + randprompt)
            
        if(batchCount > 1):
            randprompts = {}
            randprompt = ""
            for i, prompt in enumerate(p.all_prompts):
                if(is_randomize):
                   randprompt = read_random_line_from_csv_files(checkbox_group)
                   if prefix:
                      randprompt = prefix + "," + randprompt
                   if sufix:
                      randprompt = randprompt + "," + sufix
                   randprompts[i] = randprompt
                   p.all_prompts[i] = randprompts[i]
                   print("Prompt used for auto prompting:" + " " + randprompts[i])
                else:
                    if i == 0:
                      randprompt = read_random_line_from_csv_files(checkbox_group)
                      if prefix:
                         randprompt = prefix + "," + randprompt
                      if sufix:
                         randprompt = randprompt + "," + sufix
                      print("Prompt used for auto prompting:" + " " + randprompt)
                p.all_prompts[i] = randprompt
        

    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_prompt":
            self.boxx = component
        if kwargs.get("elem_id") == "img2img_prompt":
            self.boxxIMG = component









