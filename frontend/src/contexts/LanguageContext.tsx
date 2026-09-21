import React, { createContext, useContext, useState, useCallback } from "react";

export type Language = "vi" | "en";

interface Translations {
  // ─────────── SETTINGS ───────────
  nav_settings: string;
  nav_back: string;
  settings_title: string;
  settings_subtitle: string;
  tab_profile: string;
  tab_account: string;
  tab_appearance: string;
  tab_security: string;
  profile_title: string;
  profile_subtitle: string;
  profile_avatar: string;
  profile_avatar_hint: string;
  profile_fullname: string;
  profile_fullname_placeholder: string;
  profile_bio: string;
  profile_bio_placeholder: string;
  profile_save: string;
  profile_saving: string;
  profile_saved: string;
  account_title: string;
  account_subtitle: string;
  account_username: string;
  account_email: string;
  account_readonly_hint: string;
  appearance_title: string;
  appearance_subtitle: string;
  appearance_theme: string;
  appearance_theme_light: string;
  appearance_theme_dark: string;
  appearance_auto_theme: string;
  appearance_auto_theme_hint: string;
  appearance_dark_from: string;
  appearance_light_from: string;
  appearance_language: string;
  appearance_language_hint: string;
  appearance_notifications: string;
  appearance_notifications_hint: string;
  appearance_save: string;
  appearance_saving: string;
  appearance_unsaved_warning: string;
  security_title: string;
  security_subtitle: string;
  security_current_password: string;
  security_new_password: string;
  security_confirm_password: string;
  security_change: string;
  security_changing: string;
  security_hint_length: string;
  security_hint_match: string;
  toast_profile_success: string;
  toast_profile_error: string;
  toast_settings_success: string;
  toast_settings_error: string;
  toast_password_success: string;
  toast_password_error: string;
  toast_password_mismatch: string;
  toast_password_short: string;
  // ─────────── SIDEBAR / APP LAYOUT ───────────
  sidebar_slidegen: string;
  sidebar_projects: string;
  sidebar_guide: string;
  sidebar_collapse: string;
  sidebar_expand: string;
  sidebar_logout: string;
  nav_login: string;
  // ─────────── HOME ───────────
  home_nav_features: string;
  home_nav_testimonials: string;
  home_nav_partners: string;
  home_sign_in: string;
  home_go_app: string;
  home_get_started: string;
  home_hero_badge: string;
  home_hero_h1: string;
  home_hero_h1_span: string;
  home_hero_sub: string;
  home_start_free: string;
  home_watch_demo: string;
  home_scroll_hint: string;
  home_stat_presentations: string;
  home_stat_satisfaction: string;
  home_stat_templates: string;
  home_stat_ai: string;
  home_features_badge: string;
  home_features_h2: string;
  home_features_h2_span: string;
  home_features_sub: string;
  home_feat_fast_title: string;
  home_feat_fast_desc: string;
  home_feat_design_title: string;
  home_feat_design_desc: string;
  home_feat_save_title: string;
  home_feat_save_desc: string;
  home_feat_multilang_title: string;
  home_feat_multilang_desc: string;
  home_how_badge: string;
  home_how_h2: string;
  home_how_h2_span: string;
  home_step1_title: string;
  home_step1_desc: string;
  home_step2_title: string;
  home_step2_desc: string;
  home_step3_title: string;
  home_step3_desc: string;
  home_testimonial_badge: string;
  home_testimonial_h2: string;
  home_testimonial_h2_span: string;
  home_partners_badge: string;
  home_partners_h2: string;
  home_partners_h2_span: string;
  home_partner_cta: string;
  home_contact: string;
  home_cta_h2: string;
  home_cta_sub: string;
  home_get_started_free: string;
  home_footer_privacy: string;
  home_footer_terms: string;
  home_footer_contact: string;
  home_footer_tagline: string;
  // ─────────── GUIDE ───────────
  guide_title: string;
  guide_contents: string;
  guide_overview_title: string;
  guide_overview_content: string;
  guide_workflows_title: string;
  guide_workflows_content: string;
  guide_structure_title: string;
  guide_structure_content: string;
  guide_editor_title: string;
  guide_editor_content: string;
  guide_shortcuts_title: string;
  guide_shortcuts_content: string;
  guide_faq_title: string;
  guide_faq_content: string;
  // ─────────── LOGIN ───────────
  login_title: string;
  login_subtitle: string;
  login_email: string;
  login_password: string;
  login_placeholder_email: string;
  login_placeholder_password: string;
  login_remember: string;
  login_signing_in: string;
  login_sign_in: string;
  login_no_account: string;
  login_register: string;
  login_toast_success: string;
  login_toast_error: string;

  // ─────────── AUTH ERRORS ───────────
  error_auth_required: string;
  error_token_expired: string;
  error_auth_general: string;
  error_rate_limit_title: string;
  error_rate_limit_desc: string;
  error_docx_too_long_title: string;
  error_generate_title: string;
  error_upload_title: string;
  error_load_title: string;
  error_save_title: string;

  // ─────────── SUBSCRIPTION ───────────
  subscription_title: string;
  subscription_subtitle: string;
  subscription_current_plan: string;
  subscription_active: string;
  subscription_expired: string;
  subscription_expires_at: string;
  subscription_auto_renew: string;
  subscription_ends_on: string;
  subscription_no_expiry: string;
  subscription_idea_generation: string;
  subscription_docx_upload: string;
  subscription_slide_limit: string;
  subscription_today: string;
  subscription_slides: string;
  subscription_redeem_code: string;
  subscription_enter_code: string;
  subscription_code_placeholder: string;
  subscription_use_code: string;
  subscription_processing: string;
  subscription_cancel: string;
  subscription_upgrade: string;
  subscription_current_tier: string;
  subscription_guide_title: string;
  subscription_guide_code_only: string;
  subscription_guide_free_ultra: string;
  subscription_guide_payment_soon: string;
  subscription_unlimited: string;
  subscription_error_load_title: string;
  subscription_error_retry_later: string;
  subscription_error_code_required: string;
  subscription_success_title: string;
  subscription_success_desc: string;
  subscription_error_redeem_title: string;
  subscription_error_invalid_code: string;
  subscription_error_upgrade_title: string;
  subscription_error_upgrade_desc: string;
  subscription_error_load_info: string;
  subscription_retry: string;
  subscription_enter_code_desc: string;
  subscription_code_label: string;
  subscription_content_length: string;
  subscription_priority_support: string;
  subscription_advanced_features: string;
  nav_subscription: string;
  plan_requires_plus: string;
  plan_requires_ultra: string;
  plan_slide_limit_title: string;
  plan_slide_limit_desc: string;
  export_pdf_failed: string;
  export_pdf_error: string;
  export_no_slides: string;
  export_capture_failed: string;
  export_capture_error: string;
  subscription_cancel_renewal: string;
  subscription_cancel_now: string;
  subscription_cancel_renewal_title: string;
  subscription_cancel_renewal_desc: string;
  subscription_cancel_now_title: string;
  subscription_cancel_now_desc: string;
  subscription_cancel_confirm: string;
  subscription_cancelled_now: string;
  subscription_cancelled_renewal: string;
  // ─────────── REGISTER ───────────
  register_title: string;
  register_subtitle: string;
  register_fullname: string;
  register_email: string;
  register_password: string;
  register_confirm_password: string;
  register_error_fullname: string;
  register_error_password: string;
  register_error_confirm: string;
  register_creating: string;
  register_create: string;
  register_has_account: string;
  register_sign_in: string;
  register_toast_success: string;
  register_toast_error: string;
  // ─────────── PROJECTS ───────────
  projects_title: string;
  projects_search: string;
  projects_select_mode: string;
  projects_deselect_all: string;
  projects_select_all: string;
  projects_cancel: string;
  projects_no_found: string;
  projects_no_found_hint: string;
  projects_go_home: string;
  projects_edit: string;
  projects_view: string;
  projects_rename: string;
  projects_delete: string;
  projects_slides: string;
  projects_delete_title: string;
  projects_delete_desc: string;
  projects_rename_title: string;
  projects_rename_desc: string;
  projects_name_placeholder: string;
  projects_save: string;
  projects_delete_all: string;
  projects_toast_load_fail: string;
  projects_toast_deleted: string;
  projects_toast_delete_fail: string;
  projects_toast_renamed: string;
  projects_toast_rename_fail: string;
  // ─────────── SLIDEGEN ───────────
  slidegen_badge: string;
  slidegen_h1: string;
  slidegen_h1_span: string;
  slidegen_sub: string;
  slidegen_upload_title: string;
  slidegen_upload_desc: string;
  slidegen_uploading: string;
  slidegen_choose_file: string;
  slidegen_idea_title: string;

  slidegen_idea_desc: string;
  slidegen_idea_title_ph: string;
  slidegen_idea_desc_ph: string;
  slidegen_generate: string;
  slidegen_options: string;
  slidegen_workflow: string;
  slidegen_workflow_auto_heading: string;
  slidegen_workflow_auto_heading_desc: string;
  slidegen_workflow_auto_no_heading: string;
  slidegen_workflow_auto_no_heading_desc: string;
  slidegen_workflow_manual: string;
  streaming_msg_analyzing: string;
  streaming_msg_processing_struct: string;
  streaming_msg_generating_struct: string;
  streaming_msg_booting: string;
  streaming_msg_initializing_infra: string;
  streaming_msg_generating_slides: string;
  streaming_msg_starting_generation: string;
  streaming_msg_no_slides: string;
  streaming_msg_ready: string;
  slidegen_workflow_manual_desc: string;
  slidegen_transitions: string;
  slidegen_thankyou: string;
  slidegen_length_label: string;
  slidegen_length_brief: string;
  slidegen_length_standard: string;
  slidegen_length_detailed: string;
  slidegen_length_extensive: string;
  slidegen_toast_success: string;
  slidegen_toast_opening_structure: string;
  slidegen_toast_starting: string;
  slidegen_toast_upload_fail: string;
  slidegen_toast_no_title: string;

