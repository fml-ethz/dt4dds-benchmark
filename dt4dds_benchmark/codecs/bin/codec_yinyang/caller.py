# the script is based on the test script provided by the authors of the codec (https://github.com/ntpz870817/DNA-storage-YYC/blob/master/examples/test_mona_lisa.py).
# @article{ping2022towards,
#   title={Towards practical and robust DNA-based data archiving using the yin--yang codec system},
#   author={Ping, Zhi and Chen, Shihong and Zhou, Guangyu and Huang, Xiaoluo and Zhu, Sha Joe and Zhang, Haoling and Lee, Henry H and Lan, Zhaojun and Cui, Jie and Chen, Tai and others},
#   journal={Nature Computational Science},
#   pages={234--242},
#   year={2022},
#   volume={2},
#   number={4},
#   publisher={Nature Publishing Group}
# }
# All rights lie with the original authors.

import argparse
from yyc import pipeline, scheme

[support_base, rule1, rule2] = ["A", [1, 0, 0, 1], [[0, 1, 0, 1], [1, 1, 0, 0], [1, 0, 1, 0], [0, 0, 1, 1]]]

p = argparse.ArgumentParser()
p.add_argument('-m', '--mode', choices=['encode', 'decode'], help='Whether to encode or decode')
p.add_argument('-i', '--input_path', help='Input file path')
p.add_argument('-o', '--output_path', help='Output file path')
p.add_argument('-s', '--supplementary_path', help='Supplementary file path')
p.add_argument('-c', '--search_count', default=100, help='Search count')
p.add_argument('-p', '--max_homopolymer', default=4, help='Maximum homopolymer')
p.add_argument('-g', '--max_gc', default=0.6, help='Maximum GC content')
p.add_argument('-l', '--segment_length', default=120, help='Seqgment length')

args = p.parse_args()

tool = scheme.YYC(
    support_bases=support_base, 
    base_reference=rule1, 
    current_code_matrix=rule2,
    search_count=args.search_count, 
    max_homopolymer=int(args.max_homopolymer), 
    max_content=float(args.max_gc)
)

if args.mode == 'encode':
    pipeline.encode(
        method=tool,
        input_path=args.input_path,
        output_path=args.output_path,
        model_path=args.supplementary_path,
        segment_length=int(args.segment_length),
        need_index=True,
        need_log=True
    )
elif args.mode == 'decode':
    pipeline.decode(
        model_path=args.supplementary_path,
        input_path=args.input_path,
        output_path=args.output_path,
        has_index=True,
        need_log=True
    )