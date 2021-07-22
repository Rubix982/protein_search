# %%
from jina.types.document.generators import from_csv
from jina import DocumentArray, Flow

from my_executors import ProtBertExecutor, MyIndexer
from backend_config import protein_path, embeddings_path, dataset_url, print_logs, num_proteins
from utils import load_or_download

import os

# %%

def main():
    url = dataset_url
    pdb_data_path = protein_path

    with load_or_download(url, pdb_data_path) as data_file:
        docs_generator = from_csv(
            fp=data_file,
            field_resolver={
                "sequence": "text",
                "structureId": "id"
            }
        )
        proteins = DocumentArray(docs_generator)[0:num_proteins]

    flow = (
        Flow(port_expose=12345, protocol='http')
        .add(uses=ProtBertExecutor)
        .add(uses=MyIndexer)
    )

    with flow:
        import time
        from datetime import datetime

        if print_logs:
            start = time.time()
            flow.index(proteins)
            end = time.time()
            if os.path.exists('logs/username.txt'):
                name = ''
                with open('logs/username.txt', 'r') as f:
                    name = f.readline().replace("\n", "")

                with open(f'logs/{name}/index_time.txt', 'a+') as f:
                    f.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M")} | Indexing {num_proteins} proteins took {end-start:.1f} s\n')
            else:
                print('log username missing. Create logs/username.txt containing your username')

        flow.index(proteins)
        flow.block()


if __name__ == "__main__":
    main()