  // ─────────── STREAMING ───────────
  streaming_title: string;
  streaming_completed: string;
  streaming_preparing: string;
  streaming_creating: string;
  streaming_stage_analyze: string;
  streaming_stage_prepare: string;
  streaming_stage_design: string;
  streaming_stage_completed_label: string;
  streaming_stage_processing: string;
  streaming_stage_pending: string;
  streaming_done: string;
  streaming_slides_created: string;
  streaming_slides_unit: string;
  streaming_retry: string;
  streaming_slides_header: string;
  streaming_slide_n: string;
  streaming_slide_completed: string;
  streaming_go_editor: string;
  streaming_present: string;
  streaming_back: string;
  streaming_no_content: string;
  streaming_initializing: string;
  streaming_connecting: string;
  streaming_preparing_activity: string;
  streaming_toast_ready: string;
  streaming_toast_starting: string;
  streaming_toast_failed: string;
  // ─────────── STRUCTURE EDITOR ───────────
  structure_title: string;
  structure_intro_slide: string;
  structure_add_section: string;
  structure_intro_label: string;
  structure_title_ph: string;
  structure_section_title_ph: string;
  structure_content_ph: string;
  structure_transition: string;
  structure_level: string;
  structure_approve: string;
  structure_processing: string;
  structure_preview: string;
  structure_source_text: string;
  structure_structure: string;
  structure_sections: string;
  structure_toast_no_session: string;
  structure_toast_no_session_desc: string;
  structure_toast_load_fail: string;
  structure_toast_approved: string;
  structure_toast_slides_prepared: string;
  structure_toast_approval_fail: string;
  structure_toast_fail_approve: string;
  // ─────────── VIEW PROJECT ───────────
  view_present: string;
  view_slide_n: string;
  view_edit: string;
  view_no_content: string;
  view_edit_slide_title: string;
  view_edit_slide_desc: string;
  view_cancel: string;
  view_save: string;
  view_delete_slide_title: string;
  view_delete_slide_desc: string;
  view_delete: string;
  view_toast_load_fail: string;
  view_toast_updated: string;
  view_toast_save_fail: string;
  view_toast_deleted: string;
  view_toast_delete_fail: string;
  // ─────────── NOT FOUND ───────────
  notfound_title: string;
  notfound_message: string;
  notfound_link: string;
  // ─────────── EXPORT MODAL ───────────
  export_title: string;
  export_subtitle: string;
  export_pdf_title: string;
  export_pdf_desc: string;
  export_images_title: string;
  export_images_desc: string;
  export_cancel: string;
  export_success_title: string;
  export_download: string;
  export_close: string;
  export_processing_title: string;
  export_processing_sub: string;
  export_error_title: string;
  export_retry: string;
  // ─────────── TOOLBAR ───────────
  toolbar_back: string;
  toolbar_back_desc: string;
  toolbar_select: string;
  toolbar_select_button: string;
  toolbar_select_desc: string;
  toolbar_add_text: string;
  toolbar_add_text_button: string;
  toolbar_add_text_desc: string;
  toolbar_export: string;
  toolbar_export_button: string;
  toolbar_export_desc: string;
  toolbar_present: string;
  toolbar_present_button: string;
  toolbar_present_desc: string;
  toolbar_present_from_start: string;
  toolbar_present_from_current: string;
  toolbar_undo: string;
  toolbar_undo_desc: string;
  toolbar_redo: string;
  toolbar_redo_desc: string;
  // ─────────── SLIDEGEN (additional) ───────────
  slidegen_read_guide: string;
  // ─────────── SLIDE EDITOR ───────────
  editor_loading: string;
  editor_loading_slide: string;
  editor_slide_n: string;
  editor_new_slide: string;
  editor_tab_slides: string;
  editor_tab_templates: string;
  editor_tab_elements: string;
  editor_template_hint: string;
  editor_no_element: string;
  editor_no_element_desc: string;
  editor_section_transform: string;
  editor_section_typography: string;
  editor_section_appearance: string;
  editor_section_effects: string;
  editor_section_layer: string;
  editor_padding: string;
  editor_send_backward: string;
  editor_send_backward_desc: string;
  editor_bring_forward: string;
  editor_bring_forward_desc: string;
  editor_duplicate: string;
  editor_duplicate_desc: string;
  editor_delete: string;
  editor_delete_desc: string;
  editor_align_left: string;
  editor_align_left_desc: string;
  editor_align_center: string;
  editor_align_center_desc: string;
  editor_align_right: string;
  editor_align_right_desc: string;
  editor_align_justify: string;
  editor_align_justify_desc: string;
  editor_fmt_bold: string;
  editor_fmt_bold_desc: string;
  editor_fmt_italic: string;
  editor_fmt_italic_desc: string;
  editor_fmt_underline: string;
  editor_fmt_underline_desc: string;
  editor_fmt_strikethrough: string;
  editor_fmt_strikethrough_desc: string;
  editor_fmt_clear: string;
  editor_fmt_clear_desc: string;
  editor_no_fill: string;
  editor_no_fill_desc: string;
  editor_type_text: string;
  editor_type_image: string;
  editor_type_shape: string;
  editor_type_video: string;
  editor_tmpl_blank: string;
  editor_tmpl_title: string;
  editor_tmpl_content: string;
  editor_tmpl_two_col: string;
  editor_tmpl_img_text: string;
  editor_tmpl_bullets: string;
  editor_cat_text: string;
  editor_cat_shapes: string;
  editor_cat_media: string;
  editor_el_title: string;
  editor_el_subtitle: string;
  editor_el_body: string;
  editor_el_label: string;
  editor_el_rect: string;
  editor_el_circle: string;
  editor_el_triangle: string;
  editor_el_star: string;
  editor_el_diamond: string;
  editor_el_line: string;
  editor_el_image: string;
  editor_el_video: string;
  // ─── properties panel ───
  editor_prop_x: string;
  editor_prop_y: string;
  editor_prop_width: string;
  editor_prop_height: string;
  editor_prop_rotation: string;
  editor_prop_font_size: string;
  editor_prop_line_height: string;
  editor_prop_letter_spacing: string;
  editor_prop_text_color: string;
  editor_prop_border_width: string;
  editor_prop_border_color: string;
  editor_prop_border_radius: string;
  editor_prop_border_radius_desc: string;
  editor_prop_box_shadow: string;
  editor_prop_opacity: string;
  editor_prop_opacity_desc: string;
  editor_prop_blur: string;
  editor_prop_blur_desc: string;
  editor_prop_brightness: string;
  editor_prop_brightness_desc: string;
  editor_prop_saturation: string;
  editor_prop_saturation_desc: string;
  // ─── presentation mode ───
  present_slide: string;
  present_no_content: string;
  register_placeholder_fullname: string;
  structure_untitled: string;
  structure_intro_fallback: string;
  structure_transition_label: string;
  streaming_err_no_file: string;
  streaming_err_generic: string;
  editor_reset_zoom: string;
  editor_add_slide_prefix: string;
  editor_add_el_prefix: string;
}

