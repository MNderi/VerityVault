import pandas as pd
import numpy as np
from tqdm import tqdm
import nlpaug.augmenter.word as naw
import torch
import argparse

def augment(samples, class_, df, aug, times, text_column="source_article", label_column="updated_label"):
    counter = 0
    np.random.shuffle(samples)
    repetitions = (times // len(samples)) + 1

    for s in tqdm(np.repeat(samples, repetitions)):
        if counter == times:
            break
        df = pd.concat(
            [
                df,
                pd.DataFrame.from_dict(
                    {text_column: aug.augment(s), label_column: class_}
                ),
            ],
            ignore_index=True,
        )
        counter += 1

    return df

def main(train_csv, output_csv, max_upsampling=None, text_column="source_article", label_column="updated_label"):
    df_train = pd.read_csv(train_csv, usecols=[text_column, label_column])
    value_counts = df_train[label_column].value_counts().to_dict()
    print(f"Before augmentation: {value_counts}")

    if max_upsampling:
        differences = {key: max(0, max_upsampling-value) for key, value in value_counts.items()}
    else:
        max_val = max(value_counts.values())
        differences = {key: max_val - value for key, value in value_counts.items()}

    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    aug = naw.ContextualWordEmbsAug(
        model_path="roberta-base",
        top_k=5,
        aug_p=0.2,
        action="substitute",
        device=device,
    )

    for key, value in differences.items():
        print(f"Augmenting class: {key}")
        df_train = augment(
            df_train[df_train[label_column] == key][text_column].to_numpy(),
            key,
            df_train,
            aug,
            value,
            text_column,
            label_column,
        )

    print(f"After augmentation: {df_train[label_column].value_counts().to_dict()}")
    df_train.to_csv(output_csv, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv")
    parser.add_argument("--output_csv")
    parser.add_argument("--max_upsampling", default=None, type=int)
    parser.add_argument("--text_column", default="source_article")
    parser.add_argument("--label_column", default="updated_label")
    args = parser.parse_args()
    main(
        args.input_csv,
        args.output_csv,
        args.max_upsampling,
        args.text_column,
        args.label_column,
    )
