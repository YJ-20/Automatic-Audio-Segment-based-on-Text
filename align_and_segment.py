import os
import time
import torch
import torchaudio
import sox
import argparse


from text_normalization import text_normalize
from align_utils import (
    get_uroman_tokens,
    time_to_frame,
    load_model_dict,
    merge_repeats,
    get_spans,
)
import torchaudio.functional as F

import pandas as pd
SAMPLING_FREQ = 16000
EMISSION_INTERVAL = 30
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def generate_emissions(model, audio_file):
    waveform, sr = torchaudio.load(audio_file)  # waveform: channels X T
    waveform = torchaudio.transforms.Resample(sr, SAMPLING_FREQ)(waveform)
    waveform = waveform.to(DEVICE)
    total_duration = sox.file_info.duration(audio_file)

    emissions_arr = []
    with torch.inference_mode():
        i = 0
        while i < total_duration:
            segment_start_time, segment_end_time = (i, i + EMISSION_INTERVAL)

            context = EMISSION_INTERVAL * 0.1
            input_start_time = max(segment_start_time - context, 0)
            input_end_time = min(segment_end_time + context, total_duration)
            waveform_split = waveform[
                :,
                int(SAMPLING_FREQ * input_start_time) : int(
                    SAMPLING_FREQ * (input_end_time)
                ),
            ]

            model_outs, _ = model(waveform_split)
            emissions_ = model_outs[0]
            emission_start_frame = time_to_frame(segment_start_time)
            emission_end_frame = time_to_frame(segment_end_time)
            offset = time_to_frame(input_start_time)

            emissions_ = emissions_[
                emission_start_frame - offset : emission_end_frame - offset, :
            ]
            emissions_arr.append(emissions_)
            i += EMISSION_INTERVAL

    emissions = torch.cat(emissions_arr, dim=0).squeeze()
    emissions = torch.log_softmax(emissions, dim=-1)

    stride = float(waveform.size(1) * 1000 / emissions.size(0) / SAMPLING_FREQ)

    return emissions, stride

def get_alignments(
    audio_file,
    tokens,
    model,
    dictionary,
    use_star,
):
    # Generate emissions
    emissions, stride = generate_emissions(model, audio_file)
    T, N = emissions.size()
    if use_star:
        emissions = torch.cat([emissions, torch.zeros(T, 1).to(DEVICE)], dim=1)

    # Force Alignment
    if tokens:
        token_indices = [dictionary[c] for c in " ".join(tokens).split(" ") if c in dictionary]
    else:
        print(f"Empty transcript!!!!! for audio file {audio_file}")
        token_indices = []

    blank = dictionary["<blank>"]
    
    targets = torch.tensor(token_indices, dtype=torch.int32).to(DEVICE)
    input_lengths = torch.tensor(emissions.shape[0])
    target_lengths = torch.tensor(targets.shape[0])

    path, _ = F.forced_align(
        emissions, targets, input_lengths, target_lengths, blank=blank
    )
    path = path.to("cpu").tolist()
    segments = merge_repeats(path, {v: k for k, v in dictionary.items()})
    return segments, stride

def main_for_ui(text_filepath, audio_filepath, outdir="split_output", sheet_name=0, uroman_path="uroman/bin", lang="eng", use_star=False):
    transcripts = []
    if text_filepath.endswith(".txt"):
        with open(text_filepath, encoding='UTF8') as f:
            transcripts = [line.strip() for line in f]
        print("Read {} lines from {}".format(len(transcripts), text_filepath))
    elif text_filepath.endswith(".csv"):
        transcripts = pd.read_csv(text_filepath, header=None)[0].tolist()
        transcripts = [str(t).strip() for t in transcripts if t]
    elif text_filepath.endswith(".xlsx"):
        transcripts = pd.read_excel(text_filepath, header=None, sheet_name=sheet_name)[0].tolist()
        transcripts = [str(t).strip() for t in transcripts if t]
    else:
        raise ValueError("Unsupported text file format")
    norm_transcripts = [text_normalize(line.strip(), lang) for line in transcripts]
    tokens = get_uroman_tokens(norm_transcripts, uroman_path, lang)

    model, dictionary = load_model_dict()
    model = model.to(DEVICE)

    segments, stride = get_alignments(
        audio_filepath,
        tokens,
        model,
        dictionary,
        use_star,
    )
    # Get spans of each line in input text file
    spans = get_spans(tokens, segments)

    os.makedirs(outdir, exist_ok=True)
    
    splitted_audio_info = pd.DataFrame(columns=["audio_start_sec", "audio_filepath", "duration", "text"])
    for i, t in enumerate(transcripts):
        span = spans[i]
        seg_start_idx = span[0].start
        seg_end_idx = span[-1].end

        output_file = f"{outdir}/segment{i}.wav"

        audio_start_sec = seg_start_idx * stride / 1000
        audio_end_sec = seg_end_idx * stride / 1000 

        tfm = sox.Transformer()
        tfm.trim(audio_start_sec , audio_end_sec)
        tfm.build_file(audio_filepath, output_file)
        
        splitted_audio_info.loc[i] = [audio_start_sec, str(output_file), audio_end_sec - audio_start_sec, t]
    
    splitted_audio_info.to_csv(f"{outdir}/splitted_audio_info.csv", index=False, encoding="utf-8-sig")
    print("#"*100)
    print("결과가 다음 위치에 저장되었습니다.\n", f"{outdir}/segment*.wav\n", f"{outdir}/splitted_audio_info.csv")
    print("#"*100)    
    return segments, stride