const vi: Translations = {
  // ─────────── SETTINGS ───────────
  nav_settings: "Cài đặt",
  nav_back: "Quay lại",
  settings_title: "Cài đặt của bạn",
  settings_subtitle: "Quản lý thông tin cá nhân và tuỳ chỉnh trải nghiệm của bạn",
  tab_profile: "Hồ sơ",
  tab_account: "Tài khoản",
  tab_appearance: "Giao diện",
  tab_security: "Bảo mật",
  profile_title: "Thông tin hồ sơ",
  profile_subtitle: "Cập nhật họ tên, ảnh đại diện và giới thiệu bản thân",
  profile_avatar: "Ảnh đại diện (URL)",
  profile_avatar_hint: "Đường dẫn tới ảnh đại diện của bạn",
  profile_fullname: "Họ và tên",
  profile_fullname_placeholder: "Nhập họ tên đầy đủ của bạn",
  profile_bio: "Giới thiệu",
  profile_bio_placeholder: "Viết vài dòng giới thiệu về bản thân...",
  profile_save: "Lưu thay đổi",
  profile_saving: "Đang lưu...",
  profile_saved: "Đã lưu",
  account_title: "Thông tin tài khoản",
  account_subtitle: "Tên đăng nhập và email không thể thay đổi",
  account_username: "Tên đăng nhập",
  account_email: "Email",
  account_readonly_hint: "Các thông tin này chỉ đọc và không thể chỉnh sửa",
  appearance_title: "Giao diện & Ngôn ngữ",
  appearance_subtitle: "Tuỳ chỉnh màu sắc, ngôn ngữ hiển thị và thông báo",
  appearance_theme: "Giao diện màu",
  appearance_theme_light: "Sáng",
  appearance_theme_dark: "Tối",
  appearance_auto_theme: "Tự động đổi theo giờ",
  appearance_auto_theme_hint: "Tự động chuyển giao diện theo khung giờ bạn cài",
  appearance_dark_from: "Bật tối từ",
  appearance_light_from: "Bật sáng từ",
  appearance_language: "Ngôn ngữ",
  appearance_language_hint: "Chọn ngôn ngữ hiển thị cho toàn bộ ứng dụng",
  appearance_notifications: "Thông báo",
  appearance_notifications_hint: "Nhận thông báo khi có cập nhật hoặc sự kiện mới",
  appearance_save: "Lưu cài đặt",
  appearance_saving: "Đang lưu...",
  appearance_unsaved_warning: "Bạn có thay đổi chưa được lưu. Nếu rời trang bây giờ, các thay đổi sẽ bị mất.",
  security_title: "Đổi mật khẩu",
  security_subtitle: "Bảo vệ tài khoản bằng mật khẩu mạnh",
  security_current_password: "Mật khẩu hiện tại",
  security_new_password: "Mật khẩu mới",
  security_confirm_password: "Xác nhận mật khẩu mới",
  security_change: "Đổi mật khẩu",
  security_changing: "Đang xử lý...",
  security_hint_length: "Tối thiểu 6 ký tự",
  security_hint_match: "Mật khẩu mới không khớp",
  toast_profile_success: "Đã cập nhật hồ sơ thành công",
  toast_profile_error: "Cập nhật hồ sơ thất bại",
  toast_settings_success: "Đã lưu cài đặt thành công",
  toast_settings_error: "Lưu cài đặt thất bại",
  toast_password_success: "Đổi mật khẩu thành công",
  toast_password_error: "Đổi mật khẩu thất bại",
  toast_password_mismatch: "Mật khẩu xác nhận không khớp",
  toast_password_short: "Mật khẩu mới phải có ít nhất 6 ký tự",
  // ─────────── SIDEBAR / APP LAYOUT ───────────
  sidebar_slidegen: "SlideGen",
  sidebar_projects: "Dự án",
  sidebar_guide: "Hướng dẫn",
  sidebar_collapse: "Thu gọn",
  sidebar_expand: "Mở rộng thanh bên",
  sidebar_logout: "Đăng xuất",
  nav_login: "Đăng nhập",
  // ─────────── HOME ───────────
  home_nav_features: "Tính năng",
  home_nav_testimonials: "Đánh giá",
  home_nav_partners: "Đối tác",
  home_sign_in: "Đăng nhập",
  home_go_app: "Vào ứng dụng",
  home_get_started: "Bắt đầu",
  home_hero_badge: "Tạo Slide Bằng AI",
  home_hero_h1: "Tạo Slide Ấn Tượng",
  home_hero_h1_span: "Trong Vài Giây",
  home_hero_sub: "Tải lên tài liệu, mô tả ý tưởng hoặc nhập dự án có sẵn. SlideGen biến nội dung của bạn thành bài thuyết trình đẹp mắt với AI.",
  home_start_free: "Bắt đầu miễn phí",
  home_watch_demo: "Xem Demo",
  home_scroll_hint: "Khám phá thêm",
  home_stat_presentations: "Bài thuyết trình đã tạo",
  home_stat_satisfaction: "Tỷ lệ hài lòng",
  home_stat_templates: "Mẫu thiết kế",
  home_stat_ai: "Độ sẵn sàng AI",
  home_features_badge: "Tính năng",
  home_features_h2: "Mọi thứ bạn cần để",
  home_features_h2_span: "Tạo Slide Hoàn Hảo",
  home_features_sub: "Sức mạnh AI kết hợp với công cụ thiết kế trực quan giúp SlideGen trở thành trợ lý thuyết trình tối ưu.",
  home_feat_fast_title: "Siêu Nhanh",
  home_feat_fast_desc: "Tạo slide chuyên nghiệp trong vài giây với công cụ AI mạnh mẽ",
  home_feat_design_title: "Thiết Kế Đẹp",
  home_feat_design_desc: "Mẫu và chủ đề tuyệt đẹp được thiết kế bởi các chuyên gia",
  home_feat_save_title: "Tiết Kiệm Thời Gian",
  home_feat_save_desc: "Công việc từng mất nhiều giờ nay chỉ cần vài phút. Tập trung vào điều quan trọng",
  home_feat_multilang_title: "Đa Ngôn Ngữ",
  home_feat_multilang_desc: "Tạo thuyết trình bằng bất kỳ ngôn ngữ nào với xử lý văn bản thông minh",
  home_how_badge: "Cách hoạt động",
  home_how_h2: "Ba bước đơn giản để",
  home_how_h2_span: "Thuyết Trình Ấn Tượng",
  home_step1_title: "Tải lên hoặc Mô tả",
  home_step1_desc: "Tải lên file Word, mô tả ý tưởng hoặc nhập dự án của bạn",
  home_step2_title: "AI Xử Lý",
  home_step2_desc: "AI phân tích nội dung và tạo bố cục slide chuyên nghiệp",
  home_step3_title: "Xuất & Trình Chiếu",
  home_step3_desc: "Tải về PDF, hình ảnh hoặc trình chiếu trực tiếp",
  home_testimonial_badge: "Nhận xét",
  home_testimonial_h2: "Được yêu thích bởi",
  home_testimonial_h2_span: "Hàng Nghìn Người",
  home_partners_badge: "Đối tác & Nhà tài trợ",
  home_partners_h2: "Được tin dùng bởi",
  home_partners_h2_span: "Các Doanh Nghiệp Hàng Đầu",
  home_partner_cta: "Muốn trở thành đối tác?",
  home_contact: "Liên hệ chúng tôi",
  home_cta_h2: "Sẵn sàng tạo thuyết trình ấn tượng?",
  home_cta_sub: "Tham gia hàng nghìn người dùng đang tạo slide tuyệt đẹp với SlideGen. Bắt đầu miễn phí ngay hôm nay!",
  home_get_started_free: "Bắt đầu miễn phí",
  home_footer_privacy: "Chính sách bảo mật",
  home_footer_terms: "Điều khoản",
  home_footer_contact: "Liên hệ",
  home_footer_tagline: "Được tạo với ❤️ bởi đội ngũ SlideGen",
  // ─────────── GUIDE ───────────
  guide_title: "Hướng dẫn SlideGen",
  guide_contents: "Mục lục",
  guide_overview_title: "Tổng quan hệ thống",
  guide_overview_content: "SlideGen là nền tảng tạo slide bằng AI. Tải lên tài liệu, mô tả ý tưởng, hoặc nhập dự án có sẵn — để AI biến nội dung của bạn thành bài thuyết trình đẹp mắt.\n\nNền tảng hỗ trợ nhiều chế độ workflow, tạo slide streaming thời gian thực, trình soạn thảo WYSIWYG đầy đủ, và chế độ trình chiếu.",
  guide_workflows_title: "Các chế độ Workflow",
  guide_workflows_content: "**Tự động có Heading**: Tự động phát hiện heading trong tài liệu và dùng làm điểm phân chia slide. Phù hợp nhất cho tài liệu có cấu trúc rõ ràng.\n\n**Tự động không Heading**: AI phân tích nội dung và xác định cấu trúc slide tối ưu. Thích hợp cho văn bản không có cấu trúc.\n\n**Cấu trúc thủ công**: Xem lại và chỉnh sửa cấu trúc tài liệu trước khi tạo. Kiểm soát hoàn toàn nội dung từng slide.",
  guide_structure_title: "Trình soạn thảo cấu trúc",
  guide_structure_content: "Trình soạn thảo cấu trúc cho phép bạn sắp xếp nội dung trước khi tạo slide:\n\n• Áp dụng cấp độ phân cấp (0-7) để kiểm soát lồng nhau\n• Đặt loại nội dung: Tiêu đề (xanh dương), Nội dung (xanh lá), Gạch đầu dòng (cam)\n• Kéo thả và sắp xếp lại các khối văn bản\n• Thêm slide dẫn nhập và chuyển tiếp\n• Xem trước cấu trúc theo thời gian thực\n• Phê duyệt khi sẵn sàng tạo",
  guide_editor_title: "Trình soạn thảo Slide",
  guide_editor_content: "Trình soạn thảo WYSIWYG cung cấp toàn quyền kiểm soát hình ảnh:\n\n• Kéo, thay đổi kích thước và xoay các phần tử trên canvas\n• Thêm văn bản, hình ảnh, hình dạng, icon và đầu nối\n• Căn chỉnh theo lưới và hướng dẫn căn chỉnh\n• Điều khiển zoom và cuộn\n• Bảng thuộc tính để định vị chính xác\n• Bảng Slide để quản lý thứ tự slide",
  guide_shortcuts_title: "Phím tắt",
  guide_shortcuts_content: "**Trình soạn thảo:**\n• Ctrl+Z — Hoàn tác\n• Ctrl+Y — Làm lại\n• Delete — Xóa phần tử đã chọn\n\n**Trình chiếu:**\n• → / Space — Slide tiếp theo\n• ← — Slide trước\n• Escape — Thoát trình chiếu\n• Click trái — Slide trước\n• Click phải — Slide tiếp theo",
  guide_faq_title: "Câu hỏi thường gặp",
  guide_faq_content: "**H: Các định dạng file nào được hỗ trợ?**\nT: DOCX để tải lên tài liệu. Xuất sang PDF và hình ảnh.\n\n**H: Tôi có thể chỉnh sửa slide sau khi tạo không?**\nT: Có! Trình soạn thảo WYSIWYG cho phép kiểm soát toàn bộ từng phần tử.\n\n**H: Dữ liệu có được lưu tự động không?**\nT: Có, trình soạn thảo tự động lưu thay đổi sau mỗi vài giây.\n\n**H: AI tạo slide hoạt động như thế nào?**\nT: Chúng tôi sử dụng các mô hình AI tiên tiến để phân tích nội dung, cấu trúc thành slide và tạo thiết kế chuyên nghiệp.",
  // ─────────── LOGIN ───────────
  login_title: "Chào mừng trở lại",
  login_subtitle: "Đăng nhập vào tài khoản SlideGen của bạn",
  login_email: "Email",
  login_password: "Mật khẩu",
  login_placeholder_email: "you@example.com",
  login_placeholder_password: "••••••",
  login_remember: "Ghi nhớ đăng nhập",
  login_signing_in: "Đang đăng nhập...",
  login_sign_in: "Đăng nhập",
  login_no_account: "Chưa có tài khoản?",
  login_register: "Đăng ký",
  login_toast_success: "Chào mừng trở lại!",
  login_toast_error: "Đăng nhập thất bại",

  // ─────────── AUTH ERRORS ───────────
  error_auth_required: "Vui lòng đăng nhập để sử dụng tính năng này",
  error_token_expired: "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
  error_auth_general: "Vui lòng đăng nhập để sử dụng tính năng này",
  error_rate_limit_title: "Đã đạt giới hạn sử dụng",
  error_rate_limit_desc: "Bạn đã dùng hết lượt tạo trong ngày. Nâng cấp gói để tiếp tục.",
  error_docx_too_long_title: "Tài liệu quá dài",
  error_generate_title: "Lỗi tạo nội dung",
  error_upload_title: "Lỗi upload",
  error_load_title: "Lỗi tải dữ liệu",
  error_save_title: "Lỗi lưu",

  // ─────────── SUBSCRIPTION ───────────
  subscription_title: "Quản lý Subscription",
  subscription_subtitle: "Xem thông tin gói và nâng cấp tài khoản của bạn",
  subscription_current_plan: "Gói hiện tại",
  subscription_active: "Đang hoạt động",
  subscription_expired: "Đã hết hạn",
  subscription_expires_at: "Hết hạn",
  subscription_auto_renew: "Tự động gia hạn từ ngày",
  subscription_ends_on: "Gói sẽ kết thúc ngày",
  subscription_no_expiry: "Không giới hạn thời gian",
  subscription_idea_generation: "Tạo từ ý tưởng",
  subscription_docx_upload: "File upload",
  subscription_slide_limit: "Giới hạn slides",
  subscription_today: "hôm nay",
  subscription_slides: "slides",
  subscription_redeem_code: "Nhập code nâng cấp",
  subscription_enter_code: "Nhập code nâng cấp",
  subscription_code_placeholder: "Nhập code tại đây...",
  subscription_use_code: "Sử dụng code",
  subscription_processing: "Đang xử lý...",
  subscription_cancel: "Hủy",
  subscription_upgrade: "Nâng cấp",
  subscription_current_tier: "Gói hiện tại",
  subscription_guide_title: "Hướng dẫn nâng cấp",
  subscription_guide_code_only: "Hiện tại hệ thống chỉ hỗ trợ nâng cấp bằng code.",
  subscription_guide_free_ultra: "Để nhận code Ultra miễn phí, sử dụng: SLIDEGENIUS",
  subscription_guide_payment_soon: "Tính năng thanh toán online sẽ sớm được cập nhật.",
  subscription_unlimited: "Không giới hạn",
  subscription_error_load_title: "Lỗi tải subscription",
  subscription_error_retry_later: "Vui lòng thử lại sau",
  subscription_error_code_required: "Vui lòng nhập code",
  subscription_success_title: "Thành công!",
  subscription_success_desc: "Gói của bạn đã được nâng cấp thành công.",
  subscription_error_redeem_title: "Không thể sử dụng code",
  subscription_error_invalid_code: "Code không hợp lệ hoặc đã được sử dụng",
  subscription_error_upgrade_title: "Tính năng chưa khả dụng",
  subscription_error_upgrade_desc: "Hiện tại chỉ hỗ trợ nâng cấp bằng code. Vui lòng liên hệ support để nhận code.",
  subscription_error_load_info: "Không thể tải thông tin subscription",
  subscription_retry: "Thử lại",
  subscription_enter_code_desc: "Nhập code để nâng cấp lên gói cao hơn",
  subscription_code_label: "Code nâng cấp",
  subscription_content_length: "Độ dài nội dung",
  subscription_priority_support: "Hỗ trợ ưu tiên",
  subscription_advanced_features: "Tính năng nâng cao",
  nav_subscription: "Subscription",
  plan_requires_plus: "Yêu cầu gói Plus trở lên",
  plan_requires_ultra: "Yêu cầu gói Ultra",
  plan_slide_limit_title: "Đã đạt giới hạn slides",
  plan_slide_limit_desc: "Nâng cấp lên Plus hoặc Ultra để thêm nhiều slides hơn",
  export_pdf_failed: "Xuất PDF thất bại",
  export_pdf_error: "Lỗi khi xuất PDF",
  export_no_slides: "Không có slide để chụp",
  export_capture_failed: "Chụp ảnh thất bại",
  export_capture_error: "Lỗi khi chụp ảnh",
  subscription_cancel_renewal: "Hủy gia hạn",
  subscription_cancel_now: "Hủy ngay",
  subscription_cancel_renewal_title: "Hủy gia hạn?",
  subscription_cancel_renewal_desc: "Gói của bạn sẽ tiếp tục hoạt động đến hết kỳ hiện tại, sau đó tự động chuyển về gói Free.",
  subscription_cancel_now_title: "Hủy ngay?",
  subscription_cancel_now_desc: "Gói của bạn sẽ bị hủy ngay lập tức và chuyển về gói Free. Hành động này không thể hoàn tác.",
  subscription_cancel_confirm: "Xác nhận hủy",
  subscription_cancelled_now: "Đã hủy gói thành công. Tài khoản đã chuyển về gói Free.",
  subscription_cancelled_renewal: "Gói của bạn sẽ hết hạn vào cuối kỳ và không được gia hạn tự động.",
  // ─────────── REGISTER ───────────
  register_title: "Tạo tài khoản",
  register_subtitle: "Tham gia SlideGen và bắt đầu tạo slide",
  register_fullname: "Họ và tên",
  register_email: "Email",
  register_password: "Mật khẩu",
  register_confirm_password: "Xác nhận mật khẩu",
  register_error_fullname: "Tối thiểu 3 ký tự",
  register_error_password: "Tối thiểu 6 ký tự",
  register_error_confirm: "Mật khẩu không khớp",
  register_creating: "Đang tạo...",
  register_create: "Tạo tài khoản",
  register_has_account: "Đã có tài khoản?",
  register_sign_in: "Đăng nhập",
  register_toast_success: "Tài khoản đã được tạo!",
  register_toast_error: "Đăng ký thất bại",
  // ─────────── PROJECTS ───────────
  projects_title: "Dự án",
  projects_search: "Tìm kiếm dự án...",
  projects_select_mode: "Chế độ chọn",
  projects_deselect_all: "Bỏ chọn tất cả",
  projects_select_all: "Chọn tất cả",
  projects_cancel: "Hủy",
  projects_no_found: "Không tìm thấy dự án",
  projects_no_found_hint: "Tạo dự án mới từ trang SlideGen",
  projects_go_home: "Về trang chủ",
  projects_edit: "Chỉnh sửa",
  projects_view: "Xem",
  projects_rename: "Đổi tên",
  projects_delete: "Xóa",
  projects_slides: "slide",
  projects_delete_title: "Xóa dự án",
  projects_delete_desc: "Hành động này không thể hoàn tác. Bạn có chắc không?",
  projects_rename_title: "Đổi tên dự án",
  projects_rename_desc: "Nhập tên mới cho dự án của bạn",
  projects_name_placeholder: "Tên dự án",
  projects_save: "Lưu",
  projects_delete_all: "Xóa tất cả",
  projects_toast_load_fail: "Không thể tải danh sách dự án",
  projects_toast_deleted: "Đã xóa dự án",
  projects_toast_delete_fail: "Xóa thất bại",
  projects_toast_renamed: "Đã đổi tên dự án",
  projects_toast_rename_fail: "Đổi tên thất bại",
  // ─────────── SLIDEGEN ───────────
  slidegen_badge: "Tạo Slide Bằng AI",
  slidegen_h1: "Tạo Slide Ấn Tượng",
  slidegen_h1_span: "Trong Vài Giây",
  slidegen_sub: "Tải lên tài liệu, mô tả ý tưởng hoặc nhập dự án có sẵn. SlideGen biến nội dung của bạn thành bài thuyết trình đẹp mắt với AI.",
  slidegen_upload_title: "Tạo từ tài liệu",
  slidegen_upload_desc: "Tải tài liệu và để AI tự động tạo slide chuyên nghiệp",
  slidegen_uploading: "Đang tải lên...",
  slidegen_choose_file: "Tải lên file",

  slidegen_idea_title: "Tạo từ ý tưởng",

  slidegen_idea_desc: "Mô tả bài thuyết trình và để AI xây dựng cho bạn",
  slidegen_idea_title_ph: "Tiêu đề bài thuyết trình",
  slidegen_idea_desc_ph: "Mô tả bài thuyết trình của bạn...",
  slidegen_generate: "Tạo ngay",
  slidegen_options: "Tùy chọn tạo slide",
  slidegen_workflow: "Chế độ xử lý",
  slidegen_workflow_auto_heading: "Tự động với tiêu đề",
  slidegen_workflow_auto_heading_desc: "Tự động phát hiện tiêu đề để phân chia slide",
  slidegen_workflow_auto_no_heading: "Tự động không tiêu đề",
  slidegen_workflow_auto_no_heading_desc: "AI xác định cấu trúc slide tối ưu",
  slidegen_workflow_manual: "Cấu trúc thủ công",
  slidegen_workflow_manual_desc: "Chỉnh sửa cấu trúc tài liệu trước khi tạo",
  slidegen_transitions: "Bật slide chuyển tiếp",
  slidegen_thankyou: "Bật slide cảm ơn",
  slidegen_length_label: "Số lượng slide",
  slidegen_length_brief: "Ngắn gọn",
  slidegen_length_standard: "Chuẩn",
  slidegen_length_detailed: "Chi tiết",
  slidegen_length_extensive: "Mở rộng",
  slidegen_toast_success: "Tải lên thành công",
  slidegen_toast_opening_structure: "Đang mở trình chỉnh sửa cấu trúc...",
  slidegen_toast_starting: "Bắt đầu tạo slide...",
  slidegen_toast_upload_fail: "Tải lên thất bại",
  slidegen_toast_no_title: "Vui lòng nhập tiêu đề",

  // ─────────── STREAMING ───────────
  streaming_title: "SlideGen AI",
  streaming_completed: "🎉 Hoàn thành!",
  streaming_preparing: "💡 Đang chuẩn bị ý tưởng...",
  streaming_creating: "Đang tạo bài thuyết trình...",
  streaming_stage_analyze: "Phân tích nội dung",
  streaming_stage_prepare: "Chuẩn bị nội dung",
  streaming_stage_design: "Thiết kế slide",
  streaming_stage_completed_label: "Hoàn thành",
  streaming_stage_processing: "Đang xử lý...",
  streaming_stage_pending: "Đang chờ",
  streaming_done: "Hoàn thành!",
  streaming_slides_created: "Đã tạo thành công",
  streaming_slides_unit: "slide",
  streaming_retry: "Thử lại",
  streaming_slides_header: "Slide",
  streaming_slide_n: "Slide",
  streaming_slide_completed: "Hoàn thành",
  streaming_go_editor: "Mở trình chỉnh sửa",
  streaming_present: "Trình chiếu",
  streaming_back: "Quay về SlideGen",
  streaming_no_content: "Không có nội dung",
  streaming_initializing: "Đang khởi tạo...",
  streaming_connecting: "Đang kết nối...",
  streaming_preparing_activity: "Đang chuẩn bị ý tưởng...",
  streaming_toast_ready: "Cấu trúc sẵn sàng",
  streaming_toast_starting: "Bắt đầu tạo slide...",
  streaming_toast_failed: "Chuẩn bị thất bại",
  streaming_msg_analyzing: "Đang phân tích nội dung để thiết kế slide...",
  streaming_msg_processing_struct: "Đang xử lý cấu trúc tài liệu...",
  streaming_msg_generating_struct: "Đang tạo cấu trúc tài liệu từ nội dung...",
  streaming_msg_booting: "Khởi tạo hệ thống...",
  streaming_msg_initializing_infra: "Đang khởi tạo hạ tầng...",
  streaming_msg_generating_slides: "Đang tạo slide...",
  streaming_msg_starting_generation: "Bắt đầu tạo slide...",
  streaming_msg_no_slides: "Không có slide nào được tạo",
  streaming_msg_ready: "Hệ thống đã sẵn sàng",
  // ─────────── STRUCTURE EDITOR ───────────
  structure_title: "Trình soạn thảo cấu trúc",
  structure_intro_slide: "Slide giới thiệu",
  structure_add_section: "Thêm mục",
  structure_intro_label: "SLIDE GIỚI THIỆU",
  structure_title_ph: "Tiêu đề bài thuyết trình...",
  structure_section_title_ph: "Tiêu đề mục...",
  structure_content_ph: "Nội dung...",
  structure_transition: "Chuyển tiếp",
  structure_level: "Cấp độ",
  structure_approve: "Duyệt & Tạo slide",
  structure_processing: "Đang xử lý...",
  structure_preview: "Xem trước tài liệu",
  structure_source_text: "VĂN BẢN GỐC",
  structure_structure: "CẤU TRÚC",
  structure_sections: "mục",
  structure_toast_no_session: "Không có session ID",
  structure_toast_no_session_desc: "Vui lòng tải lên tài liệu trước",
  structure_toast_load_fail: "Không thể tải cấu trúc",
  structure_toast_approved: "Cấu trúc đã được duyệt!",
  structure_toast_slides_prepared: "slide đã được chuẩn bị",
  structure_toast_approval_fail: "Duyệt thất bại",
  structure_toast_fail_approve: "Không thể duyệt",
  // ─────────── VIEW PROJECT ───────────
  view_present: "Trình chiếu",
  view_slide_n: "Slide",
  view_edit: "Chỉnh sửa",
  view_no_content: "Không có nội dung",
  view_edit_slide_title: "Chỉnh sửa HTML slide",
  view_edit_slide_desc: "Chỉnh sửa nội dung HTML và xem trước thay đổi",
  view_cancel: "Hủy",
  view_save: "Lưu",
  view_delete_slide_title: "Xóa slide",
  view_delete_slide_desc: "Hành động này không thể hoàn tác. Bạn có chắc muốn xóa slide này không?",
  view_delete: "Xóa",
  view_toast_load_fail: "Không thể tải danh sách slide",
  view_toast_updated: "Đã cập nhật slide",
  view_toast_save_fail: "Lưu thất bại",
  view_toast_deleted: "Đã xóa slide",
  view_toast_delete_fail: "Xóa thất bại",
  // ─────────── NOT FOUND ───────────
  notfound_title: "Ối! Không tìm thấy trang",
  notfound_message: "Trang bạn đang tìm kiếm không tồn tại.",
  notfound_link: "Quay về trang chủ",
  // ─────────── EXPORT MODAL ───────────
  export_title: "Xuất Slides",
  export_subtitle: "slide · Chọn định dạng xuất:",
  export_pdf_title: "📄 Xuất PDF",
  export_pdf_desc: "Ghép tất cả slides thành một file PDF",
  export_images_title: "🖼️ Xuất hình ảnh",
  export_images_desc: "Chụp từng slide thành ảnh PNG, tải về dạng ZIP",
  export_cancel: "Hủy",
  export_success_title: "Xuất thành công!",
  export_download: "💾 Tải về",
  export_close: "Đóng",
  export_processing_title: "Đang xuất slides...",
  export_processing_sub: "Đang xử lý",
  export_error_title: "Xuất thất bại",
  export_retry: "Thử lại",
  // ─────────── TOOLBAR ───────────
  toolbar_back: "Quay lại",
  toolbar_back_desc: "Trở về trang danh sách dự án",
  toolbar_select: "Chọn",
  toolbar_select_button: "Chọn",
  toolbar_select_desc: "Chọn, di chuyển và thay đổi kích thước phần tử",
  toolbar_add_text: "Thêm văn bản",
  toolbar_add_text_button: "Văn bản",
  toolbar_add_text_desc: "Kéo vào canvas hoặc click để thêm hộp chữ",
  toolbar_export: "Xuất file",
  toolbar_export_button: "Xuất",
  toolbar_export_desc: "Xuất slide thành PDF hoặc hình ảnh",
  toolbar_present: "Trình chiếu",
  toolbar_present_button: "Trình chiếu",
  toolbar_present_desc: "Bắt đầu trình chiếu toàn màn hình từ slide đầu",
  toolbar_present_from_start: "Trình chiếu từ đầu",
  toolbar_present_from_current: "Trình chiếu từ slide hiện tại",
  toolbar_undo: "Hoàn tác",
  toolbar_undo_desc: "Quay lại thao tác vừa thực hiện",
  toolbar_redo: "Làm lại",
  toolbar_redo_desc: "Khôi phục thao tác đã hoàn tác",
  // ─────────── SLIDEGEN (additional) ───────────
  slidegen_read_guide: "Đọc hướng dẫn",
  // ─────────── SLIDE EDITOR ───────────
  editor_loading: "Đang tải dự án...",
  editor_loading_slide: "Đang tải slide...",
  editor_slide_n: "Slide",
  editor_new_slide: "Slide mới",
  editor_tab_slides: "Slide",
  editor_tab_templates: "Mẫu",
  editor_tab_elements: "Phần tử",
  editor_template_hint: "Click vào bố cục để thêm slide mới",
  editor_no_element: "Chưa chọn phần tử",
  editor_no_element_desc: "Click vào phần tử trên canvas để chỉnh sửa",
  editor_section_transform: "Vị trí & Kích thước",
  editor_section_typography: "Typography",
  editor_section_appearance: "Màu sắc & Viền",
  editor_section_effects: "Hiệu ứng",
  editor_section_layer: "Lớp",
  editor_padding: "Khoảng đệm",
  editor_send_backward: "Gửi xuống dưới",
  editor_send_backward_desc: "Các phần tử khác sẽ hiển thị trên phần này",
  editor_bring_forward: "Đưa lên trên",
  editor_bring_forward_desc: "Phần tử này sẽ hiển thị trên các phần tử khác",
  editor_duplicate: "Nhân đôi",
  editor_duplicate_desc: "Tạo bản sao của phần tử này",
  editor_delete: "Xóa",
  editor_delete_desc: "Xóa vĩnh viễn phần tử khỏi slide",
  editor_align_left: "Căn trái",
  editor_align_left_desc: "Căn chỉnh văn bản sang trái",
  editor_align_center: "Căn giữa",
  editor_align_center_desc: "Căn chỉnh văn bản vào giữa",
  editor_align_right: "Căn phải",
  editor_align_right_desc: "Căn chỉnh văn bản sang phải",
  editor_align_justify: "Căn đều",
  editor_align_justify_desc: "Căn đều văn bản hai bên",
  editor_fmt_bold: "Đậm",
  editor_fmt_bold_desc: "Làm chữ đậm",
  editor_fmt_italic: "Nghiêng",
  editor_fmt_italic_desc: "Làm chữ nghiêng",
  editor_fmt_underline: "Gạch chân",
  editor_fmt_underline_desc: "Gạch chân văn bản",
  editor_fmt_strikethrough: "Gạch ngang",
  editor_fmt_strikethrough_desc: "Gạch ngang văn bản",
  editor_fmt_clear: "Xóa định dạng",
  editor_fmt_clear_desc: "Xóa tất cả định dạng văn bản",
  editor_no_fill: "Không tô màu",
  editor_no_fill_desc: "Làm nền trong suốt",
  editor_type_text: "Văn bản",
  editor_type_image: "Hình ảnh",
  editor_type_shape: "Hình khối",
  editor_type_video: "Video",
  editor_tmpl_blank: "Trống",
  editor_tmpl_title: "Slide tiêu đề",
  editor_tmpl_content: "Tiêu đề & Nội dung",
  editor_tmpl_two_col: "Hai cột",
  editor_tmpl_img_text: "Hình ảnh + Văn bản",
  editor_tmpl_bullets: "Tiêu đề & Gạch đầu dòng",
  editor_cat_text: "Văn bản",
  editor_cat_shapes: "Hình khối",
  editor_cat_media: "Phương tiện",
  editor_el_title: "Tiêu đề",
  editor_el_subtitle: "Tiêu đề phụ",
  editor_el_body: "Nội dung",
  editor_el_label: "Nhãn",
  editor_el_rect: "Hình chữ nhật",
  editor_el_circle: "Hình tròn",
  editor_el_triangle: "Hình tam giác",
  editor_el_star: "Ngôi sao",
  editor_el_diamond: "Hình thoi",
  editor_el_line: "Đường thẳng",
  editor_el_image: "Hình ảnh",
  editor_el_video: "Video",
  // ─── properties panel ───
  editor_prop_x: "Vị trí X",
  editor_prop_y: "Vị trí Y",
  editor_prop_width: "Chiều rộng",
  editor_prop_height: "Chiều cao",
  editor_prop_rotation: "Góc xoay",
  editor_prop_font_size: "Cỡ chữ",
  editor_prop_line_height: "Chiều cao dòng",
  editor_prop_letter_spacing: "Khoảng cách chữ",
  editor_prop_text_color: "Màu chữ",
  editor_prop_border_width: "Độ dày viền",
  editor_prop_border_color: "Màu viền",
  editor_prop_border_radius: "Bo góc",
  editor_prop_border_radius_desc: "0px = góc nhọn • tăng để bo tròn",
  editor_prop_box_shadow: "Bóng đổ",
  editor_prop_opacity: "Độ mờ",
  editor_prop_opacity_desc: "0% = ẩn hoàn toàn • 100% = hiển thị đầy đủ",
  editor_prop_blur: "Làm mờ",
  editor_prop_blur_desc: "Làm mờ cạnh phần tử để tạo hiệu ứng mềm mại",
  editor_prop_brightness: "Độ sáng",
  editor_prop_brightness_desc: "100% = bình thường • >100% sáng hơn • <100% tối hơn",
  editor_prop_saturation: "Độ bão hoà",
  editor_prop_saturation_desc: "0% = xám • 100% = bình thường • >100% sống động hơn",
  // ─── presentation mode ───
  present_slide: "Slide",
  present_no_content: "Không có nội dung",
  register_placeholder_fullname: "Nguyễn Văn A",
  structure_untitled: "Không có tên",
  structure_intro_fallback: "Giới thiệu",
  structure_transition_label: "(Chuyển tiếp)",
  streaming_err_no_file: "Không có file hoặc session. Vui lòng tải lên file trước.",
  streaming_err_generic: "Đã xảy ra lỗi",
  editor_reset_zoom: "Đặt lại zoom",
  editor_add_slide_prefix: "Thêm slide",
  editor_add_el_prefix: "Thêm",
};

