import argparse
from Parser.md2block import read_file
from NotionClient import NotionSyncDatabase
from uploader import Md2NotionUploader
from pathlib import Path
from rich.progress import Progress
from rich.traceback import install,Traceback
from rich import print
import os

def get_parameter():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", '-f',help="input file_path")
    parser.add_argument("--connection_key", type=str, help="the notion connection key")
    parser.add_argument("--database_id", type=str, help="the notion database_id")
    parser.add_argument("--smms_token", type=str, help="the smms token")
    parser.add_argument("--start_line", default=0, type=int, help="the start line of the update")
    
    args = parser.parse_args()
    return args


def upload_single_file(filepath, client, uploader,filename=None, start_line = 0):
    if filename is None:
        if isinstance(filepath,Path):
            filename=filepath.name
        else:
            filename = filepath.split('/')[-1]
    # create a new page for this file
    client.create_new_page(filename)
    page_id = client.get_page_id_via_name(filename)
    # get the notion style block information
    notion_blocks = read_file(filepath)
    uploader.local_root = os.path.dirname(filepath)
    notion_blocks=notion_blocks[start_line:]
    with Progress() as prog:
        task=prog.add_task(filename,total=len(notion_blocks))
        for i,content in enumerate(notion_blocks):
            try:
                uploader.uploadBlock(content, client.notion, page_id)
            except Exception as e:
                print(Traceback(e))
                uploader.uploadBlock(content, client.notion, page_id)


            prog.update(task,advance=1)


if __name__ == '__main__':

    install()
    
    d=Path("doc")

    connection_key = "****"
    database_id  = "****"
    client      = NotionSyncDatabase(connection_key, database_id)
    uploader       = Md2NotionUploader(image_host='smms')

    for file in d.iterdir():
        if file.suffix == ".md":
            filepath = file.resolve()
            upload_single_file(filepath, client, uploader)
            


    # args = get_parameter()
    # connection_key = args.connection_key
    # database_id  = args.database_id
    # client      = NotionSyncDatabase(connection_key, database_id)
    # uploader       = Md2NotionUploader(image_host='smms', smms_token=args.smms_token)
    # filepath   = args.file_path
    # start_line = args.start_line
    # upload_single_file(filepath, client, uploader, start_line = start_line)