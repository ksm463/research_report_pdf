from reportlab.platypus import Frame, Paragraph, Table, TableStyle, Spacer, KeepInFrame
from reportlab.lib import colors
import pandas as pd
from datetime import timedelta
from typing import Dict

from calculator import extract_and_merge_image


### 프레임 설정
def setup_page_frames(layout: Dict[str, str], topcut_mode: bool, frame_boundary: bool) -> Frame:
  if topcut_mode:
    middle_frame_y = layout["page_height"] - layout["top_margin"] - layout["middle_height"]
    bottom_frame_y = middle_frame_y - layout["bottom_height"]
    middle_frame = Frame(layout["left_margin"], middle_frame_y, layout["usable_width"], layout["middle_height"], showBoundary=frame_boundary)
    bottom_frame = Frame(layout["left_margin"], bottom_frame_y, layout["usable_width"], layout["bottom_height"], showBoundary=frame_boundary)
    return middle_frame, bottom_frame
  else:
    top_frame_y    = layout["page_height"] - layout["top_margin"] - layout["top_height"]
    middle_frame_y = top_frame_y - layout["middle_height"]
    bottom_frame_y = middle_frame_y - layout["bottom_height"]
    top_frame = Frame(layout["left_margin"], top_frame_y, layout["usable_width"], layout["top_height"], showBoundary=frame_boundary)
    middle_frame = Frame(layout["left_margin"], middle_frame_y, layout["usable_width"], layout["middle_height"], showBoundary=frame_boundary)
    bottom_frame =  Frame(layout["left_margin"], bottom_frame_y, layout["usable_width"], layout["bottom_height"], showBoundary=frame_boundary)
    return top_frame, middle_frame, bottom_frame

### 상단(top) 내용: 작업 정보 ###
def create_top_contents(
    df: pd.DataFrame,
    week_number: int,
    layout: Dict[str, str],
    top_ratios: Dict[str, str], 
    styles, 
    list_cell_style
 ) -> Frame:

  df_week = df[df["주차"] == week_number]

  top_table_data = [[Paragraph("이름", list_cell_style),
                    Paragraph("수행 날짜", list_cell_style),
                    Paragraph("직책", list_cell_style),
                    Paragraph("주차", list_cell_style)]]

  for week, group in df_week.groupby("주차"):
    start_date = group["할당일"].min()
    end_date = start_date + timedelta(days=4)
    date_range = f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"

    name = group.iloc[0]["작업자 이름(한글)"]
    position = group.iloc[0]["직책"]

    row = [Paragraph(str(name), list_cell_style),
            Paragraph(date_range, list_cell_style),
            Paragraph(str(position), list_cell_style),
            Paragraph(str(week), list_cell_style)]
    top_table_data.append(row)

  col_widths = [
      layout["usable_width"]*top_ratios["name_width"],
      layout["usable_width"]*top_ratios["days_width"],
      layout["usable_width"]*top_ratios["position_width"],
      layout["usable_width"]*top_ratios["week_width"]
  ]

  top_table = Table(top_table_data, colWidths=col_widths)
  top_table.setStyle(TableStyle([
      ("GRID", (0,0), (-1,-1), 1, colors.black),
      ("BACKGROUND", (0,0), (-1,0), colors.grey),
      ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
      ("ALIGN", (0,0), (-1,-1), "CENTER"),
      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
  ]))

  topContents = [
      Paragraph("작업 정보", styles["Korean"]),
      Spacer(1, 10),
      top_table
  ]

  top_flow = KeepInFrame(layout["usable_width"], layout["top_height"], topContents, mode='truncate')

  return top_flow

### 중단(middle) 내용: 작업 리스트 표 ###
def create_middle_contents(
    df: pd.DataFrame,
    week_number: int,
    max_rows: int,
    layout: Dict[str, str],
    middle_ratios: Dict[str, str], 
    styles, 
    list_cell_style
) -> Frame:

  df_week = df[df["주차"] == week_number]

  work_list_data = [[Paragraph("Index", list_cell_style),
                    Paragraph("날짜", list_cell_style),
                    Paragraph("파일 이름", list_cell_style),
                    Paragraph("비고", list_cell_style)]]

  df_week_sorted = df_week.sort_values("할당일")
  for idx, row in enumerate(df_week_sorted.itertuples(index=False), start=1):
    date_str = row.할당일.strftime('%Y-%m-%d')
    filename = row.파일명
    work_list_data.append([
          Paragraph(str(idx), list_cell_style),
          Paragraph(date_str, list_cell_style),
          Paragraph(filename, list_cell_style),
          Paragraph("", list_cell_style)
      ])

  current_rows = len(work_list_data) - 1
  if current_rows < max_rows:
      for i in range(current_rows + 1, max_rows + 1):
          work_list_data.append([
              Paragraph(str(i), list_cell_style),
              Paragraph("", list_cell_style),
              Paragraph("", list_cell_style),
              Paragraph("", list_cell_style)
          ])

  col_widths = [
      layout["usable_width"]*middle_ratios["index_width"],
      layout["usable_width"]*middle_ratios["day_width"],
      layout["usable_width"]*middle_ratios["filename_width"],
      layout["usable_width"]*middle_ratios["note_width"]
  ]

  work_list_table = Table(work_list_data, colWidths = col_widths)
  work_list_table.setStyle(TableStyle([
      ("GRID", (0,0), (-1,-1), 1, colors.black),
      ("BACKGROUND", (0,0), (-1,0), colors.darkgray),
      ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
      ("ALIGN", (0,0), (-1,-1), "CENTER"),
      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
  ]))

  middleContents = [
      Paragraph("<b>작업 리스트</b>", styles["Korean"]),
      Spacer(1, 10),
      work_list_table
  ]
  middle_flow = KeepInFrame(layout["usable_width"], layout["middle_height"], middleContents, mode='truncate')

  return middle_flow

### 하단(bottom) 내용: 예시 이미지 ###
def create_bottom_contents(
    df: pd.DataFrame,
    week_number: int,
    paths: Dict[str, str],
    layout: Dict[str, str],
    bottom_ratios: Dict[str, str], 
    styles,
    video_mode, 
    logger
) -> Frame:

  df_week = df[df["주차"] == week_number]

  bottomContents = [
      Paragraph("예시 이미지", styles["Korean"]),
      Spacer(1, 10)
  ]

  try:
    img_width = layout["usable_width"] * bottom_ratios["img_width"]
    img_height = layout["bottom_height"] * bottom_ratios["img_height"]

    merged_image = extract_and_merge_image(paths, df_week, img_width, img_height, video_mode, logger)

    bottomContents.append(merged_image)
    bottom_flow = KeepInFrame(layout["usable_width"], layout["bottom_height"], bottomContents, mode='truncate')

    return bottom_flow

  except Exception as e:
      bottomContents.append(Paragraph(f"이미지 로드 실패: {e}", styles["Korean"]))