const en: Translations = {
  // ─────────── SETTINGS ───────────
  nav_settings: "Settings",
  nav_back: "Go Back",
  settings_title: "Your Settings",
  settings_subtitle: "Manage your personal information and customize your experience",
  tab_profile: "Profile",
  tab_account: "Account",
  tab_appearance: "Appearance",
  tab_security: "Security",
  profile_title: "Profile Information",
  profile_subtitle: "Update your display name, avatar and bio",
  profile_avatar: "Avatar (URL)",
  profile_avatar_hint: "Link to your profile picture",
  profile_fullname: "Full Name",
  profile_fullname_placeholder: "Enter your full name",
  profile_bio: "Bio",
  profile_bio_placeholder: "Write a short bio about yourself...",
  profile_save: "Save Changes",
  profile_saving: "Saving...",
  profile_saved: "Saved",
  account_title: "Account Information",
  account_subtitle: "Username and email cannot be changed",
  account_username: "Username",
  account_email: "Email",
  account_readonly_hint: "These fields are read-only and cannot be edited",
  appearance_title: "Appearance & Language",
  appearance_subtitle: "Customize theme, display language and notifications",
  appearance_theme: "Color Theme",
  appearance_theme_light: "Light",
  appearance_theme_dark: "Dark",
  appearance_auto_theme: "Auto switch by time",
  appearance_auto_theme_hint: "Automatically switch theme based on the hours you set",
  appearance_dark_from: "Switch to dark at",
  appearance_light_from: "Switch to light at",
  appearance_language: "Language",
  appearance_language_hint: "Choose the display language for the entire application",
  appearance_notifications: "Notifications",
  appearance_notifications_hint: "Receive notifications for updates and new events",
  appearance_save: "Save Settings",
  appearance_saving: "Saving...",
  appearance_unsaved_warning: "You have unsaved changes. If you leave now, changes from every settings tab will be lost.",
  security_title: "Change Password",
  security_subtitle: "Keep your account safe with a strong password",
  security_current_password: "Current Password",
  security_new_password: "New Password",
  security_confirm_password: "Confirm New Password",
  security_change: "Change Password",
  security_changing: "Processing...",
  security_hint_length: "Minimum 6 characters",
  security_hint_match: "Passwords do not match",
  toast_profile_success: "Profile updated successfully",
  toast_profile_error: "Failed to update profile",
  toast_settings_success: "Settings saved successfully",
  toast_settings_error: "Failed to save settings",
  toast_password_success: "Password changed successfully",
  toast_password_error: "Failed to change password",
  toast_password_mismatch: "Confirmation password does not match",
  toast_password_short: "New password must be at least 6 characters",
  // ─────────── SIDEBAR / APP LAYOUT ───────────
  sidebar_slidegen: "SlideGen",
  sidebar_projects: "Projects",
  sidebar_guide: "Guide",
  sidebar_collapse: "Collapse",
  sidebar_expand: "Expand sidebar",
  sidebar_logout: "Logout",
  nav_login: "Login",
  // ─────────── HOME ───────────
  home_nav_features: "Features",
  home_nav_testimonials: "Testimonials",
  home_nav_partners: "Partners",
  home_sign_in: "Sign In",
  home_go_app: "Go to App",
  home_get_started: "Get Started",
  home_hero_badge: "AI-Powered Presentation Generator",
  home_hero_h1: "Create Stunning Slides",
  home_hero_h1_span: "In Seconds",
  home_hero_sub: "Transform your documents and ideas into beautiful, professional presentations with the power of AI. No design skills required.",
  home_start_free: "Start Creating Free",
  home_watch_demo: "Watch Demo",
  home_scroll_hint: "Discover More",
  home_stat_presentations: "Presentations Created",
  home_stat_satisfaction: "Satisfaction Rate",
  home_stat_templates: "Templates Available",
  home_stat_ai: "AI Availability",
  home_features_badge: "Features",
  home_features_h2: "Everything You Need to",
  home_features_h2_span: "Create Perfect Slides",
  home_features_sub: "Powerful AI capabilities combined with intuitive design tools make SlideGen the ultimate presentation companion.",
  home_feat_fast_title: "Lightning Fast",
  home_feat_fast_desc: "Generate professional slides in seconds with our AI-powered engine",
  home_feat_design_title: "Beautiful Designs",
  home_feat_design_desc: "Stunning templates and themes crafted by professional designers",
  home_feat_save_title: "Save Hours",
  home_feat_save_desc: "What used to take hours now takes minutes. Focus on what matters",
  home_feat_multilang_title: "Multi-Language",
  home_feat_multilang_desc: "Create presentations in any language with intelligent text processing",
  home_how_badge: "How It Works",
  home_how_h2: "Three Simple Steps to",
  home_how_h2_span: "Amazing Presentations",
  home_step1_title: "Upload or Describe",
  home_step1_desc: "Upload a Word file, describe your idea, or import an existing project",
  home_step2_title: "AI Magic",
  home_step2_desc: "AI analyzes your content and creates a professional slide layout",
  home_step3_title: "Export & Present",
  home_step3_desc: "Download as PDF, images, or present directly in fullscreen",
  home_testimonial_badge: "Testimonials",
  home_testimonial_h2: "Loved by",
  home_testimonial_h2_span: "Thousands",
  home_partners_badge: "Partners & Sponsors",
  home_partners_h2: "Trusted by",
  home_partners_h2_span: "Industry Leaders",
  home_partner_cta: "Want to become a partner?",
  home_contact: "Contact us",
  home_cta_h2: "Ready to Create Amazing Presentations?",
  home_cta_sub: "Join thousands of users who are already creating stunning slides with SlideGen. Start for free today!",
  home_get_started_free: "Get Started Free",
  home_footer_privacy: "Privacy",
  home_footer_terms: "Terms",
  home_footer_contact: "Contact",
  home_footer_tagline: "Made with ❤️ by SlideGen Team",
  // ─────────── GUIDE ───────────
  guide_title: "SlideGen Guide",
  guide_contents: "Contents",
  guide_overview_title: "System Overview",
  guide_overview_content: "SlideGen is an AI-powered slide generation platform. Upload documents, describe ideas, or import existing projects — and let AI transform your content into beautiful presentations.\n\nThe platform supports multiple workflow modes, real-time streaming generation, a full WYSIWYG slide editor, and presentation mode.",
  guide_workflows_title: "Workflow Modes",
  guide_workflows_content: "**Auto with Heading**: Automatically detects headings in your document and uses them as slide breaks. Best for well-structured documents.\n\n**Auto without Heading**: AI analyzes your content and determines the optimal slide structure. Great for unstructured text.\n\n**Manual Structure**: Review and edit the document structure before generation. Full control over what goes on each slide.",
  guide_structure_title: "Structure Editor",
  guide_structure_content: "The Structure Editor lets you organize your content before slide generation:\n\n• Apply hierarchy levels (0-7) to control nesting\n• Set content types: Title (blue), Content (green), Bullet (orange)\n• Drag and reorder text blocks\n• Add intro and transition slides\n• Preview your structure in real-time\n• Approve when ready to generate",
  guide_editor_title: "Slide Editor",
  guide_editor_content: "The WYSIWYG Slide Editor provides full visual control:\n\n• Drag, resize, and rotate elements on the canvas\n• Add text, images, shapes, icons, and connectors\n• Grid snapping and alignment guides\n• Zoom and pan controls\n• Properties panel for precise positioning\n• Slides panel for managing slide order",
  guide_shortcuts_title: "Keyboard Shortcuts",
  guide_shortcuts_content: "**Editor:**\n• Ctrl+Z — Undo\n• Ctrl+Y — Redo\n• Delete — Remove selected element\n\n**Presentation:**\n• → / Space — Next slide\n• ← — Previous slide\n• Escape — Exit presentation\n• Click left side — Previous\n• Click right side — Next",
  guide_faq_title: "FAQ",
  guide_faq_content: "**Q: What file formats are supported?**\nA: DOCX for document upload. Export to PDF and images.\n\n**Q: Can I edit slides after generation?**\nA: Yes! The WYSIWYG editor gives you full control over every element.\n\n**Q: Is my data saved automatically?**\nA: Yes, the editor auto-saves your changes every few seconds.\n\n**Q: How does the AI generation work?**\nA: We use advanced AI models to analyze your content, structure it into slides, and generate professional designs.",
  // ─────────── LOGIN ───────────
  login_title: "Welcome Back",
  login_subtitle: "Sign in to your SlideGen account",
  login_email: "Email",
  login_password: "Password",
  login_placeholder_email: "you@example.com",
  login_placeholder_password: "••••••",
  login_remember: "Remember me",
  login_signing_in: "Signing in...",
  login_sign_in: "Sign In",
  login_no_account: "Don't have an account?",
  login_register: "Register",
  login_toast_success: "Welcome back!",
  login_toast_error: "Login failed",

  // ─────────── AUTH ERRORS ───────────
  error_auth_required: "Please login to use this feature",
  error_token_expired: "Session expired. Please login again.",
  error_auth_general: "Please login to use this feature",
  error_rate_limit_title: "Daily limit reached",
  error_rate_limit_desc: "You've used up your daily generation limit. Upgrade your plan to continue.",
  error_docx_too_long_title: "Document is too long",
  error_generate_title: "Generation Error",
  error_upload_title: "Upload Error",
  error_load_title: "Load Error",
  error_save_title: "Save Error",

  // ─────────── SUBSCRIPTION ───────────
  subscription_title: "Manage Subscription",
  subscription_subtitle: "View your plan information and upgrade your account",
  subscription_current_plan: "Current Plan",
  subscription_active: "Active",
  subscription_expired: "Expired",
  subscription_expires_at: "Expires",
  subscription_auto_renew: "Auto-renews on",
  subscription_ends_on: "Plan ends on",
  subscription_no_expiry: "No expiration",
  subscription_idea_generation: "Idea Generation",
  subscription_docx_upload: "File Upload",
  subscription_slide_limit: "Slide Limit",
  subscription_today: "today",
  subscription_slides: "slides",
  subscription_redeem_code: "Redeem Upgrade Code",
  subscription_enter_code: "Enter Upgrade Code",
  subscription_code_placeholder: "Enter code here...",
  subscription_use_code: "Use Code",
  subscription_processing: "Processing...",
  subscription_cancel: "Cancel",
  subscription_upgrade: "Upgrade",
  subscription_current_tier: "Current Plan",
  subscription_guide_title: "Upgrade Guide",
  subscription_guide_code_only: "Currently the system only supports upgrade via code.",
  subscription_guide_free_ultra: "To get a free Ultra code, use: SLIDEGENIUS",
  subscription_guide_payment_soon: "Online payment feature will be updated soon.",
  subscription_unlimited: "Unlimited",
  subscription_error_load_title: "Failed to load subscription",
  subscription_error_retry_later: "Please try again later",
  subscription_error_code_required: "Please enter a code",
  subscription_success_title: "Success!",
  subscription_success_desc: "Your plan has been upgraded successfully.",
  subscription_error_redeem_title: "Failed to redeem code",
  subscription_error_invalid_code: "Invalid or already used code",
  subscription_error_upgrade_title: "Feature unavailable",
  subscription_error_upgrade_desc: "Currently only supports upgrade via code. Please contact support for a code.",
  subscription_error_load_info: "Unable to load subscription info",
  subscription_retry: "Retry",
  subscription_enter_code_desc: "Enter code to upgrade to a higher plan",
  subscription_code_label: "Upgrade Code",
  subscription_content_length: "Content Length",
  subscription_priority_support: "Priority Support",
  subscription_advanced_features: "Advanced Features",
  nav_subscription: "Subscription",
  plan_requires_plus: "Requires Plus plan or higher",
  plan_requires_ultra: "Requires Ultra plan",
  plan_slide_limit_title: "Slide limit reached",
  plan_slide_limit_desc: "Upgrade to Plus or Ultra to add more slides",
  export_pdf_failed: "PDF export failed",
  export_pdf_error: "Error exporting PDF",
  export_no_slides: "No slides to capture",
  export_capture_failed: "Capture failed",
  export_capture_error: "Error capturing slides",
  subscription_cancel_renewal: "Cancel Renewal",
  subscription_cancel_now: "Cancel Now",
  subscription_cancel_renewal_title: "Cancel Renewal?",
  subscription_cancel_renewal_desc: "Your plan will stay active until the end of the current period, then automatically revert to the Free plan.",
  subscription_cancel_now_title: "Cancel Now?",
  subscription_cancel_now_desc: "Your subscription will be cancelled immediately and downgraded to the Free plan. This action cannot be undone.",
  subscription_cancel_confirm: "Confirm Cancel",
  subscription_cancelled_now: "Subscription cancelled. Your account has been downgraded to the Free plan.",
  subscription_cancelled_renewal: "Your plan will expire at the end of the current period and will not be renewed.",
  // ─────────── REGISTER ───────────
  register_title: "Create Account",
  register_subtitle: "Join SlideGen and start creating",
  register_fullname: "Full Name",
  register_email: "Email",
  register_password: "Password",
  register_confirm_password: "Confirm Password",
  register_error_fullname: "Min 3 characters",
  register_error_password: "Min 6 characters",
  register_error_confirm: "Passwords don't match",
  register_creating: "Creating...",
  register_create: "Create Account",
  register_has_account: "Already have an account?",
  register_sign_in: "Sign in",
  register_toast_success: "Account created!",
  register_toast_error: "Registration failed",
  // ─────────── PROJECTS ───────────
  projects_title: "Projects",
  projects_search: "Search projects...",
  projects_select_mode: "Select mode",
  projects_deselect_all: "Deselect All",
  projects_select_all: "Select All",
  projects_cancel: "Cancel",
  projects_no_found: "No projects found",
  projects_no_found_hint: "Create a new project from the SlideGen page",
  projects_go_home: "Go Home",
  projects_edit: "Edit",
  projects_view: "View",
  projects_rename: "Rename",
  projects_delete: "Delete",
  projects_slides: "slides",
  projects_delete_title: "Delete Project",
  projects_delete_desc: "This action cannot be undone. Are you sure?",
  projects_rename_title: "Rename Project",
  projects_rename_desc: "Enter a new name for your project",
  projects_name_placeholder: "Project name",
  projects_save: "Save",
  projects_delete_all: "Delete All",
  projects_toast_load_fail: "Failed to load projects",
  projects_toast_deleted: "Project deleted",
  projects_toast_delete_fail: "Delete failed",
  projects_toast_renamed: "Project renamed",
  projects_toast_rename_fail: "Rename failed",
  // ─────────── SLIDEGEN ───────────
  slidegen_badge: "AI-Powered Slide Generation",
  slidegen_h1: "Create Stunning Slides",
  slidegen_h1_span: "In Seconds",
  slidegen_sub: "Upload your documents, describe your ideas, or import existing projects. SlideGen transforms your content into beautiful presentations with AI.",
  slidegen_upload_title: "Create from Document",
  slidegen_upload_desc: "Upload your document and let AI generate professional slides automatically",
  slidegen_uploading: "Uploading...",
  slidegen_choose_file: "Upload file",

  slidegen_idea_title: "Create from Idea",

  slidegen_idea_desc: "Describe your presentation and let AI build it",
  slidegen_idea_title_ph: "Presentation title",
  slidegen_idea_desc_ph: "Describe your presentation...",
  slidegen_generate: "Generate",
  slidegen_options: "Generation Options",
  slidegen_workflow: "Workflow Mode",
  slidegen_workflow_auto_heading: "Auto with Heading",
  slidegen_workflow_auto_heading_desc: "Automatically detect headings for slide breaks",
  slidegen_workflow_auto_no_heading: "Auto without Heading",
  slidegen_workflow_auto_no_heading_desc: "AI determines optimal slide structure",
  slidegen_workflow_manual: "Manual Structure",
  slidegen_workflow_manual_desc: "Edit document structure before generating",
  slidegen_transitions: "Enable Transition Slides",
  slidegen_thankyou: "Enable Thank You Slide",
  slidegen_length_label: "Slide count",
  slidegen_length_brief: "Brief",
  slidegen_length_standard: "Standard",
  slidegen_length_detailed: "Detailed",
  slidegen_length_extensive: "Extensive",
  slidegen_toast_success: "Upload successful",
  slidegen_toast_opening_structure: "Opening structure editor...",
  slidegen_toast_starting: "Starting slide generation...",
  slidegen_toast_upload_fail: "Upload failed",
  slidegen_toast_no_title: "Please enter a title",

  // ─────────── STREAMING ───────────
  streaming_title: "SlideGen AI",
  streaming_completed: "🎉 Completed!",
  streaming_preparing: "💡 Preparing your idea...",
  streaming_creating: "Creating your presentation...",
  streaming_stage_analyze: "Analyze Content",
  streaming_stage_prepare: "Prepare Content",
  streaming_stage_design: "Design Slides",
  streaming_stage_completed_label: "Completed",
  streaming_stage_processing: "Processing...",
  streaming_stage_pending: "Pending",
  streaming_done: "Completed!",
  streaming_slides_created: "Successfully created",
  streaming_slides_unit: "slides",
  streaming_retry: "Retry",
  streaming_slides_header: "Slides",
  streaming_slide_n: "Slide",
  streaming_slide_completed: "Completed",
  streaming_go_editor: "Go to Editor",
  streaming_present: "Present",
  streaming_back: "Back to SlideGen",
  streaming_no_content: "No content",
  streaming_initializing: "Initializing...",
  streaming_connecting: "Connecting...",
  streaming_preparing_activity: "Preparing your idea...",
  streaming_toast_ready: "Structure ready",
  streaming_toast_starting: "Starting slide generation...",
  streaming_toast_failed: "Failed to prepare",
  streaming_msg_analyzing: "Analyzing content to design slides...",
  streaming_msg_processing_struct: "Processing document structure...",
  streaming_msg_generating_struct: "Generating document structure from content...",
  streaming_msg_booting: "Booting system...",
  streaming_msg_initializing_infra: "Initializing infrastructure...",
  streaming_msg_generating_slides: "Generating slides...",
  streaming_msg_starting_generation: "Starting slide generation...",
  streaming_msg_no_slides: "No slides were created",
  streaming_msg_ready: "System ready",
  // ─────────── STRUCTURE EDITOR ───────────
  structure_title: "Structure Editor",
  structure_intro_slide: "Intro Slide",
  structure_add_section: "Add Section",
  structure_intro_label: "INTRO SLIDE",
  structure_title_ph: "Presentation title...",
  structure_section_title_ph: "Section title...",
  structure_content_ph: "Content text...",
  structure_transition: "Transition",
  structure_level: "Level",
  structure_approve: "Approve & Generate",
  structure_processing: "Processing...",
  structure_preview: "Document Preview",
  structure_source_text: "SOURCE TEXT",
  structure_structure: "STRUCTURE",
  structure_sections: "sections",
  structure_toast_no_session: "No session ID",
  structure_toast_no_session_desc: "Please upload a document first",
  structure_toast_load_fail: "Failed to load structure",
  structure_toast_approved: "Structure approved!",
  structure_toast_slides_prepared: "slides prepared",
  structure_toast_approval_fail: "Approval failed",
  structure_toast_fail_approve: "Failed to approve",
  // ─────────── VIEW PROJECT ───────────
  view_present: "Present",
  view_slide_n: "Slide",
  view_edit: "Edit",
  view_no_content: "No content",
  view_edit_slide_title: "Edit Slide HTML",
  view_edit_slide_desc: "Edit the HTML content and preview your changes",
  view_cancel: "Cancel",
  view_save: "Save",
  view_delete_slide_title: "Delete Slide",
  view_delete_slide_desc: "This action cannot be undone. Are you sure you want to delete this slide?",
  view_delete: "Delete",
  view_toast_load_fail: "Failed to load slides",
  view_toast_updated: "Slide updated",
  view_toast_save_fail: "Save failed",
  view_toast_deleted: "Slide deleted",
  view_toast_delete_fail: "Delete failed",
  // ─────────── NOT FOUND ───────────
  notfound_title: "Oops! Page not found",
  notfound_message: "The page you are looking for does not exist.",
  notfound_link: "Return to Home",
  // ─────────── EXPORT MODAL ───────────
  export_title: "Export Slides",
  export_subtitle: "slides · Choose export format:",
  export_pdf_title: "📄 Export PDF",
  export_pdf_desc: "Merge all slides into a single PDF file",
  export_images_title: "🖼️ Export Images",
  export_images_desc: "Capture each slide as PNG image, download as ZIP",
  export_cancel: "Cancel",
  export_success_title: "Export Successful!",
  export_download: "💾 Download",
  export_close: "Close",
  export_processing_title: "Exporting slides...",
  export_processing_sub: "Processing",
  export_error_title: "Export Failed",
  export_retry: "Retry",
  // ─────────── TOOLBAR ───────────
  toolbar_back: "Go Back",
  toolbar_back_desc: "Return to the projects list",
  toolbar_select: "Select",
  toolbar_select_button: "Select",
  toolbar_select_desc: "Select, move and resize elements",
  toolbar_add_text: "Add Text",
  toolbar_add_text_button: "Text",
  toolbar_add_text_desc: "Drag to canvas or click to add a text box",
  toolbar_export: "Export",
  toolbar_export_button: "Export",
  toolbar_export_desc: "Export slides to PDF or images",
  toolbar_present: "Present",
  toolbar_present_button: "Present",
  toolbar_present_desc: "Start fullscreen presentation from the first slide",
  toolbar_present_from_start: "Present from start",
  toolbar_present_from_current: "Present from current slide",
  toolbar_undo: "Undo",
  toolbar_undo_desc: "Undo the last action",
  toolbar_redo: "Redo",
  toolbar_redo_desc: "Redo the undone action",
  // ─────────── SLIDEGEN (additional) ───────────
  slidegen_read_guide: "Read the Guide",
  // ─────────── SLIDE EDITOR ───────────
  editor_loading: "Loading project...",
  editor_loading_slide: "Loading slide...",
  editor_slide_n: "Slide",
  editor_new_slide: "New Slide",
  editor_tab_slides: "Slides",
  editor_tab_templates: "Templates",
  editor_tab_elements: "Elements",
  editor_template_hint: "Click a layout to add a new slide",
  editor_no_element: "No element selected",
  editor_no_element_desc: "Click on an element in the canvas to edit it",
  editor_section_transform: "Transform",
  editor_section_typography: "Typography",
  editor_section_appearance: "Appearance",
  editor_section_effects: "Effects",
  editor_section_layer: "Layer",
  editor_padding: "Padding",
  editor_send_backward: "Send Backward",
  editor_send_backward_desc: "Other elements will appear on top of this one",
  editor_bring_forward: "Bring Forward",
  editor_bring_forward_desc: "This element will appear on top of others",
  editor_duplicate: "Duplicate",
  editor_duplicate_desc: "Create a copy of this element",
  editor_delete: "Delete",
  editor_delete_desc: "Permanently remove this element from the slide",
  editor_align_left: "Align Left",
  editor_align_left_desc: "Align text to the left",
  editor_align_center: "Align Center",
  editor_align_center_desc: "Center the text",
  editor_align_right: "Align Right",
  editor_align_right_desc: "Align text to the right",
  editor_align_justify: "Justify",
  editor_align_justify_desc: "Justify text on both sides",
  editor_fmt_bold: "Bold",
  editor_fmt_bold_desc: "Make selected text bold",
  editor_fmt_italic: "Italic",
  editor_fmt_italic_desc: "Make selected text italic",
  editor_fmt_underline: "Underline",
  editor_fmt_underline_desc: "Underline selected text",
  editor_fmt_strikethrough: "Strikethrough",
  editor_fmt_strikethrough_desc: "Strike through the text",
  editor_fmt_clear: "Clear Format",
  editor_fmt_clear_desc: "Remove all text formatting",
  editor_no_fill: "No Fill",
  editor_no_fill_desc: "Make background transparent",
  editor_type_text: "Text",
  editor_type_image: "Image",
  editor_type_shape: "Shape",
  editor_type_video: "Video",
  editor_tmpl_blank: "Blank",
  editor_tmpl_title: "Title Slide",
  editor_tmpl_content: "Title & Content",
  editor_tmpl_two_col: "Two Columns",
  editor_tmpl_img_text: "Image + Text",
  editor_tmpl_bullets: "Title & Bullets",
  editor_cat_text: "Text",
  editor_cat_shapes: "Shapes",
  editor_cat_media: "Media",
  editor_el_title: "Title",
  editor_el_subtitle: "Subtitle",
  editor_el_body: "Body",
  editor_el_label: "Label",
  editor_el_rect: "Rectangle",
  editor_el_circle: "Circle",
  editor_el_triangle: "Triangle",
  editor_el_star: "Star",
  editor_el_diamond: "Diamond",
  editor_el_line: "Line",
  editor_el_image: "Image",
  editor_el_video: "Video",
  // ─── properties panel ───
  editor_prop_x: "X Position",
  editor_prop_y: "Y Position",
  editor_prop_width: "Width",
  editor_prop_height: "Height",
  editor_prop_rotation: "Rotation",
  editor_prop_font_size: "Font size",
  editor_prop_line_height: "Line height",
  editor_prop_letter_spacing: "Letter spacing",
  editor_prop_text_color: "Text color",
  editor_prop_border_width: "Border width",
  editor_prop_border_color: "Border color",
  editor_prop_border_radius: "Border radius",
  editor_prop_border_radius_desc: "0px = sharp corners • increase to round",
  editor_prop_box_shadow: "Box shadow",
  editor_prop_opacity: "Opacity",
  editor_prop_opacity_desc: "0% = fully hidden • 100% = fully visible",
  editor_prop_blur: "Blur",
  editor_prop_blur_desc: "Blur the element edges for a soft effect",
  editor_prop_brightness: "Brightness",
  editor_prop_brightness_desc: "100% = normal • >100% brighter • <100% darker",
  editor_prop_saturation: "Saturation",
  editor_prop_saturation_desc: "0% = grayscale • 100% = normal • >100% more vivid",
  // ─── presentation mode ───
  present_slide: "Slide",
  present_no_content: "No content",
  register_placeholder_fullname: "John Doe",
  structure_untitled: "Untitled",
  structure_intro_fallback: "Intro",
  structure_transition_label: "(Transition)",
  streaming_err_no_file: "No file or session specified for streaming. Please upload a file first.",
  streaming_err_generic: "An error occurred",
  editor_reset_zoom: "Reset zoom",
  editor_add_slide_prefix: "Add slide",
  editor_add_el_prefix: "Add",
};

const dictionaries: Record<Language, Translations> = { vi, en };

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextType | null>(null);

export const useLanguage = () => {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    return (localStorage.getItem("language") as Language) || "vi";
  });

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem("language", lang);
  }, []);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t: dictionaries[language] }}>
      {children}
    </LanguageContext.Provider>
  );
};
