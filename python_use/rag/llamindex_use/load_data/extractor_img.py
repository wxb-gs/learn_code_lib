from llama_index.readers.file import ImageReader
from llama_index.core import SimpleDirectoryReader

#图片阅读器
# image_reader = ImageReader(keep_image=True) 
image_reader = ImageReader(parse_text=True, text_type="plain_text") 

reader = SimpleDirectoryReader(
    input_dir="imgs/",
    file_extractor={".png": image_reader}
)

input_files = reader.load_data()

print(input_files[0].text)