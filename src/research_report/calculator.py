from reportlab.platypus import Image
import pandas as pd
from typing import Dict
import os
import cv2
import matplotlib.pyplot as plt
import io
import re


### 페이지 계산
def calculate_layout(
  ratios: Dict[str, float], 
  page_size: tuple, 
  logger, 
  topcut_mode: bool = False
) -> Dict:

  page_width, page_height = page_size
  margin_ratio = ratios["margin_ratio"]
  left_margin   = page_width  * margin_ratio
  right_margin  = page_width  * margin_ratio
  top_margin    = page_height * margin_ratio
  bottom_margin = page_height * margin_ratio

  usable_width  = (page_width  - left_margin - right_margin)
  usable_height = (page_height - top_margin - bottom_margin)
  logger.info(f"usable_page_width: {usable_width}")
  logger.info(f"usable_page_height: {usable_height}")

  if topcut_mode:
    total = ratios["middle_ratio"] + ratios["bottom_ratio"]
    new_middle_ratio = ratios["middle_ratio"] / total
    new_bottom_ratio = ratios["bottom_ratio"] / total
    middle_height = usable_height * new_middle_ratio
    bottom_height = usable_height * new_bottom_ratio
    top_height = 0
    logger.info(f"(Topcut mode) middle height: {middle_height}")
    logger.info(f"(Topcut mode) bottom height: {bottom_height}")
  else:
    top_height    = usable_height * ratios["top_ratio"]
    middle_height = usable_height * ratios["middle_ratio"]
    bottom_height = usable_height * ratios["bottom_ratio"]
    logger.info(f"top height: {top_height}")
    logger.info(f"middle height: {middle_height}")
    logger.info(f"bottom height: {bottom_height}")

  layout = {
    "page_width": page_width,
    "page_height": page_height,
    "left_margin": left_margin,
    "right_margin": right_margin,
    "top_margin": top_margin,
    "bottom_margin": bottom_margin,
    "usable_width": usable_width,
    "usable_height": usable_height,
    "top_height": top_height,
    "middle_height": middle_height,
    "bottom_height": bottom_height
  }

  return layout

### 하단 이미지 추출 및 병합 함수
def extract_and_merge_image(
    paths: dict,
    df: pd.DataFrame,
    img_width: float,
    img_height: float, 
    video_mode: bool, 
    logger
) -> Image:

    video_path = paths["video_path"]
    image_path = paths["image_path"]
    
    fig = plt.figure(figsize=(img_width / 100, img_height / 100), constrained_layout=True)
    axes = []

    # 2행 3열의 subplot 생성
    for i in range(6):
      ax = plt.subplot(2, 3, i + 1)
      axes.append(ax)

    video_files = df["파일명"].unique()
    frames = []

    for file in video_files:
      logger.debug(f"file reading...:{file}")
      if re.search(r'[가-힣]', file):
        logger.info(f"공휴일 : {file}")
        continue

      if video_mode:
        full_path = os.path.join(video_path, file)
        if not os.path.exists(full_path):
          logger.warning(f"video file not found: {file}")
          continue

        cap = cv2.VideoCapture(full_path)
        ret, frame = cap.read()
        if ret:
          frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
          frames.append(frame)
        cap.release()
      
      else:
        jpg_file = os.path.splitext(file)[0] + ".jpg"
        full_path = os.path.join(image_path, jpg_file)
        if not os.path.exists(full_path):
            logger.warning(f"image file not found: {jpg_file}")
            continue

        logger.debug(f"image file reading...: {jpg_file}")
        frame = cv2.imread(full_path)
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)
        else:
            logger.warning(f"failed to read image: {jpg_file}")

    for idx, ax in enumerate(axes):
        if idx < len(frames):
            axes[idx].imshow(frames[idx], aspect='auto', extent=[0, 1, 0, 1])
            axes[idx].set_xticks([])
            axes[idx].set_yticks([])
            axes[idx].set_frame_on(False)

    for j in range(len(frames), len(axes)):
        fig.delaxes(axes[j])

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    img_buffer.seek(0)

    merged_img = Image(img_buffer)

    return merged_img