def main(args):
    # assert not os.path.exists(
    #     args.outdir
    # ), f"Error: Output path exists already {args.outdir}"
    
    transcripts = []
    if args.text_filepath.endswith(".txt"):
        with open(args.text_filepath) as f:
            transcripts = [line.strip() for line in f]
        print("Read {} lines from {}".format(len(transcripts), args.text_filepath))
    elif args.text_filepath.endswith(".csv"):
        transcripts = pd.read_csv(args.text_filepath, header=None)[0].tolist()
        transcripts = [str(t).strip() for t in transcripts if t]
    elif args.text_filepath.endswith(".xlsx"):
        transcripts = pd.read_excel(args.text_filepath, header=None)[0].tolist()
        transcripts = [str(t).strip() for t in transcripts if t]
    else:
        raise ValueError("Unsupported text file format")
    norm_transcripts = [text_normalize(line.strip(), args.lang) for line in transcripts]
    tokens = get_uroman_tokens(norm_transcripts, args.uroman_path, args.lang)

    model, dictionary = load_model_dict()
    model = model.to(DEVICE)
    if args.use_star:
        dictionary["<star>"] = len(dictionary)
        tokens = ["<star>"] + tokens
        transcripts = ["<star>"] + transcripts
        norm_transcripts = ["<star>"] + norm_transcripts

    segments, stride = get_alignments(
        args.audio_filepath,
        tokens,
        model,
        dictionary,
        args.use_star,
    )
    # Get spans of each line in input text file
    spans = get_spans(tokens, segments)

    os.makedirs(args.outdir, exist_ok=True)
    
    splitted_audio_info = pd.DataFrame(columns=["audio_start_sec", "audio_filepath", "duration", "text"])
    for i, t in enumerate(transcripts):
        span = spans[i]
        seg_start_idx = span[0].start
        seg_end_idx = span[-1].end

        output_file = f"{args.outdir}/segment{i}.wav"

        audio_start_sec = seg_start_idx * stride / 1000
        audio_end_sec = seg_end_idx * stride / 1000 

        tfm = sox.Transformer()
        tfm.trim(audio_start_sec , audio_end_sec)
        tfm.build_file(args.audio_filepath, output_file)
        
        splitted_audio_info.loc[i] = [audio_start_sec, str(output_file), audio_end_sec - audio_start_sec, t]
        # sample = {
        #     "audio_start_sec": audio_start_sec,
        #     "audio_filepath": str(output_file),
        #     "duration": audio_end_sec - audio_start_sec,
        #     "text": t,
        # }
        # splitted_audio_info.append(sample, ignore_index=True)
    splitted_audio_info.to_csv(f"{args.outdir}/splitted_audio_info.csv", index=False, encoding="utf-8-sig")
    
    # with open( f"{args.outdir}/manifest.json", "w") as f:
    #     for i, t in enumerate(transcripts):
    #         span = spans[i]
    #         seg_start_idx = span[0].start
    #         seg_end_idx = span[-1].end

    #         output_file = f"{args.outdir}/segment{i}.wav"

    #         audio_start_sec = seg_start_idx * stride / 1000
    #         audio_end_sec = seg_end_idx * stride / 1000 

    #         tfm = sox.Transformer()
    #         tfm.trim(audio_start_sec , audio_end_sec)
    #         tfm.build_file(args.audio_filepath, output_file)
            
    #         sample = {
    #             "audio_start_sec": audio_start_sec,
    #             "audio_filepath": str(output_file),
    #             "duration": audio_end_sec - audio_start_sec,
    #             "text": t,
    #             "normalized_text":norm_transcripts[i],
    #             "uroman_tokens": tokens[i],
    #         }
    #         f.write(json.dumps(sample) + "\n")

    return segments, stride


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Align and segment long audio files")
    parser.add_argument(
        "-a", "--audio_filepath", type=str, help="Path to input audio file"
    )
    parser.add_argument(
        "-t", "--text_filepath", type=str, help="Path to input text file "
    )
    parser.add_argument(
        "-l", "--lang", type=str, default="eng", help="ISO code of the language"
    ) # 한국어, 일본어 영어는 모두 eng로 처리 가능
    parser.add_argument(
        "-u", "--uroman_path", type=str, default="uroman/bin", help="Location to uroman/bin"
    )
    parser.add_argument(
        "-s",
        "--use_star",
        action="store_true",
        help="Use star at the start of transcript",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        default="split_output",
        type=str,
        help="Output directory to store segmented audio files",
    )
    print("Using torch version:", torch.__version__)
    print("Using torchaudio version:", torchaudio.__version__)
    print("Using device: ", DEVICE)
    args = parser.parse_args()
    
    start = time.time()
    main(args)
    end = time.time()
    print(f"Time taken: {end - start} seconds")
