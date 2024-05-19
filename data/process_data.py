import os
import subprocess
import pkg_resources

from marker.convert import convert_single_pdf
from marker.logger import configure_logging
from marker.models import load_all_models

from marker.output import save_markdown

configure_logging()


def convert_folder(path:str  ):

  in_folder = path
  out_folder = path + "_md"

  script_path = pkg_resources.resource_filename(__name__, 'chunk_convert.sh')

  # Construct the command
  cmd = f"{script_path} {in_folder} {out_folder}"

  # Execute the shell script
  subprocess.run(cmd, shell=True, check=True)

def main():

  file_path = "/home/buddy/Study-Buddy/zarchive/data/docs/DT136G-PoDS/Distributed_Systems_4.pdf"
  model_lst = load_all_models()
  full_text, images, out_meta = convert_single_pdf(file_path, model_lst)

  file_path = os.path.basename(file_path)
  subfolder_path = save_markdown(".", file_path, full_text, images, out_meta)

  print(f"Saved markdown to the {subfolder_path} folder")


if __name__ == "__main__":
    main()