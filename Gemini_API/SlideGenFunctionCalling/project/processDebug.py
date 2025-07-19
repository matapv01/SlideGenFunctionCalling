def process_slides(docx_file, output_folder):
    logger.info(f"Bắt đầu xử lý slides từ {docx_file}")
    chunks = inputProcessor(docx_file)
    slide_list = create_slide_list(chunks)
    logger.debug(f"Danh sách slide ban đầu: {slide_list}")

    slide_function_calling_list = []
    pre_slide_content = ""
    pre_function_call = ""
    api_call_cnt = 0
    i = 0

    driver = initialize_chromedriver()
    if not driver:
        raise Exception("Không thể khởi tạo ChromeDriver")

    with tempfile.TemporaryDirectory() as tmpdir:
        html_folder = os.path.join(tmpdir, "html")
        png_folder = os.path.join(tmpdir, "png")
        debug_folder = os.path.join(tmpdir, "debug")
        os.makedirs(html_folder, exist_ok=True)
        os.makedirs(png_folder, exist_ok=True)
        os.makedirs(debug_folder, exist_ok=True)

        html_files = []
        png_files = []
        max_attempts = 6
        previous_image_path = None

        while i < len(slide_list):
            logger.info("--" * 20)
            logger.info(f"Đang xử lý slide {i+1}")
            slide_content = slide_list[i]
            slide_content = re.sub(r'Your Title Here|Placeholder', '', slide_content, flags=re.IGNORECASE).strip()
            
            attempts = 0
            current_tool_call = None
            text = ""
            text_json = {"remaining_content": "", "split_reason": "", "is_redundant": False, "redundancy_reason": ""}
            isRedudant = False


            # Tạo folder debug cho slide
            slide_debug_folder = os.path.join(debug_folder, f"slide{i+1}")
            llm_debug_folder = os.path.join(slide_debug_folder, "LLM")
            vlm_debug_folder = os.path.join(slide_debug_folder, "VLM")
            os.makedirs(llm_debug_folder, exist_ok=True)
            os.makedirs(vlm_debug_folder, exist_ok=True)

            while attempts < max_attempts:
                attempts += 1
                logger.info(f"Thử gọi LLM lần {attempts} cho slide {i+1}")

                # Tạo folder attempt cho LLM
                llm_attempt_folder = os.path.join(llm_debug_folder, f"attempt{attempts}")
                os.makedirs(llm_attempt_folder, exist_ok=True)

                try:
                    # Gọi LLM để tạo tool call
                    text, current_tool_call, text_json = get_html_slide(pre_slide_content, pre_function_call, slide_content)
                    api_call_cnt += 1
                    
                    if text_json.get("is_redundant"):
                        logger.warning(f"Slide số {i+1} bị xác định là dư thừa. Lý do: {text_json.get('redundancy_reason')}. Bỏ qua slide này.")
                        isRedudant = True
                        break # Bỏ qua phần còn lại của vòng lặp này

                    # Lưu output của LLM vào file txt trong folder debug
                    llm_txt_path = os.path.join(llm_attempt_folder, f"output_slide_{i+1}_attempt_{attempts}.txt")
                    with open(llm_txt_path, "w", encoding="utf-8") as txt_file:
                        txt_file.write(f"Text: {text}\nTool Call: {current_tool_call}\nText JSON: {text_json}")

                    if 'remaining_content' in text_json:
                        remaining_content = text_json['remaining_content']
                        split_reason = text_json.get('split_reason', 'Không có lý do chia tách')
                        if remaining_content and remaining_content != slide_content:
                            logger.info(f"Chèn nội dung còn lại vào slide_list tại vị trí {i+2}: {remaining_content}")
                            slide_list.insert(i + 1, remaining_content)
                        else:
                            logger.warning(f"Bỏ qua remaining_content không hợp lệ: {remaining_content}")

                    # Tạo HTML
                    html_content = get_function_by_name(current_tool_call)
                    if not isinstance(html_content, str):
                        logger.error(f"Nội dung HTML tạo bởi LLM không hợp lệ: {html_content}")
                        html_content = "<html><body><h1>Lỗi</h1><p>Nội dung HTML tạo bởi LLM không hợp lệ</p></body></html>"
                        current_tool_call = {"name": "generate_content_slide", "arguments": {"title": slide_content[:50], "content": slide_content[:200]}}

                    temp_html_path = os.path.join(html_folder, f"slide_{i+1}_attempt_{attempts}.html")
                    llm_html_path = os.path.join(llm_attempt_folder, f"slide_{i+1}_attempt_{attempts}.html")
                    with open(temp_html_path, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    with open(llm_html_path, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    
                    temp_image_path = os.path.join(png_folder, f"slide_{i+1}_attempt_{attempts}.png")
                    llm_image_path = os.path.join(llm_attempt_folder, f"slide_{i+1}_attempt_{attempts}.png")
                    slide_image = capture_slide_image(driver, html_content, temp_image_path)

                    try:
                        if os.path.exists(temp_image_path):
                            shutil.copy2(temp_image_path, llm_image_path)
                        else:
                            logger.warning(f"Không tìm thấy file PNG để sao chép: {temp_image_path}")

                    except FileNotFoundError as e:
                        logger.warning(f"Bỏ qua lỗi sao chép file PNG: {e}")

                    max_vlm_attempts = 6
                    vlm_cnt = 1
                    slide_accepted = False


                    while vlm_cnt < max_vlm_attempts and not slide_accepted:

                        # Tạo folder attempt cho VLM
                        vlm_attempt_folder = os.path.join(vlm_debug_folder, f"attempt{vlm_cnt}")
                        os.makedirs(vlm_attempt_folder, exist_ok=True)

                        # Đánh giá bằng VLM
                        text, new_tool_call, text_json = evaluate_slide_with_vlm(temp_image_path, previous_image_path, current_tool_call)
                        logger.debug(f"Kết quả VLM: {text}, Tool call mới: {new_tool_call}, JSON: {text_json}")
                        api_call_cnt += 1
                        vlm_cnt += 1

                        # Lưu output của VLM vào file txt trong folder debug
                        vlm_txt_path = os.path.join(vlm_attempt_folder, f"vlm_output_slide_{i+1}_attempt_{attempts}_vlm_{vlm_cnt-1}.txt")
                        with open(vlm_txt_path, "w", encoding="utf-8") as txt_file:
                            txt_file.write(f"VLM Text: {text}\nVLM Tool Call: {new_tool_call}\nVLM Text JSON: {text_json}")

                        # Sao chép HTML và PNG vào VLM attempt folder
                        vlm_html_path = os.path.join(vlm_attempt_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.html")
                        vlm_image_path = os.path.join(vlm_attempt_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.png")
                        try:
                            if os.path.exists(temp_html_path):
                                shutil.copy2(temp_html_path, vlm_html_path)
                            else:
                                logger.warning(f"Không tìm thấy file HTML để sao chép: {temp_html_path}")
                        except FileNotFoundError as e:
                            logger.warning(f"Bỏ qua lỗi sao chép file HTML: {e}")
                        try:
                            if os.path.exists(temp_image_path):
                                shutil.copy2(temp_image_path, vlm_image_path)
                            else:
                                logger.warning(f"Không tìm thấy file PNG để sao chép: {temp_image_path}")
                        except FileNotFoundError as e:
                            logger.warning(f"Bỏ qua lỗi sao chép file PNG: {e}")

                            
                        if "<!-- accept -->" in text:
                            final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                            final_png_path = os.path.join(png_folder, f"slide_{i+1}.png")

                            try:
                                os.rename(temp_html_path, final_html_path)
                            except FileNotFoundError as e:
                                logger.warning(f"Bỏ qua lỗi đổi tên file HTML: {e}")
                            try:
                                os.rename(temp_image_path, final_png_path)
                            except FileNotFoundError as e:
                                logger.warning(f"Bỏ qua lỗi đổi tên file PNG: {e}")

                            html_files.append(final_html_path)
                            png_files.append(final_png_path)
                            slide_function_calling_list.append(current_tool_call)
                            pre_slide_content = slide_content
                            pre_function_call = current_tool_call
                            previous_image_path = final_png_path
                            slide_accepted = True
                            logger.info(f"Slide {i+1} được chấp nhận với tool call: {current_tool_call}")

                            break  # Thoát vòng lặp VLM nếu đã chấp nhận

                        elif "<!-- deny -->" in text:
                            logger.info(f"Slide {i+1} bị từ chối: {text}")
                            if new_tool_call:
                                if hasattr(new_tool_call, 'name') and hasattr(new_tool_call, 'args'):
                                    new_tool_call = {"name": new_tool_call.name, "arguments": new_tool_call.args}

                                current_tool_call = new_tool_call

                                # xóa các file tạm nếu không chấp nhận slide
                                os.remove(temp_html_path)
                                os.remove(temp_image_path)

                                # Tạo HTML
                                html_content = get_function_by_name(current_tool_call)
                                if not isinstance(html_content, str):
                                    logger.error(f"Nội dung HTML tạo bởi VLM không hợp lệ: {html_content}")
                                    html_content = "<html><body><h1>Lỗi</h1><p>Nội dung HTML tạo bởi VLM không hợp lệ</p></body></html>"
                                    current_tool_call = {"name": "generate_content_slide", "arguments": {"title": slide_content[:50], "content": slide_content[:200]}}

                                temp_html_path = os.path.join(html_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.html")
                                vlm_html_path = os.path.join(vlm_attempt_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.html")
                                with open(temp_html_path, "w", encoding="utf-8") as file:
                                    file.write(html_content)
                                with open(vlm_html_path, "w", encoding="utf-8") as file:
                                    file.write(html_content)
                                
                                temp_image_path = os.path.join(png_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.png")
                                vlm_image_path = os.path.join(vlm_attempt_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.png")
                                slide_image = capture_slide_image(driver, html_content, temp_image_path)

                                try:
                                    if os.path.exists(temp_image_path):
                                        shutil.copy2(temp_image_path, llm_image_path)
                                    else:
                                        logger.warning(f"Không tìm thấy file PNG để sao chép: {temp_image_path}")

                                except FileNotFoundError as e:
                                    logger.warning(f"Bỏ qua lỗi sao chép file PNG: {e}")

                            # Xử lý remaining_content
                            if 'remaining_content' in text_json:
                                remaining_content = text_json['remaining_content']
                                split_reason = text_json.get('split_reason', 'Không có lý do chia tách')
                                if remaining_content and remaining_content != slide_content:
                                    logger.info(f"Chèn nội dung còn lại vào slide_list tại vị trí {i+2}: {remaining_content}")
                                    slide_list.insert(i + 1, remaining_content)
                                    
                                else:
                                    logger.warning(f"Bỏ qua remaining_content không hợp lệ: {remaining_content}")

                    if not slide_accepted:
                        logger.warning(f"Slide {i+1} với số lần thử tối đa ({max_vlm_attempts})")
                        final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                        final_png_path = os.path.join(png_folder, f"slide_{i+1}.png")
                        try:
                            os.rename(temp_html_path, final_html_path)
                        except FileNotFoundError as e:
                                logger.warning(f"Bỏ qua lỗi đổi tên file HTML: {e}")
                        try:
                            os.rename(temp_image_path, final_png_path)
                        except FileNotFoundError as e:
                            logger.warning(f"Bỏ qua lỗi đổi tên file PNG: {e}")

                        html_files.append(final_html_path)
                        png_files.append(final_png_path)
                        slide_function_calling_list.append(current_tool_call)
                        pre_slide_content = slide_content
                        pre_function_call = current_tool_call
                        previous_image_path = final_png_path
                        logger.info(f"Slide {i+1} đạt tối đa lần đánh giá, lây tool call gần nhất: {current_tool_call}")

                    break # Thoát vòng lặp LLM nếu LLM không lỗi

                except FileNotFoundError as e:
                    logger.warning(f"Bỏ qua lỗi FileNotFoundError: {e}")

                except Exception as e:
                    logger.error(f"Lỗi khi xử lý slide {i+1} với LLM, thử {attempts}: {e}")
                    logger.error(f"tool_call: {current_tool_call}")
                    logger.error(f"text: {text}")
                    logger.error(f"text_json: {text_json}")
                    logger.error(f"Thử slide {i+1} với LLM lần thứ {attempts}/ {max_attempts} thất bại, sẽ thử lại sau 1 giây...")
                    raise # Ném lại lỗi để dừng chương trình
                
                time.sleep(1)  # Chờ 1 giây để tránh quá tải API

            if isRedudant:
                logger.info(f"Slide {i+1} bị xác định là dư thừa, bỏ qua slide này.")
                slide_list.pop(i)
                continue

            if slide_accepted or attempts >= max_attempts:
                i += 1

        logger.info(f"Tổng số lần gọi API: {api_call_cnt}")
        driver.quit()
        logger.info("Đóng ChromeDriver")

        zip_file_path = os.path.join(tmpdir, "slides.zip")
        try:
            with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for html_file in html_files:
                    if html_file and os.path.exists(html_file):
                        zipf.write(html_file, os.path.join("html", os.path.basename(html_file)))
                    else:
                        logger.error(f"File HTML không tồn tại: {html_file}")
                for png_file in png_files:
                    if png_file and os.path.exists(png_file):
                        zipf.write(png_file, os.path.join("png", os.path.basename(png_file)))
                    else:
                        logger.error(f"File PNG không tồn tại: {png_file}")
                # Thêm debug folder vào ZIP
                for root, dirs, files in os.walk(debug_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join("debug", os.path.relpath(file_path, debug_folder))
                        zipf.write(file_path, arcname)
            if not os.path.exists(zip_file_path):
                logger.error(f"ZIP file không được tạo: {zip_file_path}")
                raise FileNotFoundError(f"Không tạo được file ZIP: {zip_file_path}")
        except Exception as e:
            logger.error(f"Lỗi khi tạo ZIP file: {e}")
            raise

        final_zip_path = os.path.join(output_folder, "slides.zip")
        shutil.copy2(zip_file_path, final_zip_path)

    logger.debug(f"Danh sách slide cuối cùng: {slide_list}")
    logger.debug(f"Danh sách tool call cuối cùng: {slide_function_calling_list}")
    return final_zip_path