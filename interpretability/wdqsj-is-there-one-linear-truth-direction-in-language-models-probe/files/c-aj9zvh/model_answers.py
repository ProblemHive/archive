"""Does Qwen2.5-0.5B (base) itself judge negated statements correctly?
Few-shot prompt, then the statement, then 'This statement is'; score = logit(' TRUE') - logit(' FALSE')
at the next token. Reported: accuracy at threshold 0 and AUROC of the score against the label.
The four few-shot examples are fixed, written here, and not taken from the datasets.
"""
import numpy as np, pandas as pd, torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.metrics import roc_auc_score
M = "/data/wdqsj/qwen2.5-0.5b"; D = "/data/wdqsj/got"
tok = AutoTokenizer.from_pretrained(M); tok.padding_side = "left"
model = AutoModelForCausalLM.from_pretrained(M, torch_dtype=torch.float32).to("cuda").eval()
shots = ("The sky on a clear day is blue. This statement is TRUE\n"
         "Paris is not in France. This statement is FALSE\n"
         "Two plus two is five. This statement is FALSE\n"
         "Water is not a metal. This statement is TRUE\n")
t_id = tok(" TRUE", add_special_tokens=False).input_ids; f_id = tok(" FALSE", add_special_tokens=False).input_ids
print("token ids", t_id, f_id)
for n in ["cities", "neg_cities", "sp_en_trans", "neg_sp_en_trans", "larger_than", "smaller_than"]:
    df = pd.read_csv(f"{D}/{n}.csv"); y = df["label"].astype(int).to_numpy()
    prompts = [shots + s + " This statement is" for s in df["statement"]]
    sc = []
    with torch.no_grad():
        for i in range(0, len(prompts), 64):
            b = tok(prompts[i:i + 64], return_tensors="pt", padding=True).to("cuda")
            lg = model(**b).logits[:, -1].float()
            sc.append((lg[:, t_id[0]] - lg[:, f_id[0]]).cpu().numpy())
    sc = np.concatenate(sc)
    print("%-16s n=%5d  accuracy %.3f  AUROC %.3f  share answered TRUE %.3f" % (n, len(y), ((sc > 0) == y).mean(), roc_auc_score(y, sc), (sc > 0).mean()))
