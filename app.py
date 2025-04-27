import streamlit as st
import pandas as pd
import zipfile
import io
from googletrans import Translator

st.title("🌎 日本語SRT・SBV一括翻訳＆ダウンロードツール")

# 言語リスト（ターゲット言語）
languages = {
    "英語": "en",
    "スペイン語": "es",
    "フランス語": "fr",
    "ロシア語": "ru",
    "中国語（簡体字）": "zh-cn",
    "韓国語": "ko"
}

uploaded_file = st.file_uploader("日本語の.srt または .sbv ファイルをアップロードしてください", type=["srt", "sbv"])

if uploaded_file is not None:
    filename = uploaded_file.name
    srt_text = uploaded_file.read().decode("utf-8")
    lines = srt_text.splitlines()

    translator = Translator()

    # タイムコードとテキストの分離
    timed_blocks = []
    block = {"index": "", "time": "", "text": ""}
    idx = 1

    if filename.endswith(".sbv"):
        # SBV形式用の処理
        for line in lines:
            if "," in line and "." in line:
                if block["index"]:
                    timed_blocks.append(block)
                    block = {"index": "", "time": "", "text": ""}
                start_end = line.split(",")
                start = start_end[0].replace(".", ",")
                end = start_end[1].replace(".", ",")
                block["index"] = str(idx)
                idx += 1
                block["time"] = f"{start} --> {end}"
            elif line.strip() == "":
                continue
            else:
                if block["text"]:
                    block["text"] += "\n" + line
                else:
                    block["text"] = line
        if block["index"]:
            timed_blocks.append(block)
    else:
        # SRT形式用の処理
        for line in lines:
            if line.isdigit():
                if block["index"]:
                    timed_blocks.append(block)
                    block = {"index": "", "time": "", "text": ""}
                block["index"] = line
            elif "-->" in line:
                block["time"] = line
            elif line.strip() == "":
                continue
            else:
                if block["text"]:
                    block["text"] += "\n" + line
                else:
                    block["text"] = line
        if block["index"]:
            timed_blocks.append(block)

    # 各言語ごとの翻訳SRT生成
    translated_srt_files = {}
    for lang_name, lang_code in languages.items():
        translated_blocks = []
        for block in timed_blocks:
            try:
                translated_text = translator.translate(block["text"], src='ja', dest=lang_code).text
            except Exception:
                translated_text = block["text"]  # 翻訳失敗時は日本語のまま
            translated_blocks.append(f"{block['index']}\n{block['time']}\n{translated_text}\n")

        srt_content = "\n".join(translated_blocks)
        translated_srt_files[f"{lang_name}.srt"] = srt_content

    # ZIPにまとめる
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename, content in translated_srt_files.items():
            zip_file.writestr(filename, content)

    st.success("✅ 翻訳が完了しました！")
    st.download_button(
        label="📦 翻訳済みSRTをZIPでダウンロード",
        data=zip_buffer.getvalue(),
        file_name="translated_srt_files.zip",
        mime="application/zip"
    )

else:
    st.info("まずは日本語の.srt または .sbv ファイルをアップロードしてください。")