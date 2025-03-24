from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, FrameBreak, PageBreak
import pandas as pd
from pathlib import Path
import configparser
import sys

from calculator import calculate_layout
from frames import setup_page_frames, create_top_contents, create_middle_contents, create_bottom_contents
from logger import setup_logger


def generate_pdf():
  try:
    config_path = "/research_report_pdf/src/research_report/config.ini"
    config = configparser.ConfigParser()
    config.read(config_path)

    paths = {
      "pdf_path": config['PATHS']['PDF_PATH'],
      "csv_path": config['PATHS']['CSV_PATH'],
      "video_path": config['PATHS']['VIDEO_PATH'],
      "image_path": config['PATHS']['IMAGE_PATH'],
      "font_path": config['PATHS']['FONT_PATH'],
      "log_path": config['PATHS']['LOG_PATH'],
    }

    start_week = config.getint('PARAMETERS', 'START_WEEK')
    target_week = config.getint('PARAMETERS', 'TARGET_WEEK')
    max_rows = config.getint('PARAMETERS', 'MAX_ROWS')
    frame_boundary = config.getboolean('PARAMETERS', 'FRAME_BOUNDARY')
    topcut_mode = config.getboolean('PARAMETERS', 'TOPCUT_MODE')
    total_document = config.getboolean('PARAMETERS', 'TOTAL_DOCUMENT')
    video_mode = config.getboolean('PARAMETERS', 'VIDEO_MODE')
    
    page_size_str = config['PARAMETERS'].get('PAGE_SIZE', 'A4')
    if page_size_str.upper() == "A4":
      page_size = A4
    else:
      page_size = A4

    ratios = {
      "margin_ratio": config.getfloat('RATIOS', 'MARGIN_RATIO'),
      "top_ratio": config.getfloat('RATIOS', 'TOP_RATIO'),
      "middle_ratio": config.getfloat('RATIOS', 'MIDDLE_RATIO'),
      "bottom_ratio": config.getfloat('RATIOS', 'BOTTOM_RATIO')
    }

    top_ratios = {
      "name_width": config.getfloat('TOP_RATIOS', 'NAME_WIDTH'),
      "days_width": config.getfloat('TOP_RATIOS', 'DAYS_WIDTH'),
      "position_width": config.getfloat('TOP_RATIOS', 'POSITION_WIDTH'),
      "week_width": config.getfloat('TOP_RATIOS', 'WEEK_WIDTH')
    }

    middle_ratios = {
      "index_width": config.getfloat('MIDDLE_RATIOS', 'INDEX_WIDTH'),
      "day_width": config.getfloat('MIDDLE_RATIOS', 'DAY_WIDTH'),
      "filename_width": config.getfloat('MIDDLE_RATIOS', 'FILENAME_WIDTH'),
      "note_width": config.getfloat('MIDDLE_RATIOS', 'NOTE_WIDTH')
    }

    bottom_ratios = {
      "img_width": config.getfloat('BOTTOM_RATIOS', 'IMG_WIDTH'),
      "img_height": config.getfloat('BOTTOM_RATIOS', 'IMG_HEIGHT')
    }

    
    # 로깅 모듈 세팅
    logger = setup_logger(paths["log_path"])
    logger.info("PDF 생성 스크립트 실행 시작")
    print("PDF 생성 스크립트 실행 시작")
    
    if not Path(paths["csv_path"]).exists():
      raise FileNotFoundError(f"CSV 파일이 존재하지 않습니다: {paths['csv_path']}")

    df = pd.read_csv(paths["csv_path"], parse_dates=["할당일"])
    logger.info(f"CSV 파일 로드 완료: {paths['csv_path']}")
    print(f"CSV 파일 로드 완료: {paths['csv_path']}")

    if "주차" not in df.columns:
        raise KeyError("CSV 파일에 '주차' 열이 존재하지 않습니다.")

    min_week = df["주차"].min()
    max_week = df["주차"].max()
    if start_week < min_week or target_week > max_week:
        error_msg = (
            f"요청한 주차 범위({start_week} ~ {target_week})가 데이터에 존재하는 주차 범위({min_week} ~ {max_week})를 벗어났습니다."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    pdfmetrics.registerFont(TTFont("NanumGothic", paths["font_path"]))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Korean", fontName="NanumGothic", fontSize=10, leading=12))
    list_cell_style = ParagraphStyle(name="TableCell", fontName="NanumGothic", fontSize=8, leading=10, wordWrap='CJK')
    
    logger.info(f"인자 로드 완료")


    layout = calculate_layout(ratios, page_size, logger)
    logger.debug(f"레이아웃 설정 완료")
    if topcut_mode:
      middle_frame, bottom_frame = setup_page_frames(layout, topcut_mode, frame_boundary)
      logger.debug("프레임 틀 (topcut mode) 생성 완료")
    else:
      top_frame, middle_frame, bottom_frame = setup_page_frames(layout, topcut_mode, frame_boundary)
      logger.debug("프레임 틀 생성 완료")

    if total_document:
      story = []

      if topcut_mode:
        page_template = PageTemplate(
          id='TwoFixedFrames',
          frames=[middle_frame, bottom_frame],
        )
        for week_number in range(start_week, target_week + 1):
          middle_flow = create_middle_contents(df, week_number, max_rows, layout, middle_ratios, styles, list_cell_style)
          logger.debug("중단 프레임 생성 완료")
          bottom_flow = create_bottom_contents(df, week_number, paths, layout, bottom_ratios, styles, video_mode, logger)
          logger.debug("하단 프레임 생성 완료")
          page = [middle_flow, FrameBreak(), bottom_flow]
          story.extend(page)
          logger.debug(f"{week_number}주차 페이지 조립 완료")
          if week_number < target_week:
            story.append(PageBreak())
      else:
        page_template = PageTemplate(
          id='ThreeFixedFrames',
          frames=[top_frame, middle_frame, bottom_frame],
        )
        for week_number in range(start_week, target_week + 1):
          top_flow = create_top_contents(df, week_number, layout, top_ratios, styles, list_cell_style)
          logger.debug("상단 프레임 생성 완료")
          middle_flow = create_middle_contents(df, week_number, max_rows, layout, middle_ratios, styles, list_cell_style)
          logger.debug("중단 프레임 생성 완료")
          bottom_flow = create_bottom_contents(df, week_number, paths, layout, bottom_ratios, styles, video_mode, logger)
          logger.debug("하단 프레임 생성 완료")
          page = [top_flow, FrameBreak(), middle_flow, FrameBreak(), bottom_flow]
          story.extend(page)
          logger.debug(f"{week_number}주차 페이지 조립 완료")
          if week_number < target_week:
            story.append(PageBreak())

      if start_week == target_week:
        total_pdf_path = paths["pdf_path"].format(week_number=week_number)
      else:
        total_pdf_path = paths["pdf_path"].format(week_number=f"{start_week}~{target_week}")
      
      logger.debug(f"문서 경로 지정 완료")

      doc = BaseDocTemplate(
        total_pdf_path,
        pagesize=page_size,
        pageTemplates=[page_template]
      )
      doc.build(story)
      logger.info(f"총 PDF 생성 완료: {total_pdf_path}")
      print(f"총 PDF 생성 완료: {total_pdf_path}")

    else:
      for week_number in range(start_week, target_week + 1):
        if topcut_mode:
          middle_flow = create_middle_contents(df, week_number, max_rows, layout, middle_ratios, styles, list_cell_style)
          bottom_flow = create_bottom_contents(df, week_number, paths, layout, bottom_ratios, styles, video_mode, logger)
          page_template = PageTemplate(
              id=f'TwoFixedFrames_Week_{week_number}',
              frames=[middle_frame, bottom_frame],
          )
          page = [middle_flow, FrameBreak(), bottom_flow]
        else:
          top_flow = create_top_contents(df, week_number, layout, top_ratios, styles, list_cell_style)
          middle_flow = create_middle_contents(df, week_number, max_rows, layout, middle_ratios, styles, list_cell_style)
          bottom_flow = create_bottom_contents(df, week_number, paths, layout, bottom_ratios, styles, video_mode, logger)
          page_template = PageTemplate(
              id=f'ThreeFixedFrames_Week_{week_number}',
              frames=[top_frame, middle_frame, bottom_frame],
          )
          page = [top_flow, FrameBreak(), middle_flow, FrameBreak(), bottom_flow]

        pdf_path = paths["pdf_path"].format(week_number=week_number)
        doc = BaseDocTemplate(
          pdf_path,
          pagesize=page_size,
          pageTemplates=[page_template]
        )
        doc.build(page)
        logger.info(f"PDF 생성 완료: {pdf_path}")
        print(f"PDF 생성 완료: {pdf_path}")
  
  except Exception as e:
    logger.error(f"오류 발생: {str(e)}")
    print(f"[오류] {str(e)}", file=sys.stderr)

if __name__ == "__main__":
  generate_pdf()
